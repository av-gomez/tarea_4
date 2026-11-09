"""Estimadores ponderados con error de muestreo para la ENAHO (usados por las tres Skills).

La ENAHO es una muestra probabilística, estratificada y por conglomerados. Por eso:

1. Toda proporción se estima como razón ponderada  p = sum(w*y) / sum(w)  con el factor de expansión
   de la unidad de análisis (``facpob07`` para personas, ``factor07`` para hogares).
2. El error estándar se aproxima por linealización de Taylor (Wolter, 2007) con conglomerados
   (``conglome``) como unidades primarias y estratos de diseño = departamento x estrato geográfico.
   Es la misma lógica de ``svyset conglome [pw=facpob07], strata(estrato)`` en Stata.
3. Se reporta el coeficiente de variación (CV); el INEI considera poco confiables las estimaciones con
   CV > 15 %.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

Z95 = 1.959964


def proporcion(df: pd.DataFrame, y: str, w: str = "facpob07", psu: str = "conglome",
               estrato: str = "estrato_diseno") -> dict:
    """Proporción ponderada (en %) con error estándar, IC 95 % y CV por linealización."""
    d = df[[y, w, psu, estrato]].dropna()
    W = d[w].sum()
    p = (d[w] * d[y]).sum() / W
    z = d[w] * (d[y] - p) / W                      # variable linealizada
    tot = z.groupby([d[estrato], d[psu]]).sum().rename("z").reset_index()
    var = 0.0
    for _, g in tot.groupby(estrato):
        n_h = len(g)
        if n_h > 1:
            var += n_h / (n_h - 1) * ((g.z - g.z.mean()) ** 2).sum()
    ee = float(np.sqrt(var))
    return {"valor_pct": 100 * p, "ee_pct": 100 * ee, "ic95_inf": 100 * (p - Z95 * ee),
            "ic95_sup": 100 * (p + Z95 * ee), "cv_pct": 100 * ee / p if p > 0 else np.nan,
            "n_muestral": int(len(d)), "poblacion_expandida": float(W)}


def por_grupo(df: pd.DataFrame, y: str, grupo: str, **kw) -> pd.DataFrame:
    """Aplica :func:`proporcion` a cada categoría de ``grupo``."""
    filas = [{"categoria": k, **proporcion(g, y, **kw)} for k, g in df.groupby(grupo, observed=True)]
    return pd.DataFrame(filas)


def media(df: pd.DataFrame, y: str, w: str = "facpob07") -> float:
    d = df[[y, w]].dropna()
    return float((d[y] * d[w]).sum() / d[w].sum())
