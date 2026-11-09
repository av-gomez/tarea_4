"""Acceso uniforme a cualquier módulo y año de la ENAHO (INEI), usado por todas las Skills.

    from comun import enaho
    enaho.descargar(2025, "05")                      # baja datos/1031-Modulo05.zip si falta
    df, nivel = enaho.leer(2023, "03")               # llaves como texto, columnas en minúscula, 'anio'
    dicc = enaho.diccionario(2024, "05")             # variable, etiqueta, valores codificados
    base = enaho.unir(base_personas, df, nivel)      # unión validada (m:1 o 1:1) sin duplicar filas

Reglas comunes a todos los módulos:
- Lectura con convert_categoricals=False; llaves (conglome, vivienda, hogar, codperso, ubigeo) como texto.
- El nivel del módulo se detecta por la unicidad de sus llaves: 'persona' (conglome, vivienda, hogar,
  codperso), 'hogar' (conglome, vivienda, hogar) o 'detalle' (varias filas por hogar o persona, p. ej.
  gastos por producto o programas sociales), que debe agregarse antes de unir.
- Las uniones usan validate="m:1" (o "1:1") y verifican que no se pierdan ni dupliquen filas.
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
DATOS = RAIZ / "datos"
URL = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"

# Código del INEI de la ENAHO anual (metodología actualizada); verificado con el nombre de los .dta.
CODIGOS = {2019: 687, 2020: 737, 2021: 759, 2022: 784, 2023: 906, 2024: 966, 2025: 1031}

# Módulos de la ENAHO anual publicados en el portal de microdatos (verificados para 2025).
MODULOS = {
    "01": "Características de la vivienda y del hogar",
    "02": "Características de los miembros del hogar",
    "03": "Educación",
    "04": "Salud",
    "05": "Empleo e ingresos",
    "07": "Gastos en alimentos y bebidas",
    "08": "Instituciones beneficas",
    "09": "Mantenimiento de la vivienda",
    "10": "Transportes y comunicaciones",
    "11": "Servicios a la vivienda",
    "12": "Esparcimiento, diversión y servicios de cultura",
    "13": "Vestido y calzado",
    "15": "Gastos de transferencias",
    "16": "Muebles y enseres",
    "17": "Otros bienes y servicios",
    "18": "Equipamiento del hogar",
    "22": "Producción agrícola",
    "23": "Subproductos agrícolas",
    "24": "Producción forestal",
    "25": "Gastos en actividades agrícolas o forestales",
    "26": "Producción pecuaria",
    "27": "Subproductos pecuarios",
    "28": "Gastos en actividades pecuarias",
    "34": "Sumarias (variables calculadas)",
    "37": "Programas sociales (miembros del hogar)",
    "77": "Ingresos del trabajador independiente",
    "78": "Bienes y servicios de cuidados personales",
    "84": "Participación ciudadana",
    "85": "Gobernabilidad, democracia y transparencia",
}
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = [*LLAVES_HOGAR, "codperso"]
TEXTO = [*LLAVES_PERSONA, "ubigeo"]


def _mod(modulo) -> str:
    return f"{int(modulo):02d}"


def _sin_tildes(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def codigo(anio: int) -> int:
    if anio not in CODIGOS:
        raise ValueError(f"Año {anio} no registrado. Años disponibles: {sorted(CODIGOS)}")
    return CODIGOS[anio]


def ruta_zip(anio: int, modulo) -> Path:
    return DATOS / f"{codigo(anio)}-Modulo{_mod(modulo)}.zip"


def descargar(anio: int, modulo, forzar: bool = False) -> Path:
    """Descarga el zip oficial del INEI a datos/ (si no existe) y lo devuelve."""
    import httpx

    destino = ruta_zip(anio, modulo)
    if destino.exists() and destino.stat().st_size > 10_000 and not forzar:
        return destino
    DATOS.mkdir(exist_ok=True)
    url = URL.format(codigo=codigo(anio), modulo=_mod(modulo))
    with httpx.stream("GET", url, timeout=600, follow_redirects=True) as r:
        r.raise_for_status()
        with open(destino, "wb") as f:
            for parte in r.iter_bytes():
                f.write(parte)
    if not zipfile.is_zipfile(destino):
        destino.unlink()
        raise RuntimeError(f"El INEI no devolvió un zip válido para {url}")
    return destino


def _dta_principal(z: zipfile.ZipFile, modulo: str) -> str:
    dtas = [n for n in z.namelist() if n.lower().endswith(".dta")]
    if not dtas:
        raise FileNotFoundError("El zip no contiene archivos .dta")
    if modulo == "34":
        dtas = [n for n in dtas if "sumaria" in n.lower() and "12g" not in n.lower()] or dtas
    # Se descartan tablas auxiliares (p. ej. códigos CIUO/CNO del módulo 02)
    principales = [n for n in dtas if "tabla" not in n.lower()] or dtas
    return max(principales, key=lambda n: z.getinfo(n).file_size)


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    nuevas = {}
    for c in df.columns:
        crudo = str(c).strip().lower()
        nuevas[c] = "anio" if re.fullmatch(r"a.{1,2}o", crudo) else _sin_tildes(crudo)
    return df.rename(columns=nuevas)


def nivel(df: pd.DataFrame) -> str:
    if set(LLAVES_PERSONA) <= set(df.columns) and not df.duplicated(LLAVES_PERSONA).any():
        return "persona"
    if set(LLAVES_HOGAR) <= set(df.columns) and not df.duplicated(LLAVES_HOGAR).any():
        return "hogar"
    return "detalle"


def leer(anio: int, modulo, columnas: list[str] | None = None, descargar_si_falta: bool = True):
    """Lee el .dta principal del módulo. Devuelve (DataFrame, nivel, nombre del archivo)."""
    modulo = _mod(modulo)
    z_path = ruta_zip(anio, modulo)
    if not z_path.exists():
        if not descargar_si_falta:
            raise FileNotFoundError(z_path)
        descargar(anio, modulo)
    with zipfile.ZipFile(z_path) as z:
        nombre = _dta_principal(z, modulo)
        datos = z.read(nombre)
    df = pd.read_stata(io.BytesIO(datos), convert_categoricals=False)
    df = normalizar_columnas(df)
    for c in TEXTO:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    if columnas:
        faltan = [c for c in columnas if c not in df.columns]
        if faltan:
            raise KeyError(f"Variables inexistentes en el módulo {modulo} de {anio}: {faltan}")
        llaves = [c for c in LLAVES_PERSONA if c in df.columns]
        df = df[list(dict.fromkeys([*llaves, *columnas]))]
    df["anio"] = anio
    return df, nivel(df), nombre


def diccionario(anio: int, modulo) -> pd.DataFrame:
    """Variables del módulo con su etiqueta y sus valores codificados (del propio archivo Stata)."""
    modulo = _mod(modulo)
    z_path = ruta_zip(anio, modulo)
    if not z_path.exists():
        descargar(anio, modulo)
    with zipfile.ZipFile(z_path) as z:
        nombre = _dta_principal(z, modulo)
        lector = pd.io.stata.StataReader(io.BytesIO(z.read(nombre)))
        etiquetas = lector.variable_labels()
        try:
            valores = lector.value_labels()
            lbl_por_var = dict(zip(etiquetas, lector._lbllist)) if hasattr(lector, "_lbllist") else {}
        except Exception:  # algunos archivos no traen etiquetas de valor legibles
            valores, lbl_por_var = {}, {}
    filas = []
    for var, etq in etiquetas.items():
        lbl = lbl_por_var.get(var, "")
        codigos = valores.get(lbl, {}) if lbl else {}
        filas.append({"anio": anio, "modulo": modulo, "variable": _sin_tildes(var.lower()) if not
                      re.fullmatch(r"a.{1,2}o", var.lower()) else "anio", "etiqueta": etq,
                      "valores": "; ".join(f"{int(k) if float(k).is_integer() else k}={v}"
                                           for k, v in list(codigos.items())[:40])})
    return pd.DataFrame(filas)


def unir(base: pd.DataFrame, modulo_df: pd.DataFrame, nivel_modulo: str, sufijo: str = "") -> pd.DataFrame:
    """Une un módulo a una base de personas u hogares sin duplicar filas (validate m:1 o 1:1)."""
    if nivel_modulo == "detalle":
        raise ValueError("El módulo tiene varias filas por hogar/persona: agrégalo antes de unir "
                         "(p. ej. groupby(llaves).agg(...)).")
    base_nivel = "persona" if "codperso" in base.columns else "hogar"
    llaves = LLAVES_PERSONA if nivel_modulo == "persona" else LLAVES_HOGAR
    if base_nivel == "hogar" and nivel_modulo == "persona":
        raise ValueError("No se puede unir un módulo de personas a una base de hogares sin agregarlo.")
    validar = "1:1" if base_nivel == nivel_modulo else "m:1"
    comunes = [c for c in modulo_df.columns if c in base.columns and c not in llaves]
    m = modulo_df.drop(columns=comunes)
    if sufijo:
        m = m.rename(columns={c: f"{c}{sufijo}" for c in m.columns if c not in llaves})
    n = len(base)
    out = base.merge(m, on=llaves, how="left", validate=validar)
    if len(out) != n:
        raise AssertionError(f"La unión cambió el número de filas: {n} -> {len(out)}")
    return out
