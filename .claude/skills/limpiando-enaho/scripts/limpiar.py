"""Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO (2019-2025) y valida contra el INEI.

    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py                       # 2024 (código INEI 966)
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2025           # cualquier año 2019-2025
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anios 2019 2020 2021 2022 2023 2024 2025
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2025 --modulos 03 04 05 01
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --forzar              # rehace aunque exista

--modulos agrega a la base las variables de otros módulos (cualquiera de los 29 de la ENAHO): los de nivel
persona (03 educación, 04 salud, 05 empleo, 85 gobernabilidad...) se unen por conglome, vivienda, hogar y
codperso; los de nivel hogar (01 vivienda...) por conglome, vivienda y hogar. Los módulos de detalle (07
gastos, 37 programas...) tienen varias filas por unidad y deben agregarse antes (skill explorando-enaho).
Los microdatos que falten se descargan solos del portal del INEI.

Pipeline (siempre en este orden; ver reference.md):
  1. Leer los .dta dentro de los zip con convert_categoricals=False y llaves como texto (sin perder ceros).
  2. Normalizar nombres de columnas (minúsculas, "aÑo" -> "anio").
  3. Filtrar residentes habituales: ((p204==1)&(p205==2)) | ((p204==2)&(p206==1)).
  4. Unir personas (m) con hogares (1) por conglome, vivienda, hogar con validate="m:1".
  5. Construir departamento = ubigeo[:2], área (estrato<=5 urbano), pobre = pobreza<=2, etc.
  6. Estimar indicadores ponderados (facpob07) con error de muestreo -> salidas/indicadores.csv.
  7. Validar contra cifras oficiales -> salidas/validacion.txt. Si una validación esencial falla, sale con
     código 1 y NO guarda la base: nunca se ajustan resultados para que coincidan.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def _raiz() -> Path:
    p = Path(__file__).resolve()
    for d in p.parents:
        if (d / "pyproject.toml").exists():
            return d
    return Path.cwd()


RAIZ = _raiz()
sys.path.insert(0, str(RAIZ))
from comun import enaho  # noqa: E402
from comun.estimacion import por_grupo, proporcion  # noqa: E402

CODIGOS_INEI = enaho.CODIGOS
LLAVES = ["conglome", "vivienda", "hogar"]
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios",
    "18": "Moquegua", "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna",
    "24": "Tumbes", "25": "Ucayali",
}
DOMINIOS = {1: "Costa Norte", 2: "Costa Centro", 3: "Costa Sur", 4: "Sierra Norte", 5: "Sierra Centro",
            6: "Sierra Sur", 7: "Selva", 8: "Lima Metropolitana"}
REGION_NATURAL = {1: "Costa", 2: "Costa", 3: "Costa", 8: "Costa", 4: "Sierra", 5: "Sierra", 6: "Sierra",
                  7: "Selva"}
# Cifras oficiales publicadas por el INEI (informes técnicos de pobreza monetaria; 2025: INEI, 5 may. 2026).
# Los conteos de filas solo se conocen para 2024 (sesión 16 del curso); en otros años se informan sin validar.
OFICIALES = {
    2019: {"pobreza_nacional": 20.2, "urbana": 14.6, "rural": 40.8, "extrema": 2.9},
    2020: {"pobreza_nacional": 30.1, "urbana": 26.0, "rural": 45.7, "extrema": 5.1},
    2021: {"pobreza_nacional": 25.9, "urbana": 22.3, "rural": 39.7, "extrema": 4.1},
    2022: {"pobreza_nacional": 27.5, "urbana": 24.1, "rural": 41.1, "extrema": 5.0},
    2023: {"pobreza_nacional": 29.0, "urbana": 26.4, "rural": 39.8, "extrema": 5.7},
    2024: {"pobreza_nacional": 27.6, "urbana": 24.8, "rural": 39.3, "extrema": 5.5, "residentes": 108_664,
           "filas_modulo02": 117_721, "hogares": 33_691},
    2025: {"pobreza_nacional": 25.7, "urbana": 23.4, "rural": 35.5, "extrema": 4.7},
}
REFERENCIA = OFICIALES[2024]
TOL_NACIONAL = 0.1     # puntos porcentuales (exigencia de la tarea)
TOL_AREA = 0.15        # redondeo a un decimal de la cifra publicada


def _sin_tildes(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Minúsculas, sin tildes; la columna del año (aÑo, a\xf1o) pasa a 'anio'."""
    nuevas = {}
    for c in df.columns:
        crudo = str(c).strip().lower()
        # "aÑo" puede llegar como 'año', 'a�o' o 'a\xd1o' según la codificación del .dta
        nuevas[c] = "anio" if re.fullmatch(r"a.{1,2}o", crudo) else _sin_tildes(crudo)
    return df.rename(columns=nuevas)


def leer_dta(zip_path: Path, patron: str, columnas_texto=LLAVES) -> pd.DataFrame:
    """Lee el .dta del zip sin convertir categorías y con las llaves como texto."""
    with zipfile.ZipFile(zip_path) as z:
        nombres = [n for n in z.namelist() if n.lower().endswith(".dta") and patron in n.lower()]
        if not nombres:
            raise FileNotFoundError(f"No hay un .dta con '{patron}' dentro de {zip_path}")
        nombre = sorted(nombres, key=len)[0]          # sumaria-2024.dta antes que sumaria-2024-12g.dta
        df = pd.read_stata(io.BytesIO(z.read(nombre)), convert_categoricals=False)
    df = normalizar_columnas(df)
    for c in [*columnas_texto, "codperso", "ubigeo"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df, nombre


def construir(anio: int, datos: Path, modulos: list[str] | None = None) -> tuple[pd.DataFrame, list, dict]:
    REFERENCIA = OFICIALES[anio]
    chequeos: list[tuple[str, bool, str, bool]] = []   # (nombre, ok, detalle, esencial)

    def chequear(nombre, ok, detalle, esencial=True):
        chequeos.append((nombre, bool(ok), detalle, esencial))

    hog, _, n34 = enaho.leer(anio, "34")
    per, _, n02 = enaho.leer(anio, "02")
    hog, per = hog.drop(columns="anio"), per.drop(columns="anio")
    meta = {"archivo_sumaria": n34, "archivo_miembros": n02}

    # Llaves con ceros iniciales intactos
    chequear("Llaves como texto con longitud fija (conglome 6, vivienda 3, hogar 2)",
             (hog.conglome.str.len().eq(6).all() and hog.vivienda.str.len().eq(3).all()
              and hog.hogar.str.len().eq(2).all()),
             f"conglome ej. {hog.conglome.iloc[0]!r}, ubigeo ej. {hog.ubigeo.iloc[0]!r}")
    if "hogares" in REFERENCIA:
        chequear("Hogares en la sumaria", len(hog) == REFERENCIA["hogares"],
                 f"{len(hog):,} (referencia {REFERENCIA['hogares']:,})")
    else:
        chequear("Hogares en la sumaria (sin conteo de referencia para este año)", len(hog) > 20_000,
                 f"{len(hog):,}", esencial=False)
    chequear("Llaves de hogar únicas en la sumaria", not hog.duplicated(LLAVES).any(),
             f"{hog.duplicated(LLAVES).sum()} duplicados")
    if "filas_modulo02" in REFERENCIA:
        chequear("Filas del módulo 02", len(per) == REFERENCIA["filas_modulo02"],
                 f"{len(per):,} (referencia {REFERENCIA['filas_modulo02']:,})", esencial=False)
    chequear("Llaves de persona únicas en el módulo 02", not per.duplicated([*LLAVES, "codperso"]).any(),
             f"{per.duplicated([*LLAVES, 'codperso']).sum()} duplicados")

    # Residentes habituales
    res = ((per.p204 == 1) & (per.p205 == 2)) | ((per.p204 == 2) & (per.p206 == 1))
    per = per.loc[res].copy()
    if "residentes" in REFERENCIA:
        chequear("Residentes habituales", len(per) == REFERENCIA["residentes"],
                 f"{len(per):,} (referencia {REFERENCIA['residentes']:,})")
    else:
        chequear("Residentes habituales (sin conteo de referencia para este año)", len(per) > 50_000,
                 f"{len(per):,}", esencial=False)

    # Unión m:1 personas-hogares
    cols_hog = [c for c in ["conglome", "vivienda", "hogar", "pobreza", "factor07", "mieperho", "linea", "linpe",
                            "gashog2d", "inghog1d", "inghog2d", "estrato", "dominio", "ubigeo"] if c in hog.columns]
    n_antes = len(per)
    base = per.drop(columns=["ubigeo", "dominio", "estrato"], errors="ignore").merge(
        hog[cols_hog], on=LLAVES, how="left", validate="m:1", indicator=True)
    sin_hogar = int((base._merge != "both").sum())
    chequear("Unión m:1 sin duplicar ni perder personas", len(base) == n_antes and sin_hogar == 0,
             f"{n_antes:,} personas antes y {len(base):,} después; {sin_hogar} sin hogar en la sumaria")
    base = base.drop(columns="_merge")

    # Variables analíticas
    base["departamento"] = base.ubigeo.str[:2]
    base["nombre_departamento"] = base.departamento.map(DEPARTAMENTOS)
    base["urbano"] = (base.estrato <= 5).astype(int)
    base["area"] = np.where(base.urbano == 1, "Urbana", "Rural")
    base["pobre"] = (base.pobreza <= 2).astype(int)
    base["pobre_extremo"] = (base.pobreza == 1).astype(int)
    base["dominio_nombre"] = base.dominio.map(DOMINIOS)
    base["region_natural"] = base.dominio.map(REGION_NATURAL)
    base["sexo"] = base.p207.map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base.p208a
    base["grupo_edad"] = pd.cut(base.edad, [-1, 13, 17, 29, 44, 59, 200],
                                labels=["0-13", "14-17", "18-29", "30-44", "45-59", "60 y más"]).astype(str)
    jefe = base.loc[base.p203 == 1, [*LLAVES, "sexo"]].drop_duplicates(LLAVES).rename(columns={"sexo": "sexo_jefe"})
    base = base.merge(jefe, on=LLAVES, how="left", validate="m:1")
    base["gasto_pc_mensual"] = base.gashog2d / (12 * base.mieperho)
    if "inghog1d" in base:
        base["ingreso_pc_mensual"] = base.inghog1d / (12 * base.mieperho)
    base["estrato_diseno"] = base.departamento + "_" + base.estrato.astype(str)
    base["anio"] = anio

    chequear("25 códigos departamentales (01-25), Lima 15 y Callao 07 separados",
             sorted(base.departamento.unique()) == sorted(DEPARTAMENTOS),
             f"{base.departamento.nunique()} códigos: {', '.join(sorted(base.departamento.unique()))}")
    chequear("Sin factores de expansión faltantes o no positivos",
             base.facpob07.notna().all() and (base.facpob07 > 0).all() and (hog.factor07 > 0).all(),
             f"facpob07 faltantes: {base.facpob07.isna().sum()}")
    pob = base.facpob07.sum()
    chequear("Población expandida plausible (31-36 millones)", 31e6 < pob < 36e6, f"{pob:,.0f} personas",
             esencial=False)

    # Base de hogares con el ponderador poblacional oficial del INEI (factor07 x mieperho)
    hog["departamento"] = hog.ubigeo.str[:2]
    hog["nombre_departamento"] = hog.departamento.map(DEPARTAMENTOS)
    hog["area"] = np.where(hog.estrato <= 5, "Urbana", "Rural")
    hog["region_natural"] = hog.dominio.map(REGION_NATURAL)
    hog["dominio_nombre"] = hog.dominio.map(DOMINIOS)
    hog["pobre"] = (hog.pobreza <= 2).astype(int)
    hog["pobre_extremo"] = (hog.pobreza == 1).astype(int)
    hog["pondera"] = hog.factor07 * hog.mieperho
    hog["estrato_diseno"] = hog.departamento + "_" + hog.estrato.astype(str)
    hog["gasto_pc_mensual"] = hog.gashog2d / (12 * hog.mieperho)
    hog = hog.merge(jefe, on=LLAVES, how="left", validate="1:1")
    hog["anio"] = anio
    KW_HOG = {"w": "pondera"}

    # Pobreza: dos estimadores (oficial con la sumaria y alternativo con personas)
    nac_hog = proporcion(hog, "pobre", **KW_HOG)
    nac = proporcion(base, "pobre")
    simple = 100 * base.pobre.mean()
    chequear(f"Pobreza monetaria nacional (sumaria, factor07 x mieperho; metodo INEI) a <= 0.1 p.p. de "
             f"{REFERENCIA['pobreza_nacional']} %",
             abs(nac_hog["valor_pct"] - REFERENCIA["pobreza_nacional"]) <= TOL_NACIONAL,
             f"{nac_hog['valor_pct']:.2f} % (IC 95 %: {nac_hog['ic95_inf']:.2f}-{nac_hog['ic95_sup']:.2f}; "
             f"CV {nac_hog['cv_pct']:.1f} %)")
    chequear(f"Pobreza monetaria nacional (personas residentes, facpob07) cercana a "
             f"{REFERENCIA['pobreza_nacional']} %",
             abs(nac["valor_pct"] - REFERENCIA["pobreza_nacional"]) <= (TOL_NACIONAL if anio == 2024 else 0.5),
             f"{nac['valor_pct']:.2f} % (IC 95 %: {nac['ic95_inf']:.2f}-{nac['ic95_sup']:.2f}); estimador "
             "alternativo", esencial=anio == 2024)
    chequear("La ponderacion importa: el promedio simple difiere del ponderado",
             abs(simple - nac["valor_pct"]) > 0.5,
             f"promedio simple {simple:.2f} % vs ponderado {nac['valor_pct']:.2f} % (el simple NO se usa)",
             esencial=False)
    ext = proporcion(hog, "pobre_extremo", **KW_HOG)
    chequear(f"Pobreza extrema cercana a {REFERENCIA['extrema']} %", abs(ext["valor_pct"] - REFERENCIA["extrema"]) <= TOL_AREA,
             f"{ext['valor_pct']:.2f} %", esencial=False)
    area = por_grupo(hog, "pobre", "area", **KW_HOG).set_index("categoria").valor_pct
    chequear(f"Pobreza urbana cercana a {REFERENCIA['urbana']} %", abs(area["Urbana"] - REFERENCIA["urbana"]) <= TOL_AREA,
             f"{area['Urbana']:.2f} %")
    chequear(f"Pobreza rural cercana a {REFERENCIA['rural']} %", abs(area["Rural"] - REFERENCIA["rural"]) <= TOL_AREA,
             f"{area['Rural']:.2f} %")

    ref_dep = RAIZ / "referencias" / f"pobreza_departamento_{anio}.csv"
    if ref_dep.exists():
        ref = pd.read_csv(ref_dep, dtype={"ccdd": str}).set_index("ccdd").pobreza_pct
        dep = por_grupo(hog, "pobre", "departamento", **KW_HOG).set_index("categoria").valor_pct.round(1)
        dif = (dep - ref).abs()
        chequear("Pobreza departamental igual a la referencia de la sesion 16 (25 de 25, redondeo a 0.1)",
                 (dif <= 0.1).all() and len(dif.dropna()) == 25,
                 f"diferencia maxima {dif.max():.2f} p.p. (departamento {dif.idxmax()}); "
                 f"{int((dif <= 0.1).sum())} de 25 coinciden")
        dep_p = por_grupo(base, "pobre", "departamento").set_index("categoria").valor_pct
        d2 = (dep_p - ref).abs()
        chequear("Sensibilidad: con personas y facpob07 la diferencia departamental es menor a 1 p.p.",
                 d2.max() < 1.0, f"diferencia maxima {d2.max():.2f} p.p. (departamento {d2.idxmax()})",
                 esencial=False)
    # Módulos adicionales (cualquier módulo de la ENAHO), unidos sin duplicar filas
    for m in [f"{int(x):02d}" for x in (modulos or [])]:
        mdf, niv, archivo = enaho.leer(anio, m)
        mdf = mdf.drop(columns=["anio", "ubigeo", "dominio", "estrato", "mes", "facpob07", "factor07",
                                "nconglome", "sub_conglome", "codinfor", "ticuest01", "longitud", "latitud"],
                       errors="ignore")
        if niv == "detalle":
            chequear(f"Modulo {m} ({enaho.MODULOS.get(m, '')}) no unido: varias filas por unidad", True,
                     f"{archivo}: agregalo antes con la skill explorando-enaho", esencial=False)
            continue
        n_b, n_h = len(base), len(hog)
        base = enaho.unir(base, mdf, niv, sufijo=f"_m{m}")
        if niv == "hogar":
            hog = enaho.unir(hog, mdf, niv, sufijo=f"_m{m}")
        cobertura = base.filter(like=f"_m{m}").notna().any(axis=1).mean() * 100
        chequear(f"Modulo {m} ({enaho.MODULOS.get(m, '')}) unido a nivel {niv} sin duplicar filas",
                 len(base) == n_b and len(hog) == n_h,
                 f"{archivo}: {mdf.shape[1]} variables; {cobertura:.1f} % de las personas con dato")
    meta.update({"pobreza_nacional": nac_hog, "pobreza_personas": nac, "simple": simple,
                 "modulos": modulos or []})
    return base, hog, chequeos, meta


def indicadores(base: pd.DataFrame, hog: pd.DataFrame) -> pd.DataFrame:
    """Tabla larga de indicadores ponderados con error de muestreo.

    Desagregaciones territoriales y por jefatura: sumaria con factor07 x mieperho (metodo oficial INEI).
    Desagregaciones individuales (sexo, edad): personas residentes con facpob07.
    """
    partes = []
    for ind, var in [("pobreza_monetaria", "pobre"), ("pobreza_extrema", "pobre_extremo")]:
        t = pd.DataFrame([{"categoria": "Perú", **proporcion(hog, var, w="pondera")}])
        partes.append(t.assign(desagregacion="nacional", indicador=ind, ponderador="factor07*mieperho"))
        for g in ["area", "region_natural", "dominio_nombre", "departamento", "sexo_jefe"]:
            partes.append(por_grupo(hog, var, g, w="pondera").assign(
                desagregacion=g, indicador=ind, ponderador="factor07*mieperho"))
        for g in ["sexo", "grupo_edad"]:
            partes.append(por_grupo(base, var, g).assign(desagregacion=g, indicador=ind, ponderador="facpob07"))
    out = pd.concat(partes, ignore_index=True)
    es_dep = out.desagregacion == "departamento"
    out["codigo"] = np.where(es_dep, out.categoria, "")
    out.loc[es_dep, "categoria"] = out.loc[es_dep, "codigo"].map(DEPARTAMENTOS)
    cols = ["indicador", "desagregacion", "codigo", "categoria", "valor_pct", "ee_pct", "ic95_inf", "ic95_sup",
            "cv_pct", "n_muestral", "poblacion_expandida", "ponderador"]
    out = out[cols]
    num = ["valor_pct", "ee_pct", "ic95_inf", "ic95_sup", "cv_pct"]
    out[num] = out[num].round(3)
    out["poblacion_expandida"] = out.poblacion_expandida.round(0).astype("int64")
    out["confiable_cv15"] = out.cv_pct <= 15
    return out


def escribir_validacion(chequeos, meta, ruta: Path, anio: int) -> bool:
    ok_esenciales = all(ok for _, ok, _, es in chequeos if es)
    lin = ["VALIDACION ENAHO " + str(anio), "=" * 78,
           f"Generado: {datetime.now():%Y-%m-%d %H:%M}  |  script: .claude/skills/limpiando-enaho/scripts/limpiar.py",
           f"Fuentes: {meta['archivo_sumaria']} (modulo 34) y {meta['archivo_miembros']} (modulo 02)",
           "Indicadores territoriales: sumaria con factor07 x mieperho (INEI); individuales: personas con facpob07.",
           "Error estandar: linealizacion de Taylor (UPM = conglome, estratos = departamento x estrato).", ""]
    for nombre, ok, detalle, esencial in chequeos:
        marca = "APROBADA" if ok else ("FALLIDA " if esencial else "ADVERTENCIA")
        lin.append(f"[{marca}] {nombre}{'' if esencial else ' (complementaria)'}")
        lin.append(f"           {detalle}")
    n_ok = sum(ok for _, ok, _, _ in chequeos)
    lin += ["", f"Resumen: {n_ok} de {len(chequeos)} verificaciones aprobadas.",
            "RESULTADO: " + ("TODAS LAS VALIDACIONES ESENCIALES APROBADAS" if ok_esenciales
                             else "FALLO DE VALIDACION ESENCIAL: la base NO se guardo")]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(lin) + "\n", encoding="utf-8")
    print("\n".join(lin))
    return ok_esenciales


def procesar(anio: int, salidas: Path, datos: Path, modulos: list[str], forzar: bool) -> bool:
    """Procesa un año. En 2024 escribe además los nombres originales (validacion.txt, indicadores.csv)."""
    parquet = salidas / f"personas_{anio}.parquet"
    parquet_hog = salidas / f"hogares_{anio}.parquet"
    validacion = salidas / f"validacion_{anio}.txt"
    if parquet.exists() and parquet_hog.exists() and validacion.exists() and not forzar and not modulos:
        print(f"Ya existen {parquet.name} y {parquet_hog.name}; usa --forzar para rehacerlas.")
        print(validacion.read_text(encoding="utf-8"))
        return True
    base, hog, chequeos, meta = construir(anio, datos, modulos)
    ok = escribir_validacion(chequeos, meta, validacion, anio)
    if anio == 2024:
        (salidas / "validacion.txt").write_text(validacion.read_text(encoding="utf-8"), encoding="utf-8")
    if not ok:
        print(f"ERROR: una validacion esencial fallo en {anio}. Revisa {validacion.name}; no se ajustan cifras.",
              file=sys.stderr)
        return False
    cols = ["anio", "conglome", "vivienda", "hogar", "codperso", "ubigeo", "departamento", "nombre_departamento",
            "dominio", "dominio_nombre", "region_natural", "estrato", "estrato_diseno", "urbano", "area", "p203",
            "sexo", "edad", "grupo_edad", "sexo_jefe", "mieperho", "pobreza", "pobre", "pobre_extremo",
            "linea", "linpe", "gasto_pc_mensual", "ingreso_pc_mensual", "facpob07", "factor07"]
    extra = [c for c in base.columns if re.search(r"_m\d{2}$", c)]
    out = base[[c for c in cols if c in base.columns] + extra].copy()
    for c in extra:                                   # columnas de texto mixto -> texto (parquet estable)
        if out[c].dtype == object:
            out[c] = out[c].astype("string")
    out.to_parquet(parquet, index=False)
    cols_h = ["anio", "conglome", "vivienda", "hogar", "ubigeo", "departamento", "nombre_departamento", "dominio",
              "dominio_nombre", "region_natural", "estrato", "estrato_diseno", "area", "sexo_jefe", "mieperho",
              "pobreza", "pobre", "pobre_extremo", "linea", "linpe", "gasto_pc_mensual", "factor07", "pondera"]
    extra_h = [c for c in hog.columns if re.search(r"_m\d{2}$", c)]
    oh = hog[[c for c in cols_h if c in hog.columns] + extra_h].copy()
    for c in extra_h:
        if oh[c].dtype == object:
            oh[c] = oh[c].astype("string")
    oh.to_parquet(parquet_hog, index=False)
    ind = indicadores(base, hog).assign(anio=anio)
    ind.to_csv(salidas / f"indicadores_{anio}.csv", index=False, encoding="utf-8")
    if anio == 2024:
        ind.drop(columns="anio").to_csv(salidas / "indicadores.csv", index=False, encoding="utf-8")
    print(f"\nGuardado {anio}: salidas/{parquet.name} ({len(base):,} personas, {len(extra)} variables de modulos "
          f"adicionales), salidas/{parquet_hog.name} ({len(hog):,} hogares), salidas/indicadores_{anio}.csv.")
    return True


def serie(salidas: Path) -> Path | None:
    """Une todos los indicadores_<anio>.csv disponibles en salidas/serie_indicadores.csv."""
    partes = [pd.read_csv(p, dtype={"codigo": str}) for p in sorted(salidas.glob("indicadores_20??.csv"))]
    if not partes:
        return None
    s = pd.concat(partes, ignore_index=True)
    destino = salidas / "serie_indicadores.csv"
    s.to_csv(destino, index=False, encoding="utf-8")
    print(f"Serie: {destino.name} con los años {sorted(s.anio.unique().tolist())} ({len(s)} filas).")
    return destino


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024, choices=sorted(CODIGOS_INEI))
    ap.add_argument("--anios", type=int, nargs="+", choices=sorted(CODIGOS_INEI),
                    help="varios años; genera además salidas/serie_indicadores.csv")
    ap.add_argument("--modulos", nargs="*", default=[], help="módulos adicionales a unir, p. ej. 03 04 05 01")
    ap.add_argument("--datos", default=str(RAIZ / "datos"))
    ap.add_argument("--salidas", default=str(RAIZ / "salidas"))
    ap.add_argument("--forzar", action="store_true", help="rehacer aunque ya exista la base")
    a = ap.parse_args()
    salidas = Path(a.salidas)
    salidas.mkdir(parents=True, exist_ok=True)
    anios = a.anios or [a.anio]
    fallidos = [an for an in anios if not procesar(an, salidas, Path(a.datos), a.modulos, a.forzar)]
    serie(salidas)
    if fallidos:
        sys.exit(f"ERROR: fallo la validacion esencial en {fallidos}.")


if __name__ == "__main__":
    main()
