# Verificación independiente de cifras del informe

Generado con `.claude/skills/informando-investigacion/scripts/verificar.py` a partir de `afirmaciones.csv`. Las cifras del BCRP se consultaron directamente en la API pública (sin el servidor MCP) y las de la ENAHO se recalcularon desde el archivo .dta original de la sumaria con pandas, sin la skill de limpieza.

**Tabla 1**

*Comparación entre las cifras del informe y su verificación independiente*

| Id | Afirmación | Informe | Verificado | Diferencia | Tolerancia | Coincide | Procedimiento |
|:---|:---|---:|---:|---:|---:|:---:|:---|
| f1 | Inflación de diciembre de 2022 (8.46 %) | 8.46 | 8.4592 | 0.0008 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-12/2022-12 |
| f2 | Inflación máxima del periodo en junio de 2022 (8.81 %) | 8.81 | 8.8126 | -0.0026 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-6/2022-6 |
| f3 | Inflación promedio de 2025 (1.50 %) | 1.5 | 1.5018 | -0.0018 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2025-1/2025-12 |
| f4 | Inflación de diciembre de 2025 (1.51 %) | 1.51 | 1.5088 | 0.0012 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2025-12/2025-12 |
| f5 | Crecimiento real del PBI en 2020 (-10.93 %) | -10.93 | -10.9333 | 0.0033 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM04923AA/json/2020/2020 |
| f6 | Crecimiento real del PBI en 2021 (13.42 %) | 13.42 | 13.4166 | 0.0034 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM04923AA/json/2021/2021 |
| f7 | Crecimiento real del PBI en 2025 (3.43 %) | 3.43 | 3.4306 | -0.0006 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PM04923AA/json/2025/2025 |
| f8 | Pobreza nacional 2019 (20.19 %) | 20.19 | 20.1934 | -0.0034 | 0.05 | Sí | datos/687-Modulo34.zip: sumaria-2019.dta |
| f9 | Pobreza nacional 2020 (30.13 %) | 30.13 | 30.1332 | -0.0032 | 0.05 | Sí | datos/737-Modulo34.zip: sumaria-2020.dta |
| f10 | Pobreza nacional 2025 (25.67 %) | 25.67 | 25.6667 | 0.0033 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |
| f11 | Pobreza rural 2019 (40.78 %) | 40.78 | 40.7784 | 0.0016 | 0.05 | Sí | datos/687-Modulo34.zip: sumaria-2019.dta |
| f12 | Pobreza urbana 2019 (14.58 %) | 14.58 | 14.5751 | 0.0049 | 0.05 | Sí | datos/687-Modulo34.zip: sumaria-2019.dta |
| f13 | Pobreza rural 2025 (35.46 %) | 35.46 | 35.4547 | 0.0053 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |
| f14 | Pobreza urbana 2025 (23.41 %) | 23.41 | 23.4128 | -0.0028 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |
| f15 | Pobreza en Cajamarca 2025 (41.04 %) | 41.04 | 41.0363 | 0.0037 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |
| f16 | Pobreza en Lima 2019 (14.21 %) | 14.21 | 14.2101 | -0.0001 | 0.05 | Sí | datos/687-Modulo34.zip: sumaria-2019.dta |
| f17 | Pobreza en Lima 2025 (26.33 %) | 26.33 | 26.3319 | -0.0019 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |
| f18 | Pobreza extrema nacional 2025 (4.65 %) | 4.65 | 4.6514 | -0.0014 | 0.05 | Sí | datos/1031-Modulo34.zip: sumaria-2025.dta |

*Nota.* 18 de 18 afirmaciones coinciden dentro de la tolerancia definida antes de verificar. Diferencia = valor del informe menos valor verificado.
