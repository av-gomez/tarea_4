"""Estilo APA 7 compartido por todo el sistema (Skills de ENAHO, servidor MCP del BCRP e informe).

Una sola fuente de verdad para tipografía, colores, numeración y notas, de modo que cada figura,
mapa y tabla producida por cualquier componente tenga la misma presentación:

- Tipografía Times New Roman (serif de respaldo si no está instalada).
- Figuras: número en negrita ("Figura 1"), título en cursiva debajo y nota al pie que empieza con
  "Nota." en cursiva, con la fuente de los datos (APA 7, secc. 7.4).
- Tablas: solo líneas horizontales (encabezado y cierre), número en negrita y título en cursiva.
- Colores de un solo tono (legibles en escala de grises), sin arcoíris.
"""
from __future__ import annotations

import html
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FUENTE = "Times New Roman"
AZUL = "#1f4e79"
AZUL_CLARO = "#9dc3e6"
GRIS = "#595959"
GRIS_CLARO = "#bfbfbf"
PALETA = [AZUL, "#7f7f7f", AZUL_CLARO, "#262626", "#c9c9c9"]
CMAP = "Blues"
DPI = 200

FUENTE_ENAHO = "Instituto Nacional de Estadística e Informática [INEI] (2025), Encuesta Nacional de Hogares 2024"
FUENTE_BCRP = "Banco Central de Reserva del Perú [BCRP] (2026), Series estadísticas"

REFERENCIAS_APA = {
    "enaho": ("Instituto Nacional de Estadística e Informática. (2025). *Encuesta Nacional de Hogares sobre "
              "Condiciones de Vida y Pobreza 2024* [Base de datos: módulos 02 y 34]. "
              "https://proyectos.inei.gob.pe/microdatos/"),
    "bcrp": ("Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos]. "
             "https://estadisticas.bcrp.gob.pe/estadisticas/series/"),
    "geo": ("D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub. "
            "https://github.com/d2cml-ai/Data-Science-Python"),
    "pobreza_inei": ("Instituto Nacional de Estadística e Informática. (2025). *Perú: Evolución de la pobreza "
                     "monetaria 2015-2024. Informe técnico*. INEI."),
}


def aplicar_estilo() -> None:
    """Configura matplotlib con la tipografía y la gráfica sobria que pide APA 7."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": [FUENTE, "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#404040",
        "axes.linewidth": 0.8,
        "axes.grid": False,
        "axes.prop_cycle": matplotlib.cycler(color=PALETA),
        "figure.dpi": 100,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
    })


def encabezar(fig, numero: int | str, titulo: str, nota: str, ancho_nota: int = 120,
              arriba: float = 0.84, abajo: float = 0.2, izquierda: float | None = None) -> None:
    """Número (negrita) y título (cursiva) arriba; nota APA abajo. Reserva márgenes para que no se solapen."""
    ajustes = {"top": arriba, "bottom": abajo}
    if izquierda is not None:
        ajustes["left"] = izquierda
    fig.subplots_adjust(**ajustes)
    alto = fig.get_size_inches()[1]
    fig.text(0.02, 1 - 0.12 / alto, f"Figura {numero}", fontweight="bold", fontsize=12, ha="left", va="top")
    fig.text(0.02, 1 - 0.42 / alto, titulo, fontstyle="italic", fontsize=12, ha="left", va="top")
    lineas = textwrap.wrap("Nota. " + nota.replace("$", r"\$"), ancho_nota)
    lineas[0] = lineas[0].replace("Nota.", r"$\it{Nota.}$", 1)
    fig.text(0.02, 0.1 / alto, "\n".join(lineas), fontsize=9, ha="left", va="bottom", color="#262626")


def guardar(fig, ruta: str | Path) -> Path:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=DPI, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return ruta


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


CSS_APA = """
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.6; color: #111;
       background: #fff; max-width: 980px; margin: 0 auto; padding: 24px 16px; }
h1 { font-size: 16pt; text-align: center; font-weight: bold; }
h2 { font-size: 13pt; font-weight: bold; text-align: center; margin-top: 2em; }
h3 { font-size: 12pt; font-weight: bold; text-align: left; }
table.apa { border-collapse: collapse; margin: 0.5em 0 0.3em; width: 100%; font-size: 11pt; }
table.apa thead th { border-top: 1.5px solid #000; border-bottom: 1px solid #000; padding: 4px 8px;
       text-align: center; font-weight: normal; }
table.apa td { padding: 3px 8px; text-align: right; }
table.apa td:first-child, table.apa th:first-child { text-align: left; }
table.apa tbody tr:last-child td { border-bottom: 1.5px solid #000; }
.apa-num { font-weight: bold; margin: 1.4em 0 0; }
.apa-tit { font-style: italic; margin: 0 0 0.4em; }
.apa-nota { font-size: 10.5pt; margin-top: 0.2em; }
figure { margin: 1.5em 0; } figure img { max-width: 100%; height: auto; }
.referencias p { padding-left: 2em; text-indent: -2em; margin: 0.3em 0; }
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
            f'<table class="apa"><thead><tr>{cab}</tr></thead><tbody>{"".join(cuerpo)}</tbody></table>'
            f'<p class="apa-nota"><em>Nota.</em> {html.escape(nota)}</p>')
