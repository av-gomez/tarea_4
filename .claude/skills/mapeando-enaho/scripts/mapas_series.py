"""Mapas multianuales de la pobreza departamental (ENAHO 2019-2025), con el sistema visual del proyecto.

    uv run .claude/skills/mapeando-enaho/scripts/mapas_series.py mosaico            # un mapa por año, misma escala
    uv run .claude/skills/mapeando-enaho/scripts/mapas_series.py cambio --desde 2019 --hasta 2025
    uv run .claude/skills/mapeando-enaho/scripts/mapas_series.py anio --anio 2025   # mapa de un año

Mismas reglas que mapear.py: unión por código ubigeo[:2] = FIRST_IDDP (nunca por nombre), 25 unidades con
dato, Lima y Callao separados. Escala secuencial de un tono para niveles y divergente (azul baja, rojo sube,
gris neutro en 0) para cambios. Lee salidas/serie_indicadores.csv (limpiando-enaho --anios ...).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(RAIZ))
from comun import apa  # noqa: E402

import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import BoundaryNorm, TwoSlopeNorm  # noqa: E402

GEOJSON = RAIZ / "datos" / "peru_departamental_simple.geojson"
SERIE = RAIZ / "salidas" / "serie_indicadores.csv"


def _datos(indicador: str) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    if not SERIE.exists():
        sys.exit("ERROR: falta salidas/serie_indicadores.csv; ejecuta limpiando-enaho con --anios.")
    if not GEOJSON.exists():
        import httpx
        GEOJSON.write_bytes(httpx.get("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
                                      "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson",
                                      timeout=60).content)
    geo = gpd.read_file(GEOJSON)
    geo["FIRST_IDDP"] = geo.FIRST_IDDP.astype(str).str.zfill(2)
    s = pd.read_csv(SERIE, dtype={"codigo": str})
    d = s[(s.indicador == indicador) & (s.desagregacion == "departamento")].copy()
    d["codigo"] = d.codigo.str.zfill(2)
    return geo, d


def _unir(geo, d):
    m = geo.merge(d, left_on="FIRST_IDDP", right_on="codigo", how="left", validate="1:1")
    if len(m) != 25 or m.valor_pct.isna().any() or not {"07", "15"} <= set(m.FIRST_IDDP):
        sys.exit(f"ERROR: la unión por código no cubre 25 departamentos con dato ({m.valor_pct.notna().sum()}).")
    return m


def mosaico(a):
    geo, d = _datos(a.indicador)
    anios = sorted(d.anio.unique())
    apa.aplicar_estilo()
    cols = 4
    filas = int(np.ceil(len(anios) / cols))
    fig, axes = plt.subplots(filas, cols, figsize=(11, 4.6 * filas))
    cortes = list(range(0, 55, 5))
    norm = BoundaryNorm(cortes, apa.CMAP.N)
    for ax in axes.flat:
        ax.set_axis_off()
    for ax, anio in zip(axes.flat, anios):
        m = _unir(geo, d[d.anio == anio])
        m.plot(column="valor_pct", cmap=apa.CMAP, norm=norm, edgecolor=apa.SUPERFICIE, linewidth=0.6, ax=ax)
        nac = m.valor_pct.describe()
        ax.set_title(str(anio), loc="left", fontsize=13, fontweight="semibold")
        top = m.loc[m.valor_pct.idxmax()]
        ax.text(0.02, 0.02, f"Máx.: {top.categoria} {top.valor_pct:.0f} %", transform=ax.transAxes, fontsize=8.5,
                color=apa.TINTA_2)
    ax_l = axes.flat[len(anios)] if len(anios) < filas * cols else fig.add_axes([0.3, 0.02, 0.4, 0.02])
    sm = plt.cm.ScalarMappable(cmap=apa.CMAP, norm=norm)
    cax = ax_l.inset_axes([0.05, 0.45, 0.9, 0.06]) if len(anios) < filas * cols else ax_l
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=cortes[::2])
    cb.outline.set_visible(False)
    cb.set_label("Personas en pobreza monetaria (%)", color=apa.TINTA_2)
    fig.subplots_adjust(wspace=0.02, hspace=0.06)
    archivo = f"mosaico_{a.indicador}_{anios[0]}_{anios[-1]}.png"
    apa.guardar(fig, RAIZ / "mapas" / archivo)
    print(f"[Figura {a.numero}] mapas/{archivo}\n  Título: Pobreza monetaria por departamento, Perú {anios[0]}-{anios[-1]}"
          "\n  Nota: Misma escala de color en todos los años (cortes de 5 puntos). Unión por código ubigeo[:2] = "
          "FIRST_IDDP; 25 unidades, Lima y Callao separados. Estimaciones ponderadas con factor07 × mieperho. "
          f"Fuente: INEI, ENAHO {anios[0]}-{anios[-1]}; límites departamentales de D2CML (2024).")


def cambio(a):
    geo, d = _datos(a.indicador)
    p = d[d.anio.isin([a.desde, a.hasta])].pivot_table(index="codigo", columns="anio", values="valor_pct")
    p["cambio"] = p[a.hasta] - p[a.desde]
    m = _unir(geo, p.reset_index()[["codigo", "cambio", a.desde, a.hasta]].rename(columns={"cambio": "valor_pct"}))
    lim = max(abs(m.valor_pct.min()), abs(m.valor_pct.max()))
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7, 8.4))
    ax.set_axis_off()
    m.plot(column="valor_pct", cmap=apa.CMAP_DIVERGENTE, norm=TwoSlopeNorm(0, -lim, lim), edgecolor=apa.SUPERFICIE,
           linewidth=0.7, ax=ax)
    pts = m.to_crs(32718).representative_point().to_crs(m.crs)
    for (x, y), v, cod in zip(zip(pts.x, pts.y), m.valor_pct, m.FIRST_IDDP):
        if cod == "07":
            ax.annotate(f"Callao {v:+.1f}", (x, y), xytext=(x - 2.8, y + 0.5), fontsize=8,
                        arrowprops={"arrowstyle": "-", "lw": 0.5, "color": apa.TINTA_2})
            continue
        ax.text(x, y, f"{v:+.1f}", ha="center", va="center", fontsize=8,
                color="white" if abs(v) > lim * 0.55 else apa.TINTA)
    sm = plt.cm.ScalarMappable(cmap=apa.CMAP_DIVERGENTE, norm=TwoSlopeNorm(0, -lim, lim))
    cax = ax.inset_axes([0.08, 0.03, 0.45, 0.022])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.set_label(f"Cambio {a.desde}-{a.hasta} (puntos porcentuales)", color=apa.TINTA_2, fontsize=9)
    archivo = f"cambio_{a.indicador}_{a.desde}_{a.hasta}.png"
    apa.guardar(fig, RAIZ / "mapas" / archivo)
    sube = (m.valor_pct > 0).sum()
    print(f"[Figura {a.numero}] mapas/{archivo}\n  Título: Cambio de la pobreza monetaria por departamento, "
          f"{a.desde}-{a.hasta}\n  Nota: Diferencia en puntos porcentuales ({a.hasta} menos {a.desde}); rojo: "
          f"aumentó ({sube} departamentos), azul: disminuyó. Escala divergente centrada en 0. Unión por código "
          f"ubigeo[:2] = FIRST_IDDP. Fuente: INEI, ENAHO {a.desde} y {a.hasta}.")


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for n, f in [("mosaico", mosaico), ("cambio", cambio)]:
        p = sp.add_parser(n)
        p.add_argument("--indicador", default="pobreza_monetaria")
        p.add_argument("--desde", type=int, default=2019)
        p.add_argument("--hasta", type=int, default=2025)
        p.add_argument("--numero", default="1")
        p.set_defaults(f=f)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
