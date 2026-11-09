"""Sistema visual único del proyecto (Skills de ENAHO, servidor MCP del BCRP, informes y tablero).

Una sola fuente de verdad para tipografía, colores, marcas y tablas, de modo que cada figura, mapa y tabla
tenga la misma apariencia, sin importar qué componente la produjo.

Tipografía: la sans del sistema (Segoe UI / system-ui), la misma con la que GitHub y los navegadores
muestran el Markdown y el HTML del proyecto; así el texto de las figuras coincide con el del informe.

Paleta (validada con el validador de daltonismo de la skill dataviz, modo claro, todos los pares):
  - Categórica, en orden fijo: azul #2a78d6, naranja #eb6834, aguamarina #1baf7a (máximo tres series).
  - Secuencial (magnitud, p. ej. tasa de pobreza): un solo tono azul, de claro a oscuro.
  - Divergente (cambio): azul (baja) <-> rojo (sube), con gris neutro en el centro.
Formato APA 7: el número ("Figura n", en negrita), el título (en cursiva) y la nota ("Nota." con la fuente)
van en el Markdown o HTML, con la misma tipografía; las imágenes quedan limpias. Con ENCABEZADO = True (o
--encabezado en los scripts) se incrustan en la imagen para usarla sola.
"""
from __future__ import annotations

import html
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap  # noqa: E402

ENCABEZADO = False

# --- tipografía ------------------------------------------------------------------------------------------
FUENTES = ["Segoe UI", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
FUENTE_CSS = 'system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
FUENTE = FUENTES[0]

# --- tinta y superficies -----------------------------------------------------------------------------------
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_3 = "#898781"
REJILLA = "#e1e0d9"
EJE = "#c3c2b7"

# --- categórica (orden fijo) ------------------------------------------------------------------------------
AZUL, NARANJA, AGUA = "#2a78d6", "#eb6834", "#1baf7a"
CATEGORICA = [AZUL, NARANJA, AGUA]
GRIS_NEUTRO = "#b9b8b1"           # contexto / "resto" (no es una serie)

# --- secuencial azul (100 -> 700) y divergente ------------------------------------------------------------
RAMPA_AZUL = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
              "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("pobreza", ["#eef5fd", *RAMPA_AZUL])
CMAP_DIVERGENTE = LinearSegmentedColormap.from_list(
    "cambio", ["#104281", "#3987e5", "#9ec5f4", "#f0efec", "#f4a7a6", "#e34948", "#9e2a2a"])

# Compatibilidad con nombres anteriores
AZUL_CLARO, GRIS, GRIS_CLARO = "#9ec5f4", TINTA_2, GRIS_NEUTRO
PALETA = CATEGORICA
DPI = 200

FUENTE_ENAHO = "Instituto Nacional de Estadística e Informática [INEI], Encuesta Nacional de Hogares"
FUENTE_BCRP = "Banco Central de Reserva del Perú [BCRP] (2026), Series estadísticas"

REFERENCIAS_APA = {
    "enaho": ("Instituto Nacional de Estadística e Informática. (2020-2026). *Encuesta Nacional de Hogares sobre "
              "Condiciones de Vida y Pobreza, 2019-2025* [Bases de datos]. "
              "https://proyectos.inei.gob.pe/microdatos/"),
    "bcrp": ("Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos]. "
             "https://estadisticas.bcrp.gob.pe/estadisticas/series/"),
    "geo": ("D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub. "
            "https://github.com/d2cml-ai/Data-Science-Python"),
    "pobreza_inei": ("Instituto Nacional de Estadística e Informática. (2026). *Perú: Evolución de la pobreza "
                     "monetaria 2016-2025. Informe técnico*. INEI."),
}


def aplicar_estilo() -> None:
    """Configura matplotlib: sans del sistema, marcas finas, rejilla recesiva, sin marcos innecesarios."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FUENTES,
        "font.size": 10.5,
        "text.color": TINTA,
        "axes.labelcolor": TINTA_2,
        "axes.titlesize": 12,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.labelsize": 10,
        "axes.edgecolor": EJE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": REJILLA,
        "grid.linewidth": 0.7,
        "xtick.color": TINTA_3,
        "ytick.color": TINTA_3,
        "xtick.labelcolor": TINTA_2,
        "ytick.labelcolor": TINTA_2,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "ytick.major.size": 0,
        "legend.fontsize": 9.5,
        "legend.frameon": False,
        "lines.linewidth": 2.0,
        "lines.solid_capstyle": "round",
        "axes.prop_cycle": matplotlib.cycler(color=CATEGORICA),
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
    })


def encabezar(fig, numero: int | str, titulo: str, nota: str, ancho_nota: int = 120,
              arriba: float = 0.84, abajo: float = 0.2, izquierda: float | None = None) -> None:
    """Con ENCABEZADO activo escribe número, título y nota APA en la imagen; si no, solo ajusta márgenes."""
    if not ENCABEZADO:
        if izquierda is not None:
            fig.subplots_adjust(left=izquierda)
        return
    ajustes = {"top": arriba, "bottom": abajo}
    if izquierda is not None:
        ajustes["left"] = izquierda
    fig.subplots_adjust(**ajustes)
    alto = fig.get_size_inches()[1]
    fig.text(0.02, 1 - 0.12 / alto, f"Figura {numero}", fontweight="bold", fontsize=12, ha="left", va="top")
    fig.text(0.02, 1 - 0.42 / alto, titulo, fontstyle="italic", fontsize=12, ha="left", va="top")
    lineas = textwrap.wrap("Nota. " + nota.replace("$", r"\$"), ancho_nota)
    fig.text(0.02, 0.1 / alto, "\n".join(lineas), fontsize=8.5, ha="left", va="bottom", color=TINTA_2)


def guardar(fig, ruta: str | Path) -> Path:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=DPI, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return ruta


def etiqueta_directa(ax, x, y, texto, color=TINTA, **kw):
    """Etiqueta directa al final de una serie (texto en tinta, no en el color de la serie)."""
    ax.annotate(texto, (x, y), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9.5,
                color=color, **kw)


def leyenda_marcador(ax, items, **kw):
    """Leyenda con marcadores circulares (identidad nunca solo por color: siempre con texto)."""
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], marker="o", linestyle="", markersize=7, markerfacecolor=c, markeredgecolor=SUPERFICIE,
                label=t) for t, c in items]
    return ax.legend(handles=h, **kw)


def pie_figura_md(numero, titulo: str, ruta: str, nota: str) -> str:
    """Bloque APA 7 para Markdown: número en negrita, título en cursiva, imagen y nota."""
    return f"**Figura {numero}**\n\n*{titulo}*\n\n![Figura {numero}. {titulo}]({ruta})\n\n*Nota.* {nota}\n"


def tabla_markdown(df, numero: int | str, titulo: str, nota: str, decimales: int = 1) -> str:
    """Tabla APA 7 en Markdown: número en negrita, título en cursiva y nota debajo."""
    d = df.copy()
    for c in d.select_dtypes("number").columns:
        if (d[c].dropna() % 1 == 0).all() and d[c].abs().max() > 100:
            d[c] = d[c].map(lambda v: f"{v:,.0f}")
        else:
            d[c] = d[c].map(lambda v: f"{v:,.{decimales}f}")
    cab = "| " + " | ".join(map(str, d.columns)) + " |"
    sep = "|" + "|".join(":---" if i == 0 else "---:" for i in range(len(d.columns))) + "|"
    filas = ["| " + " | ".join(map(str, r)) + " |" for r in d.itertuples(index=False)]
    return "\n".join([f"**Tabla {numero}**", "", f"*{titulo}*", "", cab, sep, *filas, "", f"*Nota.* {nota}", ""])


CSS_APA = f"""
:root {{ --surface:{SUPERFICIE}; --page:#f9f9f7; --ink:{TINTA}; --ink2:{TINTA_2}; --ink3:{TINTA_3};
        --grid:{REJILLA}; --axis:{EJE}; --s1:{AZUL}; --s2:{NARANJA}; --s3:{AGUA}; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --surface:#1a1a19; --page:#0d0d0d;
        --ink:#f0efec; --ink2:#c3c2b7; --ink3:#898781; --grid:#2c2c2a; --axis:#383835; }}
  :root:not([data-theme="light"]) figure img {{ background:#fcfcfb; border-radius:8px; }} }}
:root[data-theme="dark"] {{ --surface:#1a1a19; --page:#0d0d0d; --ink:#f0efec; --ink2:#c3c2b7; --ink3:#898781;
        --grid:#2c2c2a; --axis:#383835; }}
* {{ box-sizing: border-box; }}
body {{ font-family:{FUENTE_CSS}; font-size:16px; line-height:1.6; color:var(--ink); background:var(--page);
       max-width:1040px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:2rem; line-height:1.2; letter-spacing:-0.01em; margin:0.2em 0 0.3em; }}
h2 {{ font-size:1.35rem; margin-top:2.2em; padding-top:0.6em; border-top:1px solid var(--grid); }}
h3 {{ font-size:1.08rem; margin-top:1.6em; }}
p, li {{ color:var(--ink); }} a {{ color:var(--s1); }}
.lead {{ font-size:1.12rem; color:var(--ink2); }}
table.apa {{ border-collapse:collapse; margin:0.5em 0 0.3em; width:100%; font-size:0.92rem;
            font-variant-numeric:tabular-nums; }}
table.apa thead th {{ border-top:1.5px solid var(--ink); border-bottom:1px solid var(--ink); padding:6px 10px;
            text-align:right; font-weight:600; color:var(--ink2); }}
table.apa td {{ padding:5px 10px; text-align:right; border-bottom:1px solid var(--grid); }}
table.apa td:first-child, table.apa th:first-child {{ text-align:left; }}
table.apa tbody tr:last-child td {{ border-bottom:1.5px solid var(--ink); }}
.tabla-scroll {{ overflow-x:auto; }}
.apa-num {{ font-weight:700; margin:1.6em 0 0; }}
.apa-tit {{ font-style:italic; margin:0 0 0.5em; }}
.apa-nota {{ font-size:0.86rem; color:var(--ink2); margin-top:0.3em; }}
figure {{ margin:1.6em 0; }} img {{ max-width:100%; height:auto; border-radius:6px; }}
code {{ font-size:0.88em; background:color-mix(in srgb, var(--ink) 6%, transparent); padding:1px 5px;
        border-radius:4px; }}
pre {{ background:color-mix(in srgb, var(--ink) 5%, transparent); padding:12px; border-radius:8px; overflow-x:auto; }}
blockquote {{ margin:1em 0; padding:0.6em 1em; border-left:3px solid var(--s1);
             background:color-mix(in srgb, var(--s1) 6%, transparent); border-radius:0 8px 8px 0; }}
.referencias p {{ padding-left:2em; text-indent:-2em; margin:0.4em 0; }}
"""


def tabla_html(df, numero: int | str, titulo: str, nota: str, decimales: int = 1) -> str:
    """Tabla APA 7 en HTML (solo reglas horizontales)."""
    cab = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    cuerpo = []
    for r in df.itertuples(index=False):
        celdas = []
        for v in r:
            if isinstance(v, float):
                celdas.append(f"<td>{v:,.{decimales}f}</td>")
            elif isinstance(v, int):
                celdas.append(f"<td>{v:,}</td>")
            else:
                celdas.append(f"<td>{html.escape(str(v))}</td>")
        cuerpo.append("<tr>" + "".join(celdas) + "</tr>")
    return (f'<p class="apa-num">Tabla {numero}</p><p class="apa-tit">{html.escape(titulo)}</p>'
            f'<div class="tabla-scroll"><table class="apa"><thead><tr>{cab}</tr></thead>'
            f'<tbody>{"".join(cuerpo)}</tbody></table></div>'
            f'<p class="apa-nota"><em>Nota.</em> {html.escape(nota)}</p>')
