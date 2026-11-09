"""Mapa coroplético APA 7 de la pobreza monetaria departamental (ENAHO 2024).

    uv run .claude/skills/mapeando-enaho/scripts/mapear.py
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_extrema --numero 4

Reglas (no negociables):
  - Une por código oficial: departamento = ubigeo[:2] (texto, con cero inicial) con FIRST_IDDP del GeoJSON.
    Nunca por nombre ("APURIMAC" no es "Apurímac").
  - Exige 25 unidades territoriales, ninguna sin dato; Lima (15) y Callao (07) separados.
  - Escala secuencial de un solo tono, desde 0, con la unidad (% de personas) en la leyenda.
  - Compara cada valor con referencias/pobreza_departamento_2024.csv (sesión 16) y lo escribe en
    salidas/validacion_mapa.txt.
Si falta salidas/indicadores.csv sale con código 2: ejecutar primero la skill limpiando-enaho.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def _raiz() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    return Path.cwd()


RAIZ = _raiz()
sys.path.insert(0, str(RAIZ))
from comun import apa  # noqa: E402

import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import BoundaryNorm  # noqa: E402

GEOJSON = RAIZ / "datos" / "peru_departamental_simple.geojson"
URL_GEOJSON = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/"
               "Data/peru_departamental_simple.geojson")
INDICADORES = RAIZ / "salidas" / "indicadores.csv"
REFERENCIA = RAIZ / "referencias" / "pobreza_departamento_2024.csv"


def geometrias() -> gpd.GeoDataFrame:
    if not GEOJSON.exists():
        import httpx
        GEOJSON.parent.mkdir(exist_ok=True)
        GEOJSON.write_bytes(httpx.get(URL_GEOJSON, timeout=60, follow_redirects=True).content)
    g = gpd.read_file(GEOJSON)
    g["FIRST_IDDP"] = g.FIRST_IDDP.astype(str).str.zfill(2)
    return g


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--indicador", default="pobreza_monetaria", choices=["pobreza_monetaria", "pobreza_extrema"])
    ap.add_argument("--numero", type=int, default=1)
    ap.add_argument("--archivo", default=None)
    a = ap.parse_args()
    if not INDICADORES.exists():
        print("ERROR: no existe salidas/indicadores.csv. Ejecuta primero la skill limpiando-enaho:\n"
              "  uv run .claude/skills/limpiando-enaho/scripts/limpiar.py", file=sys.stderr)
        sys.exit(2)
    ind = pd.read_csv(INDICADORES, dtype={"codigo": str})
    dep = ind.query("indicador == @a.indicador and desagregacion == 'departamento'").copy()
    dep["codigo"] = dep.codigo.str.zfill(2)
    nac = float(ind.query("indicador == @a.indicador and desagregacion == 'nacional'").valor_pct.iloc[0])

    geo = geometrias()
    mapa = geo.merge(dep, left_on="FIRST_IDDP", right_on="codigo", how="left", validate="1:1")
    sin_dato = mapa[mapa.valor_pct.isna()].NOMBDEP.tolist()
    if len(mapa) != 25 or sin_dato or set(mapa.FIRST_IDDP) != set(dep.codigo):
        sys.exit(f"ERROR: la unión por código no cubre 25 departamentos (filas {len(mapa)}, sin dato {sin_dato}).")
    if not {"07", "15"} <= set(mapa.FIRST_IDDP):
        sys.exit("ERROR: Lima (15) y Callao (07) deben estar separados.")

    # Validación contra la referencia de la sesión 16
    lineas = [f"VALIDACION DEL MAPA ({a.indicador})", "=" * 60,
              f"Union: ubigeo[:2] (indicadores.csv) = FIRST_IDDP (GeoJSON); unidades unidas: {mapa.valor_pct.notna().sum()}/25"]
    if a.indicador == "pobreza_monetaria" and REFERENCIA.exists():
        ref = pd.read_csv(REFERENCIA, dtype={"ccdd": str})
        cmp_ = mapa[["FIRST_IDDP", "NOMBDEP", "valor_pct"]].merge(ref, left_on="FIRST_IDDP", right_on="ccdd")
        cmp_["dif"] = (cmp_.valor_pct.round(1) - cmp_.pobreza_pct).round(2)
        ok = (cmp_.dif.abs() <= 0.1).sum()
        lineas.append(f"Coinciden con referencias/pobreza_departamento_2024.csv (|dif| <= 0.1 p.p.): {ok}/25")
        lineas += [f"  {r.FIRST_IDDP} {r.NOMBDEP:<15} calculado {r.valor_pct:5.1f}  referencia {r.pobreza_pct:5.1f}"
                   f"  dif {r.dif:+.1f}" for r in cmp_.itertuples()]
        lineas.append("RESULTADO: " + ("APROBADA" if ok == 25 else "REVISAR DIFERENCIAS"))
    (RAIZ / "salidas" / f"validacion_mapa{'' if a.indicador == 'pobreza_monetaria' else '_extrema'}.txt").write_text(
        "\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))

    # Mapa
    apa.aplicar_estilo()
    tope = 50 if a.indicador == "pobreza_monetaria" else max(15, 5 * (int(mapa.valor_pct.max() // 5) + 1))
    cortes = list(range(0, tope + 1, 10 if a.indicador == "pobreza_monetaria" else 3))
    norm = BoundaryNorm(cortes, plt.get_cmap(apa.CMAP).N)
    fig, ax = plt.subplots(figsize=(7, 8.2))
    mapa.plot(column="valor_pct", cmap=apa.CMAP, norm=norm, edgecolor="#404040", linewidth=0.4, ax=ax,
              legend=True, legend_kwds={"label": "Población en situación de pobreza (% de personas)",
                                        "orientation": "horizontal", "shrink": 0.6, "pad": 0.02,
                                        "ticks": cortes, "spacing": "uniform"})
    pts = mapa.to_crs(32718).representative_point().to_crs(mapa.crs)
    for (x, y), v, cod in zip(zip(pts.x, pts.y), mapa.valor_pct, mapa.FIRST_IDDP):
        if cod == "07":   # Callao es muy pequeño: etiqueta desplazada con línea guía
            ax.annotate(f"Callao {v:.1f}", (x, y), xytext=(x - 2.6, y + 0.4), fontsize=7.5,
                        arrowprops={"arrowstyle": "-", "lw": 0.5, "color": "#404040"})
            continue
        claro = v < (cortes[-1] * 0.6)
        ax.text(x, y, f"{v:.1f}", ha="center", va="center", fontsize=7.5, color="#111" if claro else "white")
    ax.set_axis_off()
    nombre_ind = "pobreza monetaria" if a.indicador == "pobreza_monetaria" else "pobreza extrema"
    titulo = f"Incidencia de la {nombre_ind} por departamento, Perú 2024"
    nota = (f"Porcentaje de personas en situación de {nombre_ind} (promedio nacional: {nac:.1f} %). Estimaciones "
            "ponderadas con factor07 × mieperho, método oficial del INEI. La unión territorial usa el código "
            "departamental del ubigeo (ubigeo[:2]) y FIRST_IDDP; Lima y Callao se presentan por separado. "
            f"Fuente: {apa.FUENTE_ENAHO}; límites departamentales de D2CML (2024).")
    apa.encabezar(fig, a.numero, titulo, nota, ancho_nota=95, arriba=0.9, abajo=0.1)
    archivo = a.archivo or ("pobreza_departamento.png" if a.indicador == "pobreza_monetaria"
                            else "pobreza_extrema_departamento.png")
    ruta = apa.guardar(fig, RAIZ / "mapas" / archivo)
    print(f"\nMapa: {ruta.relative_to(RAIZ)} (25 unidades territoriales)")


if __name__ == "__main__":
    main()
