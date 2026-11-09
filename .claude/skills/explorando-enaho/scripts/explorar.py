"""Explora cualquier módulo de la ENAHO (2019-2025): catálogo, diccionario de variables e indicadores ponderados.

    # 1. Qué módulos y años hay
    uv run .claude/skills/explorando-enaho/scripts/explorar.py modulos

    # 2. Buscar variables por palabra en las etiquetas oficiales (descarga el módulo si falta)
    uv run .claude/skills/explorando-enaho/scripts/explorar.py diccionario --anio 2025 --modulo 04 --buscar seguro

    # 3. Indicador ponderado de cualquier variable, para uno o varios años y por grupos
    uv run .claude/skills/explorando-enaho/scripts/explorar.py indicador --modulo 04 --variable p4191 \
        --condicion "==1" --nombre afiliacion_essalud --anios 2019 2025 --por area
    uv run .claude/skills/explorando-enaho/scripts/explorar.py indicador --modulo 05 --variable i524a1 \
        --universo "edad >= 14" --nombre ingreso_ocupacion --anios 2024 --por sexo        # media
    uv run .claude/skills/explorando-enaho/scripts/explorar.py indicador --modulo 01 --variable p110 \
        --condicion "in 1,2" --nombre agua_red_publica --anios 2025 --por departamento
    uv run .claude/skills/explorando-enaho/scripts/explorar.py indicador --modulo 07 --variable i601a \
        --agregar sum --nombre gasto_alimentos --anios 2025 --unidad hogar                 # módulo de detalle

Reglas:
  - La variable se une a la base limpia de personas del año (skill limpiando-enaho; se ejecuta si falta).
  - Módulos de detalle (varias filas por hogar) se agregan por hogar con --agregar (sum, mean, max, count).
  - --condicion convierte la variable en indicador 0/1 (proporción en %); sin ella se estima la media.
  - Ponderación: personas con facpob07 (--unidad persona, por defecto) u hogares con factor07 (--unidad hogar).
  - Error estándar por linealización de Taylor (UPM conglome, estratos departamento x estrato), IC 95 % y CV.
  - Los valores no válidos (faltantes, 999999 y similares códigos de "no sabe") se excluyen y se informan.
Escribe tablas/indicador_<nombre>.csv (una fila por año y categoría) para graficar o citar.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(RAIZ))
from comun import enaho  # noqa: E402
from comun.estimacion import media_ponderada, proporcion  # noqa: E402

LIMPIAR = RAIZ / ".claude" / "skills" / "limpiando-enaho" / "scripts" / "limpiar.py"
CODIGOS_NO_VALIDOS = {99, 999, 9999, 99999, 999999, 9999999}


def cmd_modulos(_):
    print("Años disponibles (código INEI):", ", ".join(f"{a} ({c})" for a, c in enaho.CODIGOS.items()))
    print("\nMódulos de la ENAHO anual:")
    for m, n in enaho.MODULOS.items():
        local = [str(a) for a in enaho.CODIGOS if enaho.ruta_zip(a, m).exists()]
        print(f"  {m}  {n:<55} descargado: {', '.join(local) if local else 'no'}")


def cmd_diccionario(a):
    d = enaho.diccionario(a.anio, a.modulo)
    if a.buscar:
        patron = "|".join(re.escape(p) for p in a.buscar.lower().split())
        sin = d.etiqueta.str.lower().str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
        d = d[sin.str.contains(patron) | d.variable.str.contains(patron)]
    destino = RAIZ / "salidas" / "diccionarios" / f"modulo{int(a.modulo):02d}_{a.anio}.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    enaho.diccionario(a.anio, a.modulo).to_csv(destino, index=False, encoding="utf-8")
    pd.set_option("display.max_colwidth", 90)
    print(d[["variable", "etiqueta", "valores"]].head(a.limite).to_string(index=False))
    print(f"\n{len(d)} variables coinciden. Diccionario completo: {destino.relative_to(RAIZ)}")


def _base(anio: int, unidad: str) -> pd.DataFrame:
    p = RAIZ / "salidas" / f"{'personas' if unidad == 'persona' else 'hogares'}_{anio}.parquet"
    if not p.exists():
        print(f"No existe {p.name}: ejecuto primero limpiando-enaho para {anio}...")
        r = subprocess.run([sys.executable, str(LIMPIAR), "--anio", str(anio)], capture_output=True, text=True,
                           encoding="utf-8")
        if r.returncode != 0:
            sys.exit(f"ERROR: la limpieza de {anio} falló:\n{r.stdout[-1500:]}\n{r.stderr[-800:]}")
    cols = None
    base = pd.read_parquet(p, columns=cols)
    return base[[c for c in base.columns if not re.search(r"_m\d{2}$", c)]]


def _condicion(serie: pd.Series, cond: str) -> pd.Series:
    cond = cond.strip()
    if cond.startswith("in "):
        valores = [float(v) for v in cond[3:].split(",")]
        return serie.isin(valores).astype(float).where(serie.notna())
    m = re.fullmatch(r"(==|!=|>=|<=|>|<)\s*(-?[\d.]+)", cond)
    if not m:
        raise SystemExit(f"Condición no válida: {cond!r}. Usa ==1, >=7, <3 o 'in 1,2'.")
    op, v = m.group(1), float(m.group(2))
    res = {"==": serie == v, "!=": serie != v, ">=": serie >= v, "<=": serie <= v, ">": serie > v,
           "<": serie < v}[op]
    return res.astype(float).where(serie.notna())


def preparar(anio: int, a) -> tuple[pd.DataFrame, str, dict]:
    mdf, niv, archivo = enaho.leer(anio, a.modulo)
    if a.variable not in mdf.columns:
        sugerencias = [c for c in mdf.columns if c.startswith(a.variable[:3])][:15]
        raise SystemExit(f"ERROR: {a.variable!r} no existe en el módulo {a.modulo} de {anio}. "
                         f"Parecidas: {sugerencias}. Usa el subcomando diccionario.")
    llaves = enaho.LLAVES_PERSONA if niv == "persona" else enaho.LLAVES_HOGAR
    sub = mdf[[*[k for k in enaho.LLAVES_PERSONA if k in mdf.columns], a.variable]].copy()
    sub[a.variable] = pd.to_numeric(sub[a.variable], errors="coerce")
    invalidos = int(sub[a.variable].isin(CODIGOS_NO_VALIDOS).sum())
    sub.loc[sub[a.variable].isin(CODIGOS_NO_VALIDOS), a.variable] = np.nan
    if niv == "detalle":
        if not a.agregar:
            raise SystemExit(f"ERROR: el módulo {a.modulo} tiene varias filas por hogar; indica --agregar "
                             "(sum, mean, max o count).")
        sub = sub.groupby(enaho.LLAVES_HOGAR, as_index=False)[a.variable].agg(a.agregar)
        niv, llaves = "hogar", enaho.LLAVES_HOGAR
    else:
        sub = sub[[*llaves, a.variable]]
    unidad = a.unidad
    if unidad == "persona" and niv == "persona":
        base = _base(anio, "persona")
    elif unidad == "persona":
        base = _base(anio, "persona")              # variable de hogar atribuida a cada persona
    else:
        if niv == "persona":
            raise SystemExit("ERROR: una variable de personas no puede analizarse por hogar sin agregarla.")
        base = _base(anio, "hogar")
    datos = enaho.unir(base, sub.rename(columns={a.variable: "y_raw"}), niv)
    if a.universo:
        datos = datos.query(a.universo)
    datos["y"] = _condicion(datos.y_raw, a.condicion) if a.condicion else datos.y_raw
    peso = "facpob07" if unidad == "persona" else "factor07"
    meta = {"archivo": archivo, "nivel_modulo": niv, "invalidos": invalidos, "peso": peso,
            "sin_dato": int(datos.y.isna().sum()), "n": len(datos)}
    return datos, peso, meta


def cmd_indicador(a):
    filas = []
    for anio in a.anios:
        datos, peso, meta = preparar(anio, a)
        grupos = [("Perú", datos)] if not a.por else [(k, g) for k, g in datos.groupby(a.por, observed=True)]
        for cat, g in grupos:
            g = g.dropna(subset=["y"])
            if len(g) < 30:
                continue
            if a.condicion:
                r = proporcion(g, "y", w=peso)
                fila = {"valor": r["valor_pct"], "ee": r["ee_pct"], "ic95_inf": r["ic95_inf"],
                        "ic95_sup": r["ic95_sup"], "cv_pct": r["cv_pct"], "n_muestral": r["n_muestral"],
                        "poblacion_expandida": r["poblacion_expandida"], "medida": "porcentaje"}
            else:
                fila = {**media_ponderada(g, "y", w=peso), "medida": "media"}
            filas.append({"anio": anio, "indicador": a.nombre, "desagregacion": a.por or "nacional",
                          "categoria": cat, **fila, "modulo": a.modulo, "variable": a.variable,
                          "condicion": a.condicion or "", "universo": a.universo or "", "ponderador": peso,
                          "archivo_fuente": meta["archivo"], "excluidos_sin_dato": meta["sin_dato"],
                          "codigos_no_validos": meta["invalidos"]})
        print(f"{anio}: {meta['archivo']} (nivel {meta['nivel_modulo']}), {meta['n']:,} filas, "
              f"{meta['sin_dato']:,} sin dato excluidas, ponderador {peso}")
    if not filas:
        sys.exit("ERROR: no hubo observaciones suficientes para estimar.")
    out = pd.DataFrame(filas)
    if a.por == "departamento":
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("limpiar", LIMPIAR)
        lim = module_from_spec(spec)
        spec.loader.exec_module(lim)
        out["codigo"] = out.categoria
        out["categoria"] = out.codigo.map(lim.DEPARTAMENTOS)
    out["confiable_cv15"] = out.cv_pct <= 15
    for c in ["valor", "ee", "ic95_inf", "ic95_sup", "cv_pct"]:
        out[c] = out[c].astype(float).round(4)
    destino = RAIZ / "tablas" / f"indicador_{a.nombre}.csv"
    destino.parent.mkdir(exist_ok=True)
    out.to_csv(destino, index=False, encoding="utf-8")
    print(out[["anio", "categoria", "valor", "ic95_inf", "ic95_sup", "cv_pct", "n_muestral"]].to_string(index=False))
    print(f"\nGuardado: {destino.relative_to(RAIZ)}. Fuente: INEI, ENAHO {', '.join(map(str, a.anios))}, "
          f"módulo {a.modulo} ({enaho.MODULOS.get(f'{int(a.modulo):02d}', '')}).")


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("modulos").set_defaults(f=cmd_modulos)
    d = sp.add_parser("diccionario")
    d.add_argument("--anio", type=int, default=2024)
    d.add_argument("--modulo", required=True)
    d.add_argument("--buscar", default="")
    d.add_argument("--limite", type=int, default=60)
    d.set_defaults(f=cmd_diccionario)
    i = sp.add_parser("indicador")
    i.add_argument("--modulo", required=True)
    i.add_argument("--variable", required=True)
    i.add_argument("--nombre", required=True, help="nombre corto del indicador (para el archivo)")
    i.add_argument("--anios", type=int, nargs="+", default=[2024], choices=sorted(enaho.CODIGOS))
    i.add_argument("--condicion", default="", help="==1, >=7, <3 o 'in 1,2'; sin ella se estima la media")
    i.add_argument("--universo", default="", help="filtro pandas, p. ej. 'edad >= 15'")
    i.add_argument("--por", default="", help="area, region_natural, departamento, sexo, grupo_edad, sexo_jefe...")
    i.add_argument("--unidad", default="persona", choices=["persona", "hogar"])
    i.add_argument("--agregar", default="", choices=["", "sum", "mean", "max", "count"])
    i.set_defaults(f=cmd_indicador)
    a = ap.parse_args()
    if getattr(a, "modulo", None):
        a.modulo = f"{int(a.modulo):02d}"
    a.f(a)


if __name__ == "__main__":
    main()
