"""Construye evaluacion/preguntas.csv con respuestas esperadas obtenidas de forma independiente.

    uv run evaluacion/verdades.py

Independencia respecto del agente:
  - BCRP: consulta directa a la API pública con httpx (no usa mcp/server.py).
  - ENAHO: las cifras oficiales publicadas por el INEI (2025) y la referencia de la sesión 16 son la verdad;
    además se recalculan aquí desde el .dta original con pandas puro (sin la skill limpiando-enaho) como
    control cruzado (columna `control_calculado`).
  - Preguntas combinadas: se calculan aquí con ambos insumos independientes.
Las tolerancias se fijan en este archivo ANTES de ejecutar la evaluación y no se modifican después.
"""
from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"


def bcrp(codigo, desde, hasta):
    url = f"{API}/{codigo}/json/{desde}/{hasta}"
    for i in range(5):
        r = httpx.get(url, timeout=60)
        if r.text.strip().startswith("{"):
            return [float(p["values"][0]) for p in r.json()["periods"] if p["values"][0] != "n.d."], url
        time.sleep(3 + 3 * i)
    raise RuntimeError(url)


def main():
    with zipfile.ZipFile(RAIZ / "datos" / "966-Modulo34.zip") as z:
        s = pd.read_stata(io.BytesIO(z.read("966-Modulo34/sumaria-2024.dta")), convert_categoricals=False)
    w = s.factor07 * s.mieperho
    pob = lambda m, y: 100 * (w[m] * y[m]).sum() / w[m].sum()  # noqa: E731
    todos = pd.Series(True, index=s.index)
    pobre, extremo = s.pobreza <= 2, s.pobreza == 1
    gasto_pc = s.gashog2d / (12 * s.mieperho)
    gasto_medio = (w * gasto_pc).sum() / w.sum()
    linea_media = (w * s.linea).sum() / w.sum()

    ipc_dic22, u1 = bcrp("PN01273PM", "2022-12", "2022-12")
    pbi_23, u2 = bcrp("PM04923AA", "2023", "2023")
    ref_dic24, u3 = bcrp("PD04722MM", "2024-12", "2024-12")
    tc_dic24, u4 = bcrp("PN01206PM", "2024-12", "2024-12")
    tc_2024, u5 = bcrp("PN01206PM", "2024-1", "2024-12")
    ipc_dic24, u6 = bcrp("PN01273PM", "2024-12", "2024-12")
    tc_prom = sum(tc_2024) / len(tc_2024)

    filas = [
        ("bcrp_ipc_dic22", "bcrp", "¿Cuál fue la inflación interanual (variación del IPC en 12 meses) de Lima "
         "Metropolitana en diciembre de 2022, en %?", ipc_dic22[0], 0.05, "PN01273PM 2022-12", u1, ""),
        ("bcrp_pbi_2023", "bcrp", "¿Cuál fue la variación porcentual real del PBI del Perú en 2023 según el BCRP, "
         "en %?", pbi_23[0], 0.05, "PM04923AA 2023", u2, ""),
        ("bcrp_ref_dic24", "bcrp", "¿Cuál era la tasa de referencia de la política monetaria del BCRP en "
         "diciembre de 2024, en %?", ref_dic24[0], 0.01, "PD04722MM 2024-12", u3, ""),
        ("bcrp_tc_dic24", "bcrp", "¿Cuál fue el tipo de cambio interbancario venta promedio de diciembre de 2024 "
         "según el BCRP, en soles por dólar?", tc_dic24[0], 0.003, "PN01206PM 2024-12", u4, ""),
        ("enaho_pobreza_nac", "enaho", "Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del Perú "
         "estaba en situación de pobreza monetaria en 2024, en %?", 27.6, 0.1, "INEI (2025); sumaria",
         "INEI, informe técnico de pobreza 2024", round(pob(todos, pobre), 3)),
        ("enaho_pobreza_rural", "enaho", "Según la ENAHO 2024 del INEI, ¿cuál fue la tasa de pobreza monetaria "
         "en el área rural del Perú en 2024, en %?", 39.3, 0.1, "INEI (2025); estrato 6-8",
         "INEI, informe técnico de pobreza 2024", round(pob(s.estrato > 5, pobre), 3)),
        ("enaho_pobreza_cajamarca", "enaho", "Según la ENAHO 2024 del INEI, ¿cuál fue la tasa de pobreza "
         "monetaria del departamento de Cajamarca en 2024, en %?", 45.0, 0.1, "INEI (2025); ubigeo 06",
         "Sesión 16: referencias/pobreza_departamento_2024.csv",
         round(pob(s.ubigeo.str[:2] == "06", pobre), 3)),
        ("enaho_pobreza_extrema", "enaho", "Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del "
         "Perú estaba en situación de pobreza extrema en 2024, en %?", 5.5, 0.1, "INEI (2025); pobreza == 1",
         "INEI, informe técnico de pobreza 2024", round(pob(todos, extremo), 3)),
        ("mixta_gasto_usd", "mixta", "Usando la ENAHO 2024 del INEI y el BCRP: ¿cuál fue el gasto per cápita "
         "mensual promedio de la población peruana en 2024 (gashog2d / (12 × mieperho), ponderado por "
         "factor07 × mieperho), expresado en dólares con el tipo de cambio interbancario venta promedio de 2024 "
         "(promedio de los 12 meses de la serie PN01206PM), en US$?", gasto_medio / tc_prom,
         0.02 * gasto_medio / tc_prom, f"ENAHO sumaria + PN01206PM 2024 (TC promedio {tc_prom:.4f})", u5,
         round(gasto_medio, 2)),
        ("mixta_linea_ajustada", "mixta", "Usando la ENAHO 2024 del INEI y el BCRP: si la línea de pobreza "
         "monetaria promedio por persona de 2024 (variable linea de la sumaria, ponderada por factor07 × "
         "mieperho, en soles por mes) se actualizara con la inflación interanual de Lima Metropolitana de "
         "diciembre de 2024 (serie PN01273PM), ¿cuál sería su valor en soles por mes?",
         linea_media * (1 + ipc_dic24[0] / 100), 1.0,
         f"linea media {linea_media:.2f} × (1 + {ipc_dic24[0]:.4f}/100)", u6, round(linea_media, 2)),
    ]
    df = pd.DataFrame(filas, columns=["id", "tipo", "pregunta", "verdad", "tolerancia", "detalle", "fuente_verdad",
                                      "control_calculado"])
    df["verdad"] = df.verdad.round(4)
    df["tolerancia"] = df.tolerancia.round(4)
    df.to_csv(RAIZ / "evaluacion" / "preguntas.csv", index=False, encoding="utf-8")
    print(df[["id", "verdad", "tolerancia", "control_calculado", "detalle"]].to_string())


if __name__ == "__main__":
    main()
