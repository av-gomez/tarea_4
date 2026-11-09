# Verificación independiente de cifras del informe

Generado con `.claude/skills/informando-investigacion/scripts/verificar.py` a partir de `afirmaciones.csv`. Las cifras del BCRP se consultaron directamente en la API pública (sin el servidor MCP) y las de la ENAHO se recalcularon desde el archivo .dta original de la sumaria con pandas, sin la skill de limpieza.

**Tabla 1**

*Comparación entre las cifras del informe y su verificación independiente*

| Id | Afirmación | Informe | Verificado | Diferencia | Tolerancia | Coincide | Procedimiento |
|:---|:---|---:|---:|---:|---:|:---:|:---|
| f1 | Inflación de diciembre de 2022 (8.46 %) | 8.46 | 8.4592 | 0.0008 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-12/2022-12 |
| f2 | Inflación de diciembre de 2024 (1.97 %) | 1.97 | 1.9663 | 0.0037 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2024-12/2024-12 |
| f3 | Inflación promedio de 2022 (7.86 %) | 7.86 | 7.8646 | -0.0046 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-1/2022-12 |
| f4 | Pobreza rural 2024 (39.30 %) | 39.3 | 39.3028 | -0.0028 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f5 | Pobreza urbana 2024 (24.81 %) | 24.81 | 24.807 | 0.003 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f6 | Pobreza en Cajamarca 2024 (45.01 %) | 45.01 | 45.0069 | 0.0031 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |

*Nota.* 6 de 6 afirmaciones coinciden dentro de la tolerancia definida antes de verificar. Diferencia = valor del informe menos valor verificado.
