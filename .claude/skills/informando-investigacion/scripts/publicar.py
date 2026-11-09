"""Publica el informe en HTML (APA 7, Times New Roman) y construye el tablero interactivo de resultados.

    uv run .claude/skills/informando-investigacion/scripts/publicar.py
    uv run .claude/skills/informando-investigacion/scripts/publicar.py --informe informes/informe_final.md

Salidas:
  informes/informe_final.html  el informe Markdown convertido a HTML con estilo APA 7 (figuras incrustadas,
                               tablas con reglas horizontales, referencias con sangría francesa).
  informes/dashboard.html      tablero Plotly: indicadores clave, mapa interactivo, pobreza por grupos con IC 95 %,
                               series del BCRP guardadas en tablas/bcrp_*.csv y tabla de validación.
Ambos archivos son autónomos (las imágenes se incrustan en base64) para revisarlos sin el repositorio.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import markdown
import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(RAIZ))
from comun import apa  # noqa: E402

FUENTE_CSS = "font-family: 'Times New Roman', Times, serif;"


def _incrustar(html: str, base: Path) -> str:
    def rep(m):
        src = m.group(1)
        p = (base / src).resolve()
        if p.exists() and p.suffix.lower() in (".png", ".jpg", ".jpeg"):
            b64 = base64.b64encode(p.read_bytes()).decode()
            return f'src="data:image/png;base64,{b64}"'
        return m.group(0)
    return re.sub(r'src="([^"]+)"', rep, html)


def informe_html(md_path: Path) -> Path:
    texto = md_path.read_text(encoding="utf-8")
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
    cuerpo = cuerpo.replace("<table>", '<table class="apa">')
    cuerpo = _incrustar(cuerpo, md_path.parent)
    titulo = re.search(r"^#\s+(.+)$", texto, re.M)
    titulo = titulo.group(1) if titulo else "Informe"
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{titulo}</title>
<style>{apa.CSS_APA}
code {{ font-size: 10.5pt; background: #f4f4f4; padding: 0 3px; }}
pre {{ background: #f4f4f4; padding: 8px; overflow-x: auto; }}
blockquote {{ margin-left: 2em; }}
</style></head><body>{cuerpo}
<hr><p class="apa-nota">Documento generado el {datetime.now():%Y-%m-%d %H:%M} desde {md_path.name} con
publicar.py.</p></body></html>"""
    salida = md_path.with_suffix(".html")
    salida.write_text(html, encoding="utf-8")
    return salida


def dashboard() -> Path:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots  # noqa: F401

    ind = pd.read_csv(RAIZ / "salidas" / "indicadores.csv", dtype={"codigo": str})
    pm = ind[ind.indicador == "pobreza_monetaria"]
    nac = pm[pm.desagregacion == "nacional"].iloc[0]
    area = pm[pm.desagregacion == "area"].set_index("categoria")
    ext = ind[(ind.indicador == "pobreza_extrema") & (ind.desagregacion == "nacional")].iloc[0]
    fuente_layout = {"family": apa.FUENTE_CSS, "size": 14, "color": apa.TINTA}
    rampa = ["#eef5fd", *apa.RAMPA_AZUL]
    escala = [[i / (len(rampa) - 1), c] for i, c in enumerate(rampa)]
    base_layout = {"font": fuente_layout, "paper_bgcolor": apa.SUPERFICIE, "plot_bgcolor": apa.SUPERFICIE,
                   "colorway": apa.CATEGORICA, "hoverlabel": {"font": {"family": apa.FUENTE_CSS}}}
    figs = []

    geo = json.loads((RAIZ / "datos" / "peru_departamental_simple.geojson").read_text(encoding="utf-8"))
    dep = pm[pm.desagregacion == "departamento"].copy()
    m = go.Figure(go.Choropleth(geojson=geo, featureidkey="properties.FIRST_IDDP", locations=dep.codigo,
                                z=dep.valor_pct, zmin=0, zmax=50, colorscale=escala, marker_line_color=apa.SUPERFICIE,
                                text=dep.categoria, colorbar={"title": "% de personas"},
                                customdata=dep[["ic95_inf", "ic95_sup", "cv_pct"]].values,
                                hovertemplate="<b>%{text}</b><br>Pobreza: %{z:.1f} %<br>IC 95 %: "
                                              "%{customdata[0]:.1f}–%{customdata[1]:.1f}<br>CV: "
                                              "%{customdata[2]:.1f} %<extra></extra>"))
    m.update_geos(fitbounds="locations", visible=False)
    m.update_layout(title="Pobreza monetaria por departamento, 2024 (% de personas)", font=fuente_layout,
                    height=620, margin={"l": 0, "r": 0, "t": 50, "b": 0})
    figs.append(("mapa", m))
    figs += multianual(geo, escala, base_layout)

    d = dep.sort_values("valor_pct")
    b = go.Figure(go.Bar(x=d.valor_pct, y=d.categoria, orientation="h", marker_color=apa.AZUL,
                         error_x={"type": "data", "symmetric": False, "array": d.ic95_sup - d.valor_pct,
                                  "arrayminus": d.valor_pct - d.ic95_inf, "color": "#404040"},
                         hovertemplate="%{y}: %{x:.1f} %<extra></extra>"))
    b.add_vline(x=nac.valor_pct, line_dash="dash", line_color=apa.GRIS,
                annotation_text=f"Perú {nac.valor_pct:.1f} %")
    b.update_layout(title="Ranking departamental con IC 95 %", font=fuente_layout, height=700,
                    xaxis_title="% de personas en pobreza", plot_bgcolor="white", margin={"l": 120})
    figs.append(("ranking", b))

    grupos = []
    for desag, etiqueta in [("area", "Área"), ("region_natural", "Región natural"), ("sexo", "Sexo"),
                            ("grupo_edad", "Edad"), ("sexo_jefe", "Jefatura del hogar")]:
        g = pm[pm.desagregacion == desag]
        grupos.append(go.Bar(name=etiqueta, x=[f"{etiqueta}: {c}" for c in g.categoria], y=g.valor_pct,
                             error_y={"type": "data", "symmetric": False, "array": g.ic95_sup - g.valor_pct,
                                      "arrayminus": g.valor_pct - g.ic95_inf}))
    gfig = go.Figure(grupos)
    gfig.update_layout(title="Pobreza monetaria por grupos de población, 2024", font=fuente_layout, height=480,
                       yaxis_title="% de personas", plot_bgcolor="white", showlegend=False,
                       colorway=apa.PALETA)
    figs.append(("grupos", gfig))

    for csv in sorted((RAIZ / "tablas").glob("bcrp_*.csv")):
        t = pd.read_csv(csv, dtype={"periodo": str})
        f = go.Figure()
        for (cod, nom), s in t.groupby(["codigo", "nombre"], sort=False):
            x = pd.to_datetime(s.periodo + ("-01" if len(s.periodo.iloc[0]) == 7 else ""), errors="coerce")
            f.add_trace(go.Scatter(x=x, y=s.valor, mode="lines", name=f"{nom} ({cod})"))
        f.update_layout(title=f"BCRP: {', '.join(t.codigo.unique())}", font=fuente_layout, height=420,
                        plot_bgcolor="white", legend={"orientation": "h", "y": -0.2}, colorway=apa.PALETA)
        figs.append((csv.stem, f))

    val = (RAIZ / "salidas" / "validacion.txt").read_text(encoding="utf-8")
    tarjetas = [("Pobreza monetaria nacional", f"{nac.valor_pct:.1f} %",
                 f"IC 95 %: {nac.ic95_inf:.1f}–{nac.ic95_sup:.1f}"),
                ("Pobreza urbana", f"{area.loc['Urbana'].valor_pct:.1f} %", "estrato 1–5"),
                ("Pobreza rural", f"{area.loc['Rural'].valor_pct:.1f} %", "estrato 6–8"),
                ("Pobreza extrema", f"{ext.valor_pct:.1f} %", f"IC 95 %: {ext.ic95_inf:.1f}–{ext.ic95_sup:.1f}"),
                ("Departamentos", "25 / 25", "unión por ubigeo y FIRST_IDDP")]
    html_t = "".join(f'<div class="kpi"><div class="k">{a}</div><div class="v">{b}</div><div class="s">{c}</div>'
                     f'</div>' for a, b, c in tarjetas)
    graficos = "".join(f'<section class="panel">{f.to_html(full_html=False, include_plotlyjs=False)}</section>'
                       for _, f in figs)
    tabla_dep = apa.tabla_html(dep.sort_values("valor_pct", ascending=False)[
        ["categoria", "valor_pct", "ic95_inf", "ic95_sup", "cv_pct", "n_muestral"]].rename(columns={
            "categoria": "Departamento", "valor_pct": "Pobreza (%)", "ic95_inf": "IC 95 % inf.",
            "ic95_sup": "IC 95 % sup.", "cv_pct": "CV (%)", "n_muestral": "Hogares en muestra"}),
        1, "Pobreza monetaria por departamento, Perú 2024",
        "Estimaciones ponderadas con factor07 × mieperho; IC por linealización de Taylor. Fuente: "
        + apa.FUENTE_ENAHO + ".")
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Tablero socioeconómico del Perú</title>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"></script>
<style>{apa.CSS_APA}
body {{ max-width: 1200px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 1em 0; }}
.kpi {{ border-top: 2px solid #1f4e79; padding: 8px 4px; }}
.kpi .k {{ font-size: 11pt; color: #404040; }} .kpi .v {{ font-size: 24pt; font-weight: bold; color: #1f4e79; }}
.kpi .s {{ font-size: 10pt; color: #595959; }}
.panel {{ margin: 1.5em 0; border-bottom: 1px solid #ddd; }}
pre {{ font-size: 10pt; background: #f7f7f7; padding: 10px; overflow-x: auto; }}
</style></head><body>
<h1>Tablero socioeconómico del Perú: pobreza monetaria (ENAHO 2019-2025) y entorno macroeconómico (BCRP)</h1>
<p style="text-align:center">Generado el {datetime.now():%Y-%m-%d %H:%M} con
<code>.claude/skills/informando-investigacion/scripts/publicar.py</code>. Todas las cifras provienen de
<code>salidas/indicadores.csv</code> y de las tablas <code>tablas/bcrp_*.csv</code>.</p>
<div class="kpis">{html_t}</div>
{graficos}
<section class="panel">{tabla_dep}</section>
<h2>Validación del procesamiento</h2><pre>{val}</pre>
<h2>Referencias</h2><div class="referencias">{''.join(f'<p>{markdown.markdown(r)[3:-4]}</p>'
                                                      for r in apa.REFERENCIAS_APA.values())}</div>
</body></html>"""
    salida = RAIZ / "informes" / "dashboard.html"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    return salida


def multianual(geo, escala, base_layout):
    """Figuras interactivas de la serie 2019-2025 (si existe salidas/serie_indicadores.csv)."""
    import plotly.graph_objects as go

    ruta = RAIZ / "salidas" / "serie_indicadores.csv"
    if not ruta.exists():
        return []
    s = pd.read_csv(ruta, dtype={"codigo": str})
    pm = s[s.indicador == "pobreza_monetaria"]
    figs = []
    t = go.Figure()
    for nombre, filtro, color in [("Rural", (pm.desagregacion == "area") & (pm.categoria == "Rural"), apa.NARANJA),
                                  ("Perú", pm.desagregacion == "nacional", apa.AZUL),
                                  ("Urbana", (pm.desagregacion == "area") & (pm.categoria == "Urbana"), apa.AGUA)]:
        g = pm[filtro].sort_values("anio")
        t.add_trace(go.Scatter(x=list(g.anio) + list(g.anio[::-1]), y=list(g.ic95_sup) + list(g.ic95_inf[::-1]),
                               fill="toself", fillcolor=color, opacity=0.15, line={"width": 0}, hoverinfo="skip",
                               showlegend=False))
        t.add_trace(go.Scatter(x=g.anio, y=g.valor_pct, mode="lines+markers", name=nombre,
                               line={"color": color, "width": 2.5}, marker={"size": 8},
                               customdata=g[["ic95_inf", "ic95_sup"]].values,
                               hovertemplate=f"<b>{nombre}</b> %{{x}}: %{{y:.1f}} %<br>IC 95 %: "
                                             "%{customdata[0]:.1f}–%{customdata[1]:.1f}<extra></extra>"))
    t.update_layout(**base_layout, title="Pobreza monetaria 2019-2025 por área (IC 95 %)", height=460,
                    yaxis={"title": "% de personas", "rangemode": "tozero", "gridcolor": apa.REJILLA},
                    xaxis={"dtick": 1}, hovermode="x unified")
    figs.append(("tendencia", t))
    dep = pm[pm.desagregacion == "departamento"].sort_values(["anio", "codigo"])
    anios = sorted(dep.anio.unique())

    def capa(anio):
        g = dep[dep.anio == anio]
        return go.Choropleth(geojson=geo, featureidkey="properties.FIRST_IDDP", locations=g.codigo, z=g.valor_pct,
                             zmin=0, zmax=50, colorscale=escala, marker_line_color=apa.SUPERFICIE, text=g.categoria,
                             colorbar={"title": "%"},
                             hovertemplate="<b>%{text}</b><br>%{z:.1f} %<extra>" + str(anio) + "</extra>")

    mapa = go.Figure(data=[capa(anios[-1])], frames=[go.Frame(data=[capa(a)], name=str(a)) for a in anios])
    mapa.update_geos(fitbounds="locations", visible=False)
    mapa.update_layout(**base_layout, title="Pobreza por departamento: mueve el selector de año", height=650,
                       margin={"l": 0, "r": 0, "t": 50, "b": 0},
                       sliders=[{"active": len(anios) - 1, "currentvalue": {"prefix": "Año: "},
                                 "steps": [{"label": str(a), "method": "animate",
                                            "args": [[str(a)], {"mode": "immediate", "frame": {"duration": 0}}]}
                                           for a in anios]}])
    figs.append(("mapa_anual", mapa))
    return figs


def portal() -> Path:
    """Página índice que reúne informe, tablero, figuras, mapas, tablas y validaciones."""
    def lista(carpeta, patron):
        return sorted((RAIZ / carpeta).glob(patron))
    tarjetas = []
    for img in [*lista("figuras", "*.png"), *lista("mapas", "*.png")]:
        rel = f"../{img.parent.name}/{img.name}"
        tarjetas.append(f'<a class="tarjeta" href="{rel}"><img src="{rel}" loading="lazy" alt="{img.stem}">'
                        f'<span>{img.parent.name}/{img.name}</span></a>')
    validaciones = "".join(f'<li><a href="../salidas/{p.name}">{p.name}</a></li>'
                           for p in lista("salidas", "validacion*.txt"))
    tablas = "".join(f'<li><a href="../tablas/{p.name}">{p.name}</a></li>' for p in lista("tablas", "*.csv"))
    css = apa.CSS_APA + """
.botones { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:1.2em 0; }
.boton { display:block; padding:16px; border-radius:10px; background:var(--surface); text-decoration:none;
         border:1px solid var(--grid); color:var(--ink); }
.boton b { display:block; font-size:1.05rem; color:var(--s1); }
.galeria { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:14px; }
.tarjeta { display:block; background:var(--surface); border:1px solid var(--grid); border-radius:10px; padding:8px;
           text-decoration:none; color:var(--ink2); font-size:0.8rem; }
.tarjeta img { width:100%; height:160px; object-fit:contain; background:#fcfcfb; }
"""
    html_ = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Portal de resultados</title>
<style>{css}</style></head><body>
<h1>Agente de investigación socioeconómica del Perú</h1>
<p class="lead">Portal de resultados: BCRP (servidor MCP) y ENAHO 2019-2025 del INEI (Skills de Claude Code).</p>
<div class="botones">
<a class="boton" href="informe_final.html"><b>Informe final</b>Investigación en formato APA 7</a>
<a class="boton" href="dashboard.html"><b>Tablero interactivo</b>Mapas por año, tendencias y tablas</a>
<a class="boton" href="verificacion.md"><b>Verificación de cifras</b>Control independiente</a>
<a class="boton" href="../evaluacion/comparacion.md"><b>Evaluación del agente</b>Con y sin MCP y Skills</a>
</div>
<h2>Figuras y mapas</h2><div class="galeria">{''.join(tarjetas)}</div>
<h2>Validaciones</h2><ul>{validaciones}</ul>
<h2>Tablas de datos</h2><ul>{tablas}</ul>
</body></html>"""
    destino = RAIZ / "informes" / "index.html"
    destino.write_text(html_, encoding="utf-8")
    return destino


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--informe", default=str(RAIZ / "informes" / "informe_final.md"))
    ap.add_argument("--sin-dashboard", action="store_true")
    a = ap.parse_args()
    md = Path(a.informe)
    if md.exists():
        print(f"Informe HTML: {informe_html(md).relative_to(RAIZ)}")
    else:
        print(f"Aviso: no existe {md}; solo se construye el tablero.")
    if not a.sin_dashboard:
        print(f"Tablero: {dashboard().relative_to(RAIZ)}")
    print(f"Portal: {portal().relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
