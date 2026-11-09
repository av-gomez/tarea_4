"""Visualizaciones de la ENAHO 2019-2025 con el sistema visual del proyecto (comun/apa.py).

    uv run .claude/skills/graficando-enaho/scripts/visualizar.py evolucion        # tendencia con IC 95 %
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py calor            # departamento x año
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py pendiente --desde 2019 --hasta 2025
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py distribucion     # gasto / línea de pobreza
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py perfil --indicadores agua_red_publica ...
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py waffle --anio 2025
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py macro --bcrp tablas/bcrp_inflacion.csv
    uv run .claude/skills/graficando-enaho/scripts/visualizar.py todas

Fuentes: salidas/serie_indicadores.csv y salidas/hogares_<año>.parquet (skill limpiando-enaho con --anios),
tablas/indicador_*.csv (skill explorando-enaho) y tablas/*.csv del servidor MCP del BCRP (graficar_serie).
Cada figura se guarda en figuras/ y su tabla de datos en tablas/, y el script imprime el pie APA sugerido.
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

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

SERIE = RAIZ / "salidas" / "serie_indicadores.csv"
FIG = RAIZ / "figuras"
TAB = RAIZ / "tablas"
NOTA_ENAHO = ("Estimaciones ponderadas (factor07 × mieperho, método del INEI); bandas o barras: IC 95 % por "
              "linealización de Taylor. Fuente: INEI, ENAHO {anios}.")


def _serie() -> pd.DataFrame:
    if not SERIE.exists():
        sys.exit("ERROR: falta salidas/serie_indicadores.csv. Ejecuta: uv run .claude/skills/limpiando-enaho/"
                 "scripts/limpiar.py --anios 2019 2020 2021 2022 2023 2024 2025")
    return pd.read_csv(SERIE, dtype={"codigo": str})


def _pie(numero, titulo, archivo, nota, datos=None):
    if datos is not None:
        TAB.mkdir(exist_ok=True)
        datos.to_csv(TAB / (Path(archivo).stem + ".csv"), index=False, encoding="utf-8")
    print(f"\n[Figura {numero}] figuras/{archivo}\n  Título: {titulo}\n  Nota: {nota}")
    if datos is not None:
        print(f"  Datos: tablas/{Path(archivo).stem}.csv")


def _anios(s):
    a = sorted(s.anio.unique())
    return f"{a[0]}-{a[-1]}" if len(a) > 1 else str(a[0])


# ---------------------------------------------------------------------------------------------- evolución
def evolucion(a):
    s = _serie()
    d = s[(s.indicador == a.indicador) & (s.desagregacion.isin(["nacional", "area"]))].copy()
    d["serie"] = np.where(d.desagregacion == "nacional", "Perú", d.categoria)
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colores = {"Rural": apa.NARANJA, "Perú": apa.AZUL, "Urbana": apa.AGUA}
    for nombre in ["Rural", "Perú", "Urbana"]:
        g = d[d.serie == nombre].sort_values("anio")
        c = colores[nombre]
        ax.fill_between(g.anio, g.ic95_inf, g.ic95_sup, color=c, alpha=0.14, linewidth=0)
        ax.plot(g.anio, g.valor_pct, color=c, linewidth=2.2 if nombre == "Perú" else 1.8)
        ax.scatter(g.anio, g.valor_pct, s=26, color=c, edgecolor=apa.SUPERFICIE, linewidth=1.2, zorder=3)
        ult = g.iloc[-1]
        apa.etiqueta_directa(ax, ult.anio, ult.valor_pct, f"{nombre}  {ult.valor_pct:.1f} %",
                             fontweight="semibold" if nombre == "Perú" else "normal")
        pri = g.iloc[0]
        ax.annotate(f"{pri.valor_pct:.1f}", (pri.anio, pri.valor_pct), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=9, color=apa.TINTA_2)
    ax.axvspan(2019.6, 2020.4, color=apa.GRIS_NEUTRO, alpha=0.18, linewidth=0)
    ax.text(2020, ax.get_ylim()[1], "Pandemia", ha="center", va="top", fontsize=9, color=apa.TINTA_2)
    ax.set_xticks(sorted(d.anio.unique()))
    ax.set_xlim(d.anio.min() - 0.5, d.anio.max() + 1.6)
    ax.set_ylim(0, None)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylabel("Personas en pobreza (%)")
    nombre_ind = "pobreza monetaria" if a.indicador == "pobreza_monetaria" else "pobreza extrema"
    archivo = f"evolucion_{a.indicador}.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"Evolución de la {nombre_ind} por área de residencia, Perú {_anios(d)}", archivo,
         NOTA_ENAHO.format(anios=_anios(d)), d[["anio", "serie", "valor_pct", "ic95_inf", "ic95_sup", "cv_pct"]])


# ------------------------------------------------------------------------------------------ mapa de calor
def calor(a):
    s = _serie()
    d = s[(s.indicador == a.indicador) & (s.desagregacion == "departamento")]
    m = d.pivot_table(index="categoria", columns="anio", values="valor_pct")
    m = m.loc[m[m.columns.max()].sort_values(ascending=False).index]
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7.2, 8.6))
    im = ax.imshow(m.values, cmap=apa.CMAP, vmin=0, vmax=max(50, np.nanmax(m.values)), aspect="auto")
    ax.grid(False)
    ax.set_xticks(range(m.shape[1]), m.columns)
    ax.set_yticks(range(m.shape[0]), m.index)
    ax.tick_params(length=0)
    ax.xaxis.tick_top()
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8.5,
                    color="white" if v >= 30 else apa.TINTA)
    for x in np.arange(-0.5, m.shape[1], 1):
        ax.axvline(x, color=apa.SUPERFICIE, linewidth=2)
    for y in np.arange(-0.5, m.shape[0], 1):
        ax.axhline(y, color=apa.SUPERFICIE, linewidth=2)
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.03, pad=0.02, aspect=40)
    cb.set_label("Personas en pobreza (%)", color=apa.TINTA_2)
    cb.outline.set_visible(False)
    archivo = f"calor_departamentos_{a.indicador}.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"Pobreza monetaria por departamento y año, Perú {_anios(d)}", archivo,
         "Valores en porcentaje de personas, ordenados de mayor a menor según el último año. Celdas más oscuras "
         "indican mayor pobreza. " + NOTA_ENAHO.format(anios=_anios(d)).split("; bandas")[0] + ". Fuente: INEI, "
         f"ENAHO {_anios(d)}.", m.reset_index())


# ---------------------------------------------------------------------------------------------- pendiente
def pendiente(a):
    s = _serie()
    d = s[(s.indicador == a.indicador) & (s.desagregacion == "departamento") & s.anio.isin([a.desde, a.hasta])]
    m = d.pivot_table(index="categoria", columns="anio", values="valor_pct").dropna()
    m["cambio"] = m[a.hasta] - m[a.desde]
    m = m.sort_values("cambio")
    nac = s[(s.indicador == a.indicador) & (s.desagregacion == "nacional")].set_index("anio").valor_pct
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7.6, 8.4))
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    for i, (dep, r) in enumerate(m.iterrows()):
        sube = r.cambio > 0
        ax.plot([r[a.desde], r[a.hasta]], [i, i], color=apa.NARANJA if sube else apa.AZUL, alpha=0.45,
                linewidth=2.4, solid_capstyle="round")
        ax.scatter(r[a.desde], i, s=34, color=apa.GRIS_NEUTRO, edgecolor=apa.SUPERFICIE, linewidth=1.2, zorder=3)
        ax.scatter(r[a.hasta], i, s=46, color=apa.NARANJA if sube else apa.AZUL, edgecolor=apa.SUPERFICIE,
                   linewidth=1.2, zorder=4)
        x_txt = max(r[a.desde], r[a.hasta])
        ax.text(x_txt + 1.2, i, f"{r.cambio:+.1f}", va="center", fontsize=8.8, color=apa.TINTA_2)
    ax.set_yticks(range(len(m)), m.index)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_xlabel("Personas en pobreza (%)")
    ax.set_xlim(0, m[[a.desde, a.hasta]].values.max() + 8)
    apa.leyenda_marcador(ax, [(str(a.desde), apa.GRIS_NEUTRO), (f"{a.hasta}: bajó", apa.AZUL),
                              (f"{a.hasta}: subió", apa.NARANJA)], loc="lower right")
    archivo = f"pendiente_departamentos_{a.desde}_{a.hasta}.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"Cambio de la pobreza monetaria por departamento entre {a.desde} y {a.hasta}", archivo,
         f"Cada línea une el valor de {a.desde} (gris) con el de {a.hasta} (color); el número indica el cambio en "
         f"puntos porcentuales. Nacional: {nac[a.desde]:.1f} % en {a.desde} y {nac[a.hasta]:.1f} % en {a.hasta}. "
         f"Diferencias pequeñas pueden no ser significativas (ver IC en tablas/). Fuente: INEI, ENAHO {a.desde} y "
         f"{a.hasta}.", m.reset_index())


# ------------------------------------------------------------------------------------------- distribución
def _kde_ponderado(x, w, malla, ancho):
    w = w / w.sum()
    dens = np.zeros_like(malla)
    for xi, wi in zip(np.array_split(x, 50), np.array_split(w, 50)):
        dens += (wi[:, None] * np.exp(-0.5 * ((malla[None, :] - xi[:, None]) / ancho) ** 2)).sum(0)
    return dens / (ancho * np.sqrt(2 * np.pi))


def distribucion(a):
    anios = sorted(int(p.stem.split("_")[1]) for p in (RAIZ / "salidas").glob("hogares_20??.parquet"))
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(8, 0.75 * len(anios) + 1.6))
    ax.grid(False)
    malla = np.linspace(-2.0, 2.6, 400)
    filas = []
    for k, anio in enumerate(reversed(anios)):
        h = pd.read_parquet(RAIZ / "salidas" / f"hogares_{anio}.parquet",
                            columns=["gasto_pc_mensual", "linea", "pondera", "pobre"])
        tasa = 100 * (h.pondera * h.pobre).sum() / h.pondera.sum()
        h = h[(h.gasto_pc_mensual > 0) & (h.linea > 0)]
        r = np.log(h.gasto_pc_mensual / h.linea).to_numpy()
        w = h.pondera.to_numpy()
        dens = _kde_ponderado(r, w, malla, 0.07)
        dens = dens / dens.max() * 1.15
        base = k
        pobre = malla < 0
        z = 10 - k
        ax.fill_between(malla, base, base + dens, where=~pobre, color=apa.AZUL, linewidth=0, zorder=z)
        ax.fill_between(malla, base, base + dens, where=pobre | np.isclose(malla, 0, atol=0.006),
                        color=apa.NARANJA, linewidth=0, zorder=z)
        ax.plot(malla, base + dens, color=apa.SUPERFICIE, linewidth=1.4, zorder=z)
        mediana = np.exp(np.interp(0.5, np.cumsum(w[np.argsort(r)]) / w.sum(), np.sort(r)))
        ax.text(-2.05, base + 0.18, str(anio), zorder=20, ha="right", va="bottom", fontsize=10, color=apa.TINTA,
                fontweight="semibold")
        ax.text(2.62, base + 0.18, f"pobreza {tasa:.1f} %", ha="right", va="bottom", fontsize=9,
                color=apa.TINTA_2, zorder=20)
        filas.append({"anio": anio, "pobreza_oficial_pct": round(tasa, 2),
                      "pct_gasto_bajo_linea": round(100 * (w * (r < 0)).sum() / w.sum(), 2), "mediana_gasto_sobre_linea": round(mediana, 3)})
    ax.axvline(0, color=apa.TINTA, linewidth=1, linestyle=(0, (3, 3)), zorder=30)
    ax.text(0, len(anios) + 0.6, "Línea de pobreza", ha="center", fontsize=9, color=apa.TINTA)
    ticks = [0.25, 0.5, 1, 2, 4, 8]
    ax.set_xticks(np.log(ticks), [f"{t:g}×" for t in ticks])
    ax.set_yticks([])
    ax.spines["bottom"].set_color(apa.EJE)
    ax.set_xlim(-2.1, 2.65)
    ax.set_ylim(-0.1, len(anios) + 0.9)
    ax.set_xlabel("Gasto per cápita del hogar como múltiplo de su línea de pobreza (escala logarítmica)")
    archivo = "distribucion_gasto_linea.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"Distribución del gasto per cápita respecto de la línea de pobreza, Perú {anios[0]}-{anios[-1]}",
         archivo, "Densidad ponderada por población (factor07 × mieperho) del cociente gasto per cápita / línea de "
         "pobreza del hogar (gashog2d / (12 × mieperho) / linea). El área naranja, a la izquierda de 1×, aproxima la "
         "población pobre; la cifra rotulada es la pobreza oficial (variable pobreza), que difiere en pocas décimas "
         "del cociente porque el INEI usa su propio agregado de gasto. Fuente: INEI, "
         f"ENAHO {anios[0]}-{anios[-1]}.", pd.DataFrame(filas))


# ------------------------------------------------------------------------------------------------- perfil
def perfil(a):
    filas = []
    for nombre in a.indicadores:
        p = TAB / f"indicador_{nombre}.csv"
        if not p.exists():
            sys.exit(f"ERROR: falta {p.name}; genéralo con la skill explorando-enaho.")
        filas.append(pd.read_csv(p))
    d = pd.concat(filas)
    d = d[d.desagregacion == "pobre"].copy()
    d["grupo"] = d.categoria.astype(str).map({"1": "Pobres", "0": "No pobres", "1.0": "Pobres", "0.0": "No pobres"})
    etiquetas = {"agua_red_publica": "Agua por red pública", "desague_red_publica": "Desagüe por red pública",
                 "afiliacion_essalud": "Afiliado a EsSalud", "afiliacion_sis": "Afiliado al SIS",
                 "secundaria_completa_25mas": "Secundaria completa o más (25+ años)",
                 "tasa_ocupacion_14mas": "Ocupado (14+ años)"}
    d["etiqueta"] = d.indicador.map(etiquetas).fillna(d.indicador)
    anios = sorted(d.anio.unique())
    apa.aplicar_estilo()
    fig, axes = plt.subplots(1, len(anios), figsize=(4.4 * len(anios) + 1.6, 0.62 * d.etiqueta.nunique() + 1.4),
                             sharey=True)
    axes = np.atleast_1d(axes)
    orden = (d[(d.anio == anios[-1]) & (d.grupo == "No pobres")].set_index("etiqueta").valor
             - d[(d.anio == anios[-1]) & (d.grupo == "Pobres")].set_index("etiqueta").valor).sort_values().index
    for ax, anio in zip(axes, anios):
        g = d[d.anio == anio].set_index(["etiqueta", "grupo"])
        ax.grid(axis="x")
        ax.grid(axis="y", visible=False)
        for i, et in enumerate(orden):
            vp, vn = g.loc[(et, "Pobres")], g.loc[(et, "No pobres")]
            ax.plot([vp.valor, vn.valor], [i, i], color=apa.GRIS_NEUTRO, linewidth=3, solid_capstyle="round")
            for v, c in [(vp, apa.NARANJA), (vn, apa.AZUL)]:
                ax.errorbar(v.valor, i, xerr=[[v.valor - v.ic95_inf], [v.ic95_sup - v.valor]], fmt="o", ms=7,
                            color=c, mec=apa.SUPERFICIE, mew=1.2, elinewidth=1, capsize=0, zorder=3)
            ax.text(116, i, f"{vn.valor - vp.valor:+.0f} p.p.", va="center", ha="right", fontsize=8.8,
                    color=apa.TINTA_2)
        ax.set_title(str(anio), loc="left", fontsize=11)
        ax.set_xlim(0, 117)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.spines["bottom"].set_bounds(0, 100)
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(range(len(orden)), orden)
    apa.leyenda_marcador(axes[-1], [("Pobres", apa.NARANJA), ("No pobres", apa.AZUL)], loc="lower left",
                         bbox_to_anchor=(0, -0.02))
    archivo = "perfil_brechas_pobres.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"Brechas de acceso entre población pobre y no pobre, Perú {' y '.join(map(str, anios))}",
         archivo, "Porcentaje de personas con cada característica; líneas horizontales: IC 95 %. A la derecha, "
         "diferencia en puntos porcentuales (no pobres menos pobres). Variables: módulo 01 (p110, p111a), 04 "
         "(p4191, p4195), 03 (p301a, 25 años o más) y 05 (ocu500, 14 años o más); ponderador facpob07. Fuente: "
         f"INEI, ENAHO {' y '.join(map(str, anios))}.",
         d[["anio", "indicador", "grupo", "valor", "ic95_inf", "ic95_sup", "cv_pct", "modulo", "variable"]])


# ------------------------------------------------------------------------------------------------- waffle
def waffle(a):
    s = _serie()
    r = s[(s.anio == a.anio) & (s.desagregacion == "nacional")].set_index("indicador").valor_pct
    total, extrema = r["pobreza_monetaria"], r["pobreza_extrema"]
    n_ext, n_pob = round(extrema), round(total)
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(5.2, 5.4))
    ax.axis("off")
    for k in range(100):
        fila, col = divmod(k, 10)
        c = apa.NARANJA if k < n_ext else (apa.AZUL if k < n_pob else "#e8e7e1")
        ax.add_patch(plt.Rectangle((col, 9 - fila), 0.86, 0.86, color=c, linewidth=0, joinstyle="round"))
    ax.set_xlim(-0.1, 10)
    ax.set_ylim(-1.6, 10)
    ax.set_aspect("equal")
    apa.leyenda_marcador(ax, [(f"Pobreza extrema: {extrema:.1f} %", apa.NARANJA),
                              (f"Pobreza no extrema: {total - extrema:.1f} %", apa.AZUL),
                              (f"No pobres: {100 - total:.1f} %", "#d6d5cd")],
                         loc="lower left", bbox_to_anchor=(0, -0.02), ncol=1)
    archivo = f"waffle_pobreza_{a.anio}.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, f"De cada 100 peruanos en {a.anio}, {n_pob} eran pobres", archivo,
         f"Cada cuadro representa 1 % de la población. Pobreza monetaria {total:.2f} % y extrema {extrema:.2f} % "
         f"(redondeadas a cuadros enteros). Fuente: INEI, ENAHO {a.anio}.", None)


# -------------------------------------------------------------------------------------------------- macro
def macro(a):
    """Dos paneles alineados en el tiempo (nunca doble eje): inflación (BCRP) y pobreza (ENAHO)."""
    s = _serie()
    pob = s[(s.indicador == "pobreza_monetaria") & (s.desagregacion == "nacional")].sort_values("anio")
    b = pd.read_csv(RAIZ / a.bcrp, dtype={"periodo": str})
    cod = b.codigo.iloc[0]
    b = b[b.codigo == cod].copy()
    b["fecha"] = pd.to_datetime(b.periodo + "-01")
    apa.aplicar_estilo()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
    ax1.axhspan(1, 3, color=apa.AGUA, alpha=0.12, linewidth=0)
    ax1.text(pd.Timestamp(b.fecha.min()), 3.05, "Rango meta del BCRP (1 %-3 %)", fontsize=8.8,
             color=apa.TINTA_2, va="bottom")
    ax1.plot(b.fecha, b.valor, color=apa.AZUL, linewidth=1.9)
    pico = b.loc[b.valor.idxmax()]
    ax1.scatter(pico.fecha, pico.valor, s=40, color=apa.AZUL, edgecolor=apa.SUPERFICIE, zorder=3)
    ax1.annotate(f"Máximo: {pico.valor:.2f} % ({pico.periodo})", (pico.fecha, pico.valor), xytext=(10, -4),
                 textcoords="offset points", fontsize=9, color=apa.TINTA)
    ult = b.iloc[-1]
    apa.etiqueta_directa(ax1, ult.fecha, ult.valor, f"{ult.valor:.2f} % ({ult.periodo})")
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax1.set_ylabel("Inflación a 12 meses")
    ax1.set_title(f"A. Inflación de Lima Metropolitana (BCRP, {cod}), mensual", fontsize=10.5)
    x = pd.to_datetime(pob.anio.astype(str) + "-07-01")
    ax2.fill_between(x, pob.ic95_inf, pob.ic95_sup, color=apa.NARANJA, alpha=0.15, linewidth=0)
    ax2.plot(x, pob.valor_pct, color=apa.NARANJA, linewidth=1.9)
    ax2.scatter(x, pob.valor_pct, s=30, color=apa.NARANJA, edgecolor=apa.SUPERFICIE, zorder=3)
    for xi, v in zip(x, pob.valor_pct):
        ax2.annotate(f"{v:.1f}", (xi, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8.8,
                     color=apa.TINTA_2)
    ax2.set_ylim(0, pob.ic95_sup.max() + 6)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax2.set_ylabel("Pobreza monetaria")
    ax2.set_title("B. Pobreza monetaria nacional (INEI, ENAHO), anual, con IC 95 %", fontsize=10.5)
    archivo = "macro_inflacion_pobreza.png"
    apa.guardar(fig, FIG / archivo)
    _pie(a.numero, "Inflación mensual y pobreza monetaria anual en el Perú", archivo,
         f"Panel A: variación del IPC de Lima Metropolitana a 12 meses (BCRP, serie {cod}). Panel B: pobreza "
         "monetaria nacional; los puntos se ubican a mitad de año. Paneles separados con escalas propias; la "
         "coincidencia temporal es descriptiva y no implica causalidad. Fuentes: BCRP (2026) e INEI, ENAHO.", None)


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for nombre, f in [("evolucion", evolucion), ("calor", calor), ("pendiente", pendiente),
                      ("distribucion", distribucion), ("perfil", perfil), ("waffle", waffle), ("macro", macro)]:
        p = sp.add_parser(nombre)
        p.add_argument("--numero", default="1")
        p.add_argument("--indicador", default="pobreza_monetaria")
        p.add_argument("--desde", type=int, default=2019)
        p.add_argument("--hasta", type=int, default=2025)
        p.add_argument("--anio", type=int, default=2025)
        p.add_argument("--indicadores", nargs="*", default=[
            "agua_red_publica", "desague_red_publica", "afiliacion_essalud", "afiliacion_sis",
            "secundaria_completa_25mas", "tasa_ocupacion_14mas"])
        p.add_argument("--bcrp", default="tablas/bcrp_inflacion.csv")
        p.add_argument("--encabezado", action="store_true")
        p.set_defaults(f=f)
    a = ap.parse_args()
    apa.ENCABEZADO = a.encabezado
    a.f(a)


if __name__ == "__main__":
    main()
