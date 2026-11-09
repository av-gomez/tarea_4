---
name: informando-investigacion
description: Coordina una investigación socioeconómica del Perú que combina series macroeconómicas del BCRP (servidor MCP bcrp) con microdatos de la ENAHO 2024 del INEI (skills limpiando-enaho, graficando-enaho y mapeando-enaho), y produce un informe académico en formato APA 7 con hallazgos, figuras, mapa, tablas, verificación independiente de cifras, versión HTML y tablero interactivo. Úsala cuando pidan investigar, analizar o redactar un informe sobre pobreza, inflación, actividad económica, tipo de cambio o desigualdad territorial en el Perú.
argument-hint: "[pregunta de investigación]"
---

# Investigación socioeconómica del Perú (BCRP + ENAHO)

Pregunta: $ARGUMENTS

Trabaja en este orden y no te saltes pasos. Ninguna cifra se escribe de memoria: cada número del informe sale
de una herramienta MCP, de `salidas/indicadores.csv` o de una tabla en `tablas/`.

## 1. Plan (escríbelo en `informes/plan.md`)

- Reformula la pregunta, su objetivo y su delimitación (periodo, territorio, unidad de análisis).
- Lista qué responde cada fuente: BCRP (series nacionales, frecuencia mensual o anual) y ENAHO (corte
  transversal 2024, personas y hogares). Declara que la comparación es descriptiva y no causal.
- Lista las herramientas a usar: al menos dos del MCP `bcrp` y al menos dos skills.

## 2. Datos del BCRP (servidor MCP `bcrp`)

1. Identifica las series con `buscar_series` o el recurso `bcrp://series-clave`; lee `bcrp://serie/{codigo}`
   para conocer su definición.
2. Obtén cifras con `resumen_anual` (por año), `resumen` (periodo) o `comparar_series` (dos indicadores).
3. Genera la figura con `graficar_serie` (número APA correlativo; guarda PNG en `figuras/` y datos en `tablas/`).
4. Anota código, periodo y URL de cada cifra. Si una herramienta falla, regístralo como limitación.

## 3. Datos de la ENAHO (skills)

1. `limpiando-enaho`: si no existe `salidas/indicadores.csv`, ejecútala y confirma la validación.
2. `graficando-enaho`: al menos un gráfico (p. ej. `--tipo area` o `--tipo departamento`).
3. `mapeando-enaho`: el mapa departamental.
4. Toma las cifras de `salidas/indicadores.csv` con su IC 95 %; si los IC se superponen, no afirmes diferencia.

## 4. Informe (`informes/informe_final.md`)

Estructura obligatoria, en español y estilo APA 7 (encabezados de nivel 1 y 2, figuras y tablas numeradas con
número en negrita y título en cursiva, nota debajo, citas autor-año y lista de referencias con
`comun/apa.py: REFERENCIAS_APA`):

1. Pregunta de investigación (tema, objetivo, delimitación).
2. Fuentes y metodología (series con código; módulos, filtros, ponderadores, error de muestreo).
3. Resultados: al menos tres hallazgos numerados, cada uno con cifra, fuente y figura o tabla.
4. Visualizaciones: una figura del BCRP, una de la ENAHO y el mapa (rutas relativas `../figuras/...`).
5. Interpretación (patrones; asociación, no causalidad).
6. Limitaciones (cobertura del IPC de Lima, corte transversal 2024, niveles de agregación distintos, error de
   muestreo, herramientas que fallaron).
7. Reproducibilidad (comandos, scripts, archivos y códigos de serie).
8. Referencias.

## 5. Verificación y publicación

1. Escribe `informes/afirmaciones.csv` con al menos 3 cifras del informe (de ambas fuentes); formato en el
   docstring de `scripts/verificar.py`. Fija la tolerancia antes de verificar.
2. Ejecuta `uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv`. Si
   alguna no coincide, corrige el informe con el valor de la herramienta o explica la diferencia; nunca cambies
   el valor verificado.
3. Ejecuta `uv run .claude/skills/informando-investigacion/scripts/publicar.py` para generar
   `informes/informe_final.html` y `informes/dashboard.html`.
4. Termina con un resumen: hallazgos, archivos generados y herramientas MCP y skills usadas.
