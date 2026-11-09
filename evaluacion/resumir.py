"""Resume evaluacion/resultados.csv: tabla por modo, por tipo de pregunta y figura APA 7.

    uv run evaluacion/resumir.py
Escribe evaluacion/resumen.md (tablas que se copian en comparacion.md) y figuras/evaluacion_modos.png.
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from comun import apa  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402


def main():
    r = pd.read_csv(RAIZ / "evaluacion" / "resultados.csv")
    r["correcta"] = r.resultado.eq("correcta")
    t = r.groupby("modo").agg(correctas=("correcta", "sum"),
                              incorrectas=("resultado", lambda s: s.str.startswith("incorrecta").sum()),
                              parciales=("resultado", lambda s: s.eq("correcta sin citar ambas fuentes").sum()),
                              no_responde=("resultado", lambda s: s.eq("no responde").sum()),
                              segundos_promedio=("segundos", "mean"), turnos_promedio=("turnos", "mean")).reset_index()
    t["modo"] = t.modo.map({"A": "A: sin MCP ni Skills", "B": "B: con MCP y Skills"})
    por_tipo = r.pivot_table(index="tipo", columns="modo", values="correcta", aggfunc="sum").reset_index()
    piv = r.pivot(index="id", columns="modo", values="resultado")
    cambios = piv[piv.get("A") != piv.get("B")] if {"A", "B"} <= set(piv.columns) else piv
    md = [apa.tabla_markdown(t.rename(columns={"modo": "Modo", "correctas": "Correctas", "incorrectas": "Incorrectas",
                                               "parciales": "Parciales", "no_responde": "Sin respuesta",
                                               "segundos_promedio": "Segundos (media)",
                                               "turnos_promedio": "Turnos (media)"}), 1,
                             "Resultados de la evaluación por modo (10 preguntas)",
                             "Correcta = dentro de la tolerancia fijada antes de ejecutar; en preguntas mixtas además "
                             "debe citar BCRP e INEI.", decimales=1),
          apa.tabla_markdown(por_tipo.rename(columns={"tipo": "Tipo de pregunta"}), 2,
                             "Respuestas correctas por tipo de pregunta y modo",
                             "BCRP: 4 preguntas; ENAHO: 4; mixtas: 2.", decimales=0),
          "**Cambios por pregunta (A -> B)**", "", "| Pregunta | Modo A | Modo B |", "|:---|:---|:---|",
          *[f"| {i} | {f.get('A', '')} | {f.get('B', '')} |" for i, f in cambios.iterrows()], ""]
    (RAIZ / "evaluacion" / "resumen.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))

    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(7, 4.6))
    cats = ["correctas", "incorrectas", "no_responde"]
    etiquetas = ["Correctas", "Incorrectas", "Sin respuesta"]
    x = range(len(cats))
    for i, (fila, color, hatch) in enumerate(zip(t.itertuples(), [apa.GRIS_CLARO, apa.AZUL], ["//", ""])):
        vals = [getattr(fila, c) for c in cats]
        pos = [p + (i - 0.5) * 0.38 for p in x]
        ax.bar(pos, vals, width=0.38, color=color, hatch=hatch, edgecolor="#404040", linewidth=0.5,
               label=fila.modo)
        for p, v in zip(pos, vals):
            ax.text(p, v + 0.15, f"{v:.0f}", ha="center", fontsize=10)
    ax.set_xticks(list(x), etiquetas)
    ax.set_ylabel("Número de preguntas (de 10)")
    ax.set_ylim(0, 10.5)
    ax.legend(loc="upper right")
    apa.encabezar(fig, "E1", "Desempeño de Claude Code sin y con el MCP del BCRP y las Skills de ENAHO",
                  "Diez preguntas con respuesta verificada de forma independiente (4 BCRP, 4 ENAHO, 2 mixtas), "
                  "mismo modelo e instrucción en sesiones independientes. Fuente: elaboración propia con "
                  "evaluacion/resultados.csv.", ancho_nota=100, abajo=0.22)
    apa.guardar(fig, RAIZ / "figuras" / "evaluacion_modos.png")


if __name__ == "__main__":
    main()
