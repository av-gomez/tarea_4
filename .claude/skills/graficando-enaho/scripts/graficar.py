"""Gráficos APA 7 de pobreza monetaria con la ENAHO 2024 (estimaciones ponderadas con IC 95 %).

    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento --numero 3
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo todos

Tipos: area, sexo, edad, sexo_jefe, region, dominio, departamento, extrema, todos.

Lee salidas/indicadores.csv (producido por la skill limpiando-enaho con factores de expansión y error de
muestreo). Si no existe, sale con código 2 y pide ejecutar primero limpiando-enaho. Cada figura se guarda en
figuras/ (PNG a 200 dpi) junto con su tabla de datos en tablas/ (CSV) para que toda cifra sea rastreable.
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

import matplotlib.pyplot as plt  # noqa: E402

INDICADORES = RAIZ / "salidas" / "indicadores.csv"
NOTA_BASE = ("Estimaciones ponderadas con factores de expansión ({pond}); las barras de error son intervalos de "
             "confianza al 95 % por linealización de Taylor (conglomerados y estratos de diseño). Pobreza "
             "monetaria: gasto per cápita del hogar menor que la línea de pobreza. Fuente: " + apa.FUENTE_ENAHO + ".")
CONFIG = {
    "area": ("pobreza_monetaria", "area", "Pobreza monetaria por área de residencia, Perú 2024",
             "pobreza_area.png", ["Urbana", "Rural"]),
    "sexo": ("pobreza_monetaria", "sexo", "Pobreza monetaria por sexo, Perú 2024", "pobreza_sexo.png",
             ["Hombre", "Mujer"]),
    "edad": ("pobreza_monetaria", "grupo_edad", "Pobreza monetaria por grupo de edad, Perú 2024",
             "pobreza_edad.png", ["0-13", "14-17", "18-29", "30-44", "45-59", "60 y más"]),
    "sexo_jefe": ("pobreza_monetaria", "sexo_jefe", "Pobreza monetaria según sexo de la jefatura del hogar, "
                  "Perú 2024", "pobreza_sexo_jefe.png", ["Hombre", "Mujer"]),
    "region": ("pobreza_monetaria", "region_natural", "Pobreza monetaria por región natural, Perú 2024",
               "pobreza_region_natural.png", ["Costa", "Sierra", "Selva"]),
    "dominio": ("pobreza_monetaria", "dominio_nombre", "Pobreza monetaria por dominio geográfico, Perú 2024",
                "pobreza_dominio.png", None),
    "departamento": ("pobreza_monetaria", "departamento", "Pobreza monetaria por departamento, Perú 2024",
                     "pobreza_departamento.png", None),
    "extrema": ("pobreza_extrema", "area", "Pobreza extrema por área de residencia, Perú 2024",
                "pobreza_extrema_area.png", ["Urbana", "Rural"]),
}


def cargar() -> pd.DataFrame:
    if not INDICADORES.exists():
        print("ERROR: no existe salidas/indicadores.csv. Ejecuta primero la skill limpiando-enaho:\n"
              "  uv run .claude/skills/limpiando-enaho/scripts/limpiar.py", file=sys.stderr)
        sys.exit(2)
    return pd.read_csv(INDICADORES, dtype={"codigo": str})


def _nacional(ind: pd.DataFrame, indicador: str) -> float:
    return float(ind.query("indicador == @indicador and desagregacion == 'nacional'").valor_pct.iloc[0])


def graficar(tipo: str, numero: int, ind: pd.DataFrame) -> dict:
    indicador, desag, titulo, archivo, orden = CONFIG[tipo]
    d = ind.query("indicador == @indicador and desagregacion == @desag").copy()
    if d.empty:
        raise SystemExit(f"ERROR: no hay datos para {indicador} por {desag} en indicadores.csv")
    nac = _nacional(ind, indicador)
    horizontal = tipo in ("departamento", "dominio")
    if orden:
        d["categoria"] = pd.Categorical(d.categoria, orden, ordered=True)
        d = d.sort_values("categoria")
    else:
        d = d.sort_values("valor_pct", ascending=horizontal)
    d["categoria"] = d.categoria.astype(str)
    pond = d.ponderador.iloc[0].replace("*", " × ")
    err = [d.valor_pct - d.ic95_inf, d.ic95_sup - d.valor_pct]

    apa.aplicar_estilo()
    if horizontal:
        alto = 0.28 * len(d) + 2.2
        fig, ax = plt.subplots(figsize=(7.5, alto))
        colores = [apa.AZUL if v > nac else apa.AZUL_CLARO for v in d.valor_pct]
        ax.barh(d.categoria, d.valor_pct, xerr=err, color=colores, edgecolor="none", height=0.7,
                error_kw={"elinewidth": 0.8, "ecolor": "#404040", "capsize": 2})
        for y, (v, s) in enumerate(zip(d.valor_pct, d.ic95_sup)):
            ax.text(s + 0.6, y, f"{v:.1f}", va="center", fontsize=9)
        ax.axvline(nac, color=apa.GRIS, linestyle="--", linewidth=1)
        ax.text(nac, len(d) - 0.3, f" Perú: {nac:.1f} %", fontsize=9, color=apa.GRIS, va="bottom")
        ax.set_xlabel("Porcentaje de la población en situación de pobreza (%)")
        ax.set_xlim(0, max(d.ic95_sup) * 1.12)
        ax.tick_params(axis="y", length=0)
        extra = (" Las barras oscuras superan el promedio nacional; las claras están por debajo. Lima incluye "
                 "Lima Metropolitana y Lima provincias; Callao se presenta por separado.") if tipo == "departamento" else ""
        apa.encabezar(fig, numero, titulo, NOTA_BASE.format(pond=pond) + extra, ancho_nota=105,
                      arriba=1 - 0.95 / alto, abajo=2.0 / alto, izquierda=0.2)
    else:
        fig, ax = plt.subplots(figsize=(7, 4.8))
        x = range(len(d))
        ax.bar(x, d.valor_pct, yerr=err, color=apa.AZUL, width=0.6,
               error_kw={"elinewidth": 0.9, "ecolor": "#404040", "capsize": 4})
        for i, (v, s) in enumerate(zip(d.valor_pct, d.ic95_sup)):
            ax.text(i, v - 1.0, f"{v:.1f} %", ha="center", va="top", fontsize=10, color="white",
                    fontweight="bold")
        ax.axhline(nac, color=apa.GRIS, linestyle="--", linewidth=1, label=f"Promedio nacional: {nac:.1f} %")
        ax.legend(loc="upper right", fontsize=9)
        ax.set_xticks(list(x), d.categoria)
        ax.set_ylabel("Porcentaje de la población (%)")
        ax.set_ylim(0, max(d.ic95_sup) * 1.18)
        etiqueta_x = {"area": "Área de residencia", "sexo": "Sexo", "grupo_edad": "Grupo de edad (años)",
                      "sexo_jefe": "Sexo de la jefatura del hogar", "region_natural": "Región natural"}
        ax.set_xlabel(etiqueta_x.get(desag, ""))
        apa.encabezar(fig, numero, titulo, NOTA_BASE.format(pond=pond), ancho_nota=100, abajo=0.24)
    ruta = apa.guardar(fig, RAIZ / "figuras" / archivo)
    tabla = d[["categoria", "valor_pct", "ee_pct", "ic95_inf", "ic95_sup", "cv_pct", "n_muestral",
               "poblacion_expandida"]]
    (RAIZ / "tablas").mkdir(exist_ok=True)
    tabla.to_csv(RAIZ / "tablas" / archivo.replace(".png", ".csv"), index=False, encoding="utf-8")
    print(f"Figura {numero}: {ruta.relative_to(RAIZ)}  |  tabla: tablas/{archivo.replace('.png', '.csv')}")
    print(tabla.round(2).to_string(index=False))
    return {"tipo": tipo, "archivo": str(ruta.relative_to(RAIZ))}


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tipo", default="todos", choices=[*CONFIG, "todos"])
    ap.add_argument("--numero", type=int, default=1, help="número APA de la (primera) figura")
    a = ap.parse_args()
    ind = cargar()
    tipos = list(CONFIG) if a.tipo == "todos" else [a.tipo]
    for i, t in enumerate(tipos):
        graficar(t, a.numero + i, ind)


if __name__ == "__main__":
    main()
