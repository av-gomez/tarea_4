---
name: informando-investigacion
description: Coordina una investigación socioeconómica del Perú que combina series macroeconómicas del BCRP (servidor MCP bcrp) con microdatos de la ENAHO 2019-2025 del INEI (skills limpiando-enaho, explorando-enaho, graficando-enaho y mapeando-enaho), y produce un informe académico en formato APA 7 con hallazgos, figuras, mapas, tablas, verificación independiente de cifras, versión HTML y tablero interactivo. Úsala cuando pidan investigar, analizar o redactar un informe sobre pobreza, inflación, actividad económica, empleo, educación, salud, servicios o desigualdad territorial en el Perú.
argument-hint: "[pregunta de investigación]"
---

# Investigación socioeconómica del Perú (BCRP + ENAHO)

Pregunta: $ARGUMENTS

Trabaja en este orden. Ninguna cifra se escribe de memoria: cada número sale de una herramienta MCP, de
`salidas/serie_indicadores.csv`, de `salidas/indicadores_<año>.csv` o de una tabla en `tablas/`.

## 1. Plan (`informes/plan.md`)

Reformula la pregunta, el objetivo y la delimitación (años, territorio, unidad de análisis). Indica qué aporta
cada fuente y declara que la comparación entre fuentes es descriptiva, no causal. Lista las herramientas.

## 2. BCRP (servidor MCP `bcrp`)

1. Series con `buscar_series` o `bcrp://series-clave`; definición con `bcrp://serie/{codigo}`.
2. Cifras con `resumen_anual`, `resumen` o `comparar_series`.
3. Datos para figuras con `graficar_serie` (guarda la tabla en `tablas/<archivo>.csv`). Para el gráfico
   combinado inflación-pobreza usa `archivo="bcrp_inflacion.png"` con PN01273PM en el periodo de la ENAHO.

## 3. ENAHO (skills; invócalas con la herramienta `Skill`)

1. `limpiando-enaho`: todos los años necesarios con `--anios 2019 2020 2021 2022 2023 2024 2025` (valida
   cada año contra el INEI y crea `salidas/serie_indicadores.csv`).
2. `explorando-enaho`: dimensiones de otros módulos (educación 03, salud 04, empleo 05, vivienda 01...) con
   `explorar.py diccionario` e `explorar.py indicador`, por ejemplo por `pobre`, `area` o `departamento`.
3. `graficando-enaho`: visualizaciones con `scripts/visualizar.py` (evolucion, distribucion, calor, pendiente,
   perfil, waffle, macro) y, si hace falta, barras de `scripts/graficar.py`.
4. `mapeando-enaho`: `scripts/mapas_series.py mosaico` y `cambio`, y `scripts/mapear.py`.
5. Si los IC 95 % se superponen, no afirmes diferencias; advierte CV > 15 %.

## 4. Informe (`informes/informe_final.md`)

Estilo APA 7 con la tipografía del documento. Cada script imprime el pie sugerido; úsalo así (la imagen va sin
texto incrustado):

```markdown
**Figura 3**

*Título en cursiva*

![Figura 3. Título](../figuras/archivo.png)

*Nota.* Descripción, método y fuente.
```

Estructura: resumen ejecutivo (3-5 viñetas con las cifras clave), 1. Pregunta, 2. Fuentes y metodología,
3. Resultados (al menos cinco hallazgos numerados, cada uno con figura o tabla), 4. Interpretación,
5. Limitaciones, 6. Reproducibilidad (comandos y archivos), Referencias (de `comun/apa.py: REFERENCIAS_APA`).
Numera figuras y tablas en orden de aparición y pasa ese número a cada script (`--numero`).

## 5. Verificación y publicación

1. `informes/afirmaciones.csv` con al menos 6 cifras de ambas fuentes (formato en `scripts/verificar.py`;
   para otro año de la ENAHO usa `pobreza_monetaria@2025` en la columna agregacion).
2. `uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv`.
3. `uv run .claude/skills/informando-investigacion/scripts/publicar.py` (HTML del informe, tablero y portal
   `informes/index.html`).
4. Resume hallazgos, archivos y herramientas usadas.
