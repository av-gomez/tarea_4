# Plan de investigación

## Pregunta reformulada
¿Cómo evolucionaron la inflación (IPC de Lima Metropolitana) y la actividad económica (PBI trimestral) del Perú entre 2019 y 2024, y qué brechas territoriales (departamentos; urbano–rural) mostraba la pobreza monetaria en 2024?

**Objetivo.** Describir la trayectoria macroeconómica 2019-2024 y cuantificar la desigualdad territorial de la pobreza monetaria en 2024.

**Delimitación.** Periodo 2019-2024 (BCRP); corte transversal 2024 (ENAHO); nivel nacional, 25 departamentos (Lima y Callao separados) y área urbana/rural; unidad de análisis: personas (ponderador `factor07 × mieperho`).

## Qué responde cada fuente
- **BCRP** (series nacionales): PN01273PM (inflación a 12 meses, mensual) y PN02516AQ (PBI global, índice 2007 = 100, trimestral).
- **ENAHO 2024, INEI** (personas y hogares): pobreza monetaria por área y departamento, con IC 95 %.
- La comparación entre ambas fuentes es **descriptiva y no causal**: difieren el nivel de agregación y el periodo.

## Herramientas
- MCP `bcrp`: `buscar_series`, `resumen_anual`, `resumen`, `graficar_serie`.
- Skills: `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho`, `informando-investigacion` (verificar.py, publicar.py).

## Figuras
1 inflación; 2 PBI; 3 pobreza por área; 4 pobreza por departamento; 5 mapa.
