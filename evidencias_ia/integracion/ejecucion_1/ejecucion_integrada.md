# Ejecución integrada 1 (previa a las correcciones)

Fuente: `ejecucion_integrada.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: [{"name": "bcrp", "status": "connected", "source": "dynamic"}]
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Task, Bash, CronCreate, CronDelete, CronList, DesignSync, Edit, EnterWorktree, ExitWorktree, Glob, Grep, ListAgents, ListMcpResourcesTool, Monitor, NotebookEdit, PowerShell, PushNotification, Read, ReadMcpResourceDirTool, ReadMcpResourceTool, RemoteTrigger, ReportFindings, ScheduleWakeup, SendMessage, Skill, TaskStop, ToolSearch, WebFetch, WebSearch, Workflow, Write, mcp__bcrp__buscar_series, mcp__bcrp__comparar_series, mcp__bcrp__graficar_serie, mcp__bcrp__resumen, mcp__bcrp__resumen_anual, mcp__bcrp__serie

## 1. Asistente (Claude)

**Herramienta:** `Skill`

```json
{
 "skill": "informando-investigacion"
}
```

## 2. Resultado

**Resultado de la herramienta:**

```
Launching skill: informando-investigacion
```

## 3. Usuario

Base directory for this skill: C:/Users/[usuario]\Documents\tarea_4\.claude\skills\informando-investigacion

# Investigación socioeconómica del Perú (BCRP + ENAHO)

Pregunta: 

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


## 4. Asistente (Claude)

**Herramienta:** `ToolSearch`

```json
{
 "query": "select:mcp__bcrp__buscar_series,mcp__bcrp__resumen,mcp__bcrp__resumen_anual,mcp__bcrp__comparar_series,mcp__bcrp__serie,mcp__bcrp__graficar_serie",
 "max_results": 10
}
```

## 5. Resultado

**Resultado de la herramienta:**

```
[imagen]
[imagen]
[imagen]
[imagen]
[imagen]
[imagen]
```

## 6. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls; ls informes salidas tablas figuras mapas 2>&1 | head -50; sed -n 1,40p .claude/skills/informando-investigacion/scripts/verificar.py; grep -n \"REFERENCIAS_APA\" -A30 comun/apa.py | head -50"
}
```

## 7. Asistente (Claude)

**Herramienta:** `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc 12 meses"
}
```

## 8. Asistente (Claude)

**Herramienta:** `mcp__bcrp__buscar_series`

```json
{
 "texto": "producto bruto interno",
 "limite": 15
}
```

## 9. Resultado

**Resultado de la herramienta:**

```
{"result":[{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1950","actualizada":"2026-10-08"},{"codigo":"PN09821PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Importado","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01281PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01283PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09820PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09830PM","nombre":"Inflación de socios comerciales - IPC Externo Multilateral (var% 12 meses)","categoria":"Tipo de cambio real","frecuencia":"Mensual","inicio":"Ene-1996","actualizada":"2026-10-08"},{"codigo":"PN09819PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01277PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Sin Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"}]}
```

## 10. Resultado

**Resultado de la herramienta:**

```
{"result":[{"codigo":"PN02509AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Pesca","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37685AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Pesca","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02514AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Comercio","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02515AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Servicios","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02516AQ","nombre":"Producto bruto interno (índice 2007 = 100) - PBI Global","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37690AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Comercio","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02511AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Manufactura","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37691AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Servicios","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02508AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Agropecuario","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02513AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Construcción","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37692AQ","nombre":"Producto bruto interno (millones S/ de 2007) - PBI Global","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1979","actualizada":"2026-08-20"},{"codigo":"PN37687AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Manufactura","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN39029BQ","nombre":"Producto bruto interno (millones US$) - PBI (millones US$)","categoria":"PBI gasto","frecuencia":"Trimestral","inicio":"T1-1994","actualizada":"2026-08-20"},{"codigo":"PN37684AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Agropecuario","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37689AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Construcción","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"}]}
```

## 11. Resultado

**Resultado de la herramienta:**

```
CLAUDE.md
comun
datos
evaluacion
evidencias_ia
figuras
informes
mapas
mcp
pyproject.toml
referencias
salidas
tablas
uv.lock
figuras:

informes:

mapas:

salidas:

tablas:
"""Verificación independiente de las afirmaciones numéricas de un informe.

    uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv

Cada fila de afirmaciones.csv describe una cifra del informe:

    id,afirmacion,fuente,codigo,periodo,agregacion,valor_informe,tolerancia
    f1,"La inflación de 2022 cerró en 8.5 %",bcrp,PN01273PM,2022-12,valor,8.46,0.01
    f2,"Inflación promedio de 2022",bcrp,PN01273PM,2022,promedio,7.88,0.01
    f3,"Pobreza rural",enaho,area,Rural,pobreza_monetaria,39.3,0.05

La verificación NO usa el servidor MCP ni la skill de limpieza, para que sea un control independiente:
  - bcrp: consulta directamente la API pública (https://estadisticas.bcrp.gob.pe/estadisticas/series/api)
    y toma el valor del periodo (agregacion = valor) o el promedio / último dato del año (promedio, fin).
  - enaho: vuelve a leer el .dta original de la sumaria y calcula con pandas puro
    sum(factor07*mieperho*pobre)/sum(factor07*mieperho) para nacional, area, departamento (código), dominio
    o region. En agregacion se indica pobreza_monetaria o pobreza_extrema.
Escribe informes/verificacion.md (tabla APA 7) e informes/verificacion.csv. Sale con código 1 si alguna
afirmación no coincide, para que el agente la corrija o la reporte como limitación.
"""
from __future__ import annotations

import io
import sys
import time
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9,
         "Oct": 10, "Nov": 11, "Dic": 12}


def _bcrp(codigo: str, desde: str, hasta: str) -> pd.DataFrame:
    url = f"{API}/{codigo}/json/{desde}/{hasta}"
    for i in range(5):
35:REFERENCIAS_APA = {
36-    "enaho": ("Instituto Nacional de Estadística e Informática. (2025). *Encuesta Nacional de Hogares sobre "
37-              "Condiciones de Vida y Pobreza 2024* [Base de datos: módulos 02 y 34]. "
38-              "https://proyectos.inei.gob.pe/microdatos/"),
39-    "bcrp": ("Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos]. "
40-             "https://estadisticas.bcrp.gob.pe/estadisticas/series/"),
41-    "geo": ("D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub. "
42-            "https://github.com/d2cml-ai/Data-Science-Python"),
43-    "pobreza_inei": ("Instituto Nacional de Estadística e Informática. (2025). *Perú: Evolución de la pobreza "
44-                     "monetaria 2015-2024. Informe técnico*. INEI."),
45-}
46-
47-
48-def aplicar_estilo() -> None:
49-    """Configura matplotlib con la tipografía y la gráfica sobria que pide APA 7."""
50-    plt.rcParams.update({
51-        "font.family": "serif",
52-        "font.serif": [FUENTE, "Times", "DejaVu Serif"],
53-        "mathtext.fontset": "stix",
54-        "font.size": 11,
55-        "axes.titlesize": 12,
56-        "axes.labelsize": 11,
57-        "xtick.labelsize": 10,
58-        "ytick.labelsize": 10,
59-        "legend.fontsize": 10,
60-        "legend.frameon": False,
61-        "axes.spines.top": False,
62-        "axes.spines.right": False,
63-        "axes.edgecolor": "#404040",
64-        "axes.linewidth": 0.8,
65-        "axes.grid": False,
```

## 12. Asistente (Claude)

**Herramienta:** `mcp__bcrp__buscar_series`

```json
{
 "texto": "PBI var% anual",
 "frecuencia": "Trimestral"
}
```

## 13. Resultado

**Resultado de la herramienta:**

```
{"result":[]}
```

## 14. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen_anual`

```json
{
 "codigo": "PN01273PM",
 "desde_anio": 2019,
 "hasta_anio": 2024
}
```

## 15. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","anios":[{"anio":2019,"promedio":2.136886,"fin_de_periodo":{"periodo":"2019-12","valor":1.900092},"maximo":{"periodo":"2019-05","valor":2.725128},"minimo":{"periodo":"2019-09","valor":1.851007},"n":12,"completo":true},{"anio":2020,"promedio":1.827263,"fin_de_periodo":{"periodo":"2020-12","valor":1.973232},"maximo":{"periodo":"2020-11","valor":2.14221},"minimo":{"periodo":"2020-06","valor":1.598732},"n":12,"completo":true},{"anio":2021,"promedio":3.972447,"fin_de_periodo":{"periodo":"2021-12","valor":6.430387},"maximo":{"periodo":"2021-12","valor":6.430387},"minimo":{"periodo":"2021-04","valor":2.383698},"n":12,"completo":true},{"anio":2022,"promedio":7.864561,"fin_de_periodo":{"periodo":"2022-12","valor":8.459162},"maximo":{"periodo":"2022-06","valor":8.812633},"minimo":{"periodo":"2022-01","valor":5.684917},"n":12,"completo":true},{"anio":2023,"promedio":6.312536,"fin_de_periodo":{"periodo":"2023-12","valor":3.237383},"maximo":{"periodo":"2023-01","valor":8.664267},"minimo":{"periodo":"2023-12","valor":3.237383},"n":12,"completo":true},{"anio":2024,"promedio":2.354973,"fin_de_periodo":{"periodo":"2024-12","valor":1.966303},"maximo":{"periodo":"2024-02","valor":3.294067},"minimo":{"periodo":"2024-09","valor":1.775011},"n":12,"completo":true}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12","nota":"Promedio = media aritmética de las observaciones del año; fin de periodo = última observación."}
```

## 16. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen_anual`

```json
{
 "codigo": "PN37692AQ",
 "desde_anio": 2019,
 "hasta_anio": 2024
}
```

## 17. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls datos evidencias_ia referencias; (uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 2>&1 | tail -25)",
 "timeout": 500000
}
```

## 18. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN37692AQ","nombre":"Producto bruto interno (millones S/ de 2007) - PBI Global","frecuencia":"Trimestral","anios":[{"anio":2019,"promedio":136651.250013,"fin_de_periodo":{"periodo":"2019-T4","valor":143862.017305},"maximo":{"periodo":"2019-T4","valor":143862.017305},"minimo":{"periodo":"2019-T1","valor":127532.946748},"n":4,"completo":true},{"anio":2020,"promedio":121710.750023,"fin_de_periodo":{"periodo":"2020-T4","valor":141876.296288},"maximo":{"periodo":"2020-T4","valor":141876.296288},"minimo":{"periodo":"2020-T2","valor":95975.848},"n":4,"completo":true},{"anio":2021,"promedio":138040.25001,"fin_de_periodo":{"periodo":"2021-T4","valor":146790.796253},"maximo":{"periodo":"2021-T4","valor":146790.796253},"minimo":{"periodo":"2021-T1","valor":128175.738787},"n":4,"completo":true},{"anio":2022,"promedio":141930.500018,"fin_de_periodo":{"periodo":"2022-T4","valor":149732.63923},"maximo":{"periodo":"2022-T4","valor":149732.63923},"minimo":{"periodo":"2022-T1","valor":133215.627842},"n":4,"completo":true},{"anio":2023,"promedio":141432.75002,"fin_de_periodo":{"periodo":"2023-T4","valor":149238.526247},"maximo":{"periodo":"2023-T4","valor":149238.526247},"minimo":{"periodo":"2023-T1","valor":133188.255831},"n":4,"completo":true},{"anio":2024,"promedio":146404.500006,"fin_de_periodo":{"periodo":"2024-T4","valor":155868.383158},"maximo":{"periodo":"2024-T4","valor":155868.383158},"minimo":{"periodo":"2024-T1","valor":135172.356865},"n":4,"completo":true}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN37692AQ/json/2019-1/2024-4","nota":"Promedio = media aritmética de las observaciones del año; fin de periodo = última observación."}
```

## 19. Resultado

**Resultado de la herramienta:**

```
This command uses shell operators that require approval for safety
```

## 20. Asistente (Claude)

**Herramienta:** `PowerShell`

```json
{
 "command": "ls datos, evidencias_ia, referencias | Out-String; uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 2>&1 | Select-Object -Last 30",
 "timeout": 500000
}
```

## 21. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen`

```json
{
 "codigo": "PN37692AQ",
 "desde": "2019-T4",
 "hasta": "2024-T4"
}
```

## 22. Asistente (Claude)

**Herramienta:** `mcp__bcrp__comparar_series`

```json
{
 "codigo_a": "PN01273PM",
 "codigo_b": "PN01279PM",
 "desde": "2019-01",
 "hasta": "2024-12"
}
```

## 23. Resultado

**Resultado de la herramienta:**

```
get-childitem uses a parameter or complex path expression (array literal, subexpression, unknown parameter, etc.) that cannot be statically validated and requires manual approval
```

## 24. Resultado

**Resultado de la herramienta:**

```
{"serie_a":{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","promedio":4.078111},"serie_b":{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","promedio":3.55432},"periodos_comunes":72,"desde":"2019-01","hasta":"2024-12","descartados":0,"correlacion_niveles":0.8948,"correlacion_diferencias":0.6637,"diferencia_promedio":0.523791,"maxima_diferencia":{"periodo":"2022-06","valor":3.00736},"minima_diferencia":{"periodo":"2024-05","valor":-1.358235},"fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01279PM/json/2019-1/2024-12"],"advertencia":"Correlación descriptiva; no demuestra una relación causal."}
```

## 25. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN37692AQ","nombre":"Producto bruto interno (millones S/ de 2007) - PBI Global","frecuencia":"Trimestral","n":21,"primero":{"periodo":"2019-T4","valor":143862.017305},"ultimo":{"periodo":"2024-T4","valor":155868.383158},"cambio":12006.365853,"variacion_pct":8.345751,"promedio":138187.477029,"desviacion_estandar":12755.167208,"maximo":{"periodo":"2024-T4","valor":155868.383158},"minimo":{"periodo":"2020-T2","valor":95975.848},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN37692AQ/json/2019-4/2024-4"}
```

## 26. Asistente (Claude)

**Herramienta:** `mcp__bcrp__graficar_serie`

```json
{
 "codigos": [
  "PN01273PM"
 ],
 "desde": "2019-01",
 "hasta": "2024-12",
 "titulo": "Inflación anual de Lima Metropolitana, 2019-2024",
 "linea_referencia": 3,
 "etiqueta_referencia": "Techo del rango meta (3 %)",
 "archivo": "inflacion_2019_2024.png",
 "numero_figura": 1
}
```

## 27. Resultado

**Resultado de la herramienta:**

```
{"archivo":"figuras/inflacion_2019_2024.png","datos":"tablas/inflacion_2019_2024.csv","codigos":["PN01273PM"],"desde":"2019-01","hasta":"2024-12","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12"]}
```

## 28. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 2>&1 | tail -30",
 "timeout": 500000
}
```

## 29. Resultado

**Resultado de la herramienta:**

```
           108,664 (referencia 108,664)
[APROBADA] Unión m:1 sin duplicar ni perder personas
           108,664 personas antes y 108,664 después; 0 sin hogar en la sumaria
[APROBADA] 25 códigos departamentales (01-25), Lima 15 y Callao 07 separados
           25 códigos: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25
[APROBADA] Sin factores de expansión faltantes o no positivos
           facpob07 faltantes: 0
[APROBADA] Población expandida plausible (33-35 millones) (complementaria)
           34,147,768 personas
[APROBADA] Pobreza monetaria nacional (sumaria, factor07 x mieperho; metodo INEI) a <= 0.1 p.p. de 27.6 %
           27.58 % (IC 95 %: 26.59-28.57; CV 1.8 %)
[APROBADA] Pobreza monetaria nacional (personas residentes, facpob07) a <= 0.1 p.p. de 27.6 %
           27.53 % (IC 95 %: 26.54-28.52)
[APROBADA] La ponderacion importa: el promedio simple difiere del ponderado (complementaria)
           promedio simple 25.61 % vs ponderado 27.53 % (el simple NO se usa)
[APROBADA] Pobreza extrema cercana a 5.5 % (complementaria)
           5.50 %
[APROBADA] Pobreza urbana cercana a 24.8 %
           24.81 %
[APROBADA] Pobreza rural cercana a 39.3 %
           39.30 %
[APROBADA] Pobreza departamental igual a la referencia de la sesion 16 (25 de 25, redondeo a 0.1)
           diferencia maxima 0.00 p.p. (departamento 01); 25 de 25 coinciden
[APROBADA] Sensibilidad: con personas y facpob07 la diferencia departamental es menor a 1 p.p. (complementaria)
           diferencia maxima 0.52 p.p. (departamento 21)

Resumen: 18 de 18 verificaciones aprobadas.
RESULTADO: TODAS LAS VALIDACIONES ESENCIALES APROBADAS

Guardado: salidas/personas_2024.parquet (108,664 personas), salidas/hogares_2024.parquet (33,691 hogares) y salidas/indicadores.csv (98 filas).
```

## 30. Asistente (Claude)

Limpieza ENAHO validada (18/18). Ahora genero gráficos y mapa.

## 31. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "(uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area 2>&1 | tail -5; uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento 2>&1 | tail -5; uv run .claude/skills/mapeando-enaho/scripts/mapear.py 2>&1 | tail -8); ls figuras mapas tablas; head -3 salidas/indicadores.csv; grep -E \"area|nacional\" salidas/indicadores.csv | head -12",
 "timeout": 500000
}
```

## 32. Resultado

**Resultado de la herramienta:**

```
This command can't be checked before it runs
```

## 33. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo todos 2>&1 | tail -5",
 "timeout": 500000
}
```

## 34. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/mapeando-enaho/scripts/mapear.py 2>&1 | tail -8",
 "timeout": 500000
}
```

## 35. Resultado

**Resultado de la herramienta:**

```
    Cajamarca      45.01    2.12     40.84     49.17    4.72        1469              1554586
Figura 8: figuras\pobreza_extrema_area.png  |  tabla: tablas/pobreza_extrema_area.csv
categoria  valor_pct  ee_pct  ic95_inf  ic95_sup  cv_pct  n_muestral  poblacion_expandida
   Urbana       3.14    0.25      2.65      3.62    7.93       22031             27887512
    Rural      15.52    0.60     14.34     16.70    3.88       11660              6595188
```

## 36. Resultado

**Resultado de la herramienta:**

```
  21 PUNO            calculado  39.9  referencia  39.9  dif +0.0
  22 SAN MARTIN      calculado  22.0  referencia  22.0  dif +0.0
  23 TACNA           calculado  24.0  referencia  24.0  dif +0.0
  24 TUMBES          calculado  26.9  referencia  26.9  dif +0.0
  25 UCAYALI         calculado  27.1  referencia  27.1  dif +0.0
RESULTADO: APROBADA

Mapa: mapas\pobreza_departamento.png (25 unidades territoriales)
```

## 37. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cat tablas/pobreza_area.csv tablas/pobreza_departamento.csv | cut -c1-120; grep -n \"^figura\\|nacional\" salidas/indicadores.csv | head; head -2 salidas/indicadores.csv; grep -n \"REFERENCIAS_APA\\|def \" comun/apa.py | head -30"
}
```

## 38. Resultado

**Resultado de la herramienta:**

```
categoria,valor_pct,ee_pct,ic95_inf,ic95_sup,cv_pct,n_muestral,poblacion_expandida
Urbana,24.807,0.603,23.624,25.99,2.433,22031,27887512
Rural,39.303,0.769,37.796,40.81,1.957,11660,6595188
categoria,valor_pct,ee_pct,ic95_inf,ic95_sup,cv_pct,n_muestral,poblacion_expandida
Ica,6.014,0.939,4.174,7.854,15.61,1500,854203
Moquegua,10.968,1.78,7.479,14.457,16.231,963,198386
Madre de Dios,11.148,2.174,6.887,15.408,19.499,603,165992
Lambayeque,14.041,1.873,10.369,17.713,13.343,1302,1349731
Arequipa,15.784,1.558,12.73,18.838,9.871,1506,1421684
Junín,18.499,1.825,14.922,22.077,9.866,1506,1450149
Cusco,18.541,1.951,14.718,22.364,10.52,1230,1409467
San Martín,22.021,1.991,18.119,25.924,9.043,1347,947446
Áncash,22.775,1.843,19.162,26.387,8.093,1393,1212494
Apurímac,23.959,2.303,19.446,28.472,9.61,913,494188
Tacna,23.989,2.863,18.377,29.601,11.936,1271,380755
Amazonas,25.749,2.464,20.92,30.578,9.569,1243,442355
Tumbes,26.901,2.449,22.102,31.7,9.102,842,261959
Lima,27.069,1.205,24.708,29.43,4.451,4544,11279908
Ucayali,27.07,2.198,22.762,31.378,8.119,1119,558484
La Libertad,30.19,1.827,26.609,33.772,6.053,1509,2080789
Piura,31.861,1.654,28.618,35.104,5.193,1611,1988570
Ayacucho,32.763,2.245,28.363,37.164,6.853,1160,775447
Huancavelica,33.403,2.187,29.118,37.689,6.546,1042,543103
Callao,33.86,2.399,29.158,38.562,7.085,1027,1142618
Huánuco,38.963,2.541,33.983,43.943,6.521,1244,926653
Pasco,38.972,2.534,34.005,43.939,6.503,865,327776
Puno,39.938,2.302,35.427,44.449,5.763,1123,1586886
Loreto,42.973,2.122,38.813,47.132,4.938,1359,1129071
Cajamarca,45.007,2.123,40.845,49.168,4.718,1469,1554586
2:pobreza_monetaria,nacional,,Perú,27.579,0.506,26.589,28.57,1.833,33691,34482700,factor07*mieperho,True
51:pobreza_extrema,nacional,,Perú,5.505,0.233,5.049,5.96,4.226,33691,34482700,factor07*mieperho,True
indicador,desagregacion,codigo,categoria,valor_pct,ee_pct,ic95_inf,ic95_sup,cv_pct,n_muestral,poblacion_expandida,ponderador,confiable_cv15
pobreza_monetaria,nacional,,Perú,27.579,0.506,26.589,28.57,1.833,33691,34482700,factor07*mieperho,True
35:REFERENCIAS_APA = {
48:def aplicar_estilo() -> None:
74:def encabezar(fig, numero: int | str, titulo: str, nota: str, ancho_nota: int = 120,
89:def guardar(fig, ruta: str | Path) -> Path:
97:def tabla_markdown(df, numero: int | str, titulo: str, nota: str, decimales: int = 1) -> str:
131:def tabla_html(df, numero: int | str, titulo: str, nota: str, decimales: int = 1) -> str:
```

## 39. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls figuras mapas tablas; grep -n \"pobreza_area\\|Figura\" -r .claude/skills/graficando-enaho/scripts/graficar.py | head -8; sed -n 1,12p .claude/skills/informando-investigacion/scripts/publicar.py"
}
```

## 40. Resultado

**Resultado de la herramienta:**

```
figuras:
inflacion_2019_2024.png
pobreza_area.png
pobreza_departamento.png
pobreza_dominio.png
pobreza_edad.png
pobreza_extrema_area.png
pobreza_region_natural.png
pobreza_sexo.png
pobreza_sexo_jefe.png

mapas:
pobreza_departamento.png

tablas:
inflacion_2019_2024.csv
pobreza_area.csv
pobreza_departamento.csv
pobreza_dominio.csv
pobreza_edad.csv
pobreza_extrema_area.csv
pobreza_region_natural.csv
pobreza_sexo.csv
pobreza_sexo_jefe.csv
41:             "pobreza_area.png", ["Urbana", "Rural"]),
127:    print(f"Figura {numero}: {ruta.relative_to(RAIZ)}  |  tabla: tablas/{archivo.replace('.png', '.csv')}")
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
```

## 41. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "head -3 tablas/inflacion_2019_2024.csv; grep -n \"bcrp_\" .claude/skills/informando-investigacion/scripts/publicar.py | head"
}
```

## 42. Resultado

**Resultado de la herramienta:**

```
codigo,periodo,valor,nombre,fuente
PN01273PM,2019-01,2.12915785051415,Índice de precios Lima Metropolitana (var% 12 meses) - IPC,https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12
PN01273PM,2019-02,2.00338485500231,Índice de precios Lima Metropolitana (var% 12 meses) - IPC,https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12
10:                               series del BCRP guardadas en tablas/bcrp_*.csv y tabla de validación.
115:    for csv in sorted((RAIZ / "tablas").glob("bcrp_*.csv")):
158:<code>salidas/indicadores.csv</code> y de las tablas <code>tablas/bcrp_*.csv</code>.</p>
```

## 43. Asistente (Claude)

Ahora el plan, el informe y las afirmaciones.

## 44. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cp tablas/inflacion_2019_2024.csv tablas/bcrp_ipc.csv\ncat > informes/plan.md <<'EOF'\n# Plan de investigación\n\n**Pregunta.** ¿Cómo evolucionaron la inflación y la actividad económica del Perú entre 2019 y 2024, y qué brechas territoriales (departamentos; urbano–rural) presentaba la pobreza monetaria en 2024?\n\n**Objetivo.** Describir la trayectoria macroeconómica 2019-2024 y medir las brechas de pobreza monetaria de 2024.\n\n**Delimitación.** Periodo 2019-2024 (BCRP, series nacionales/Lima Metropolitana); corte transversal 2024 (ENAHO); unidad: personas; 25 departamentos (Lima y Callao separados) y área urbana/rural.\n\n**Qué responde cada fuente.**\n- BCRP: inflación (IPC Lima Metropolitana, var. % 12 meses, mensual, PN01273PM; subyacente PN01279PM) y actividad (PBI global, millones S/ de 2007, trimestral, PN37692AQ).\n- ENAHO 2024 (INEI): pobreza monetaria ponderada (factor07 × mieperho) por área y departamento, con IC 95 % y CV.\n\n**Alcance analítico.** La comparación es descriptiva, no causal; los niveles de agregación difieren (nacional/Lima vs. departamentos 2024).\n\n**Herramientas.** MCP bcrp: buscar_series, resumen_anual, resumen, comparar_series, graficar_serie. Skills: limpiando-enaho, graficando-enaho, mapeando-enaho, informando-investigacion.\nEOF\ncat > informes/informe_final.md <<'EOF'\n# Inflación, actividad económica y brechas territoriales de la pobreza monetaria en el Perú, 2019-2024\n\n## Pregunta de investigación\n\n**Tema.** Evolución macroeconómica del Perú (2019-2024) y desigualdad territorial de la pobreza monetaria en 2024.\n\n**Objetivo.** Describir cómo evolucionaron la inflación y la actividad económica entre 2019 y 2024 y medir las brechas de pobreza monetaria entre departamentos y entre áreas urbana y rural en 2024.\n\n**Delimitación.** Periodo 2019-2024 para las series del BCRP; corte transversal 2024 para la ENAHO; unidad de análisis: personas residentes en hogares particulares; 25 unidades departamentales (Lima y Callao por separado).\n\n## Fuentes y metodología\n\n**BCRP** (Banco Central de Reserva del Perú [BCRP], 2026), consultado mediante el servidor MCP del proyecto: PN01273PM (IPC de Lima Metropolitana, variación % a 12 meses, mensual), PN01279PM (IPC subyacente) y PN37692AQ (PBI global, millones de S/ de 2007, trimestral). Fuente de las consultas: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/...`.\n\n**ENAHO 2024** (Instituto Nacional de Estadística e Informática [INEI], 2025a): módulos 34 (sumaria) y 02 (miembros), 33 691 hogares y 108 664 personas. La pobreza monetaria se estima con ponderador factor07 × mieperho (método INEI), con error estándar, IC 95 % y coeficiente de variación (CV); se advierte cuando CV > 15 %. La limpieza pasó 18 de 18 validaciones, incluida la coincidencia de los 25 departamentos con la referencia oficial (INEI, 2025b).\n\n## Resultados\n\n**Hallazgo 1. La inflación subió con fuerza en 2021-2022 y regresó al rango meta en 2024.** La inflación a 12 meses (PN01273PM) cerró diciembre en 1.90 % (2019), 1.97 % (2020), 6.43 % (2021), 8.46 % (2022), 3.24 % (2023) y 1.97 % (2024); el máximo mensual del periodo anual 2022 fue 8.81 % (junio) y en enero de 2023 llegó a 8.66 % (Tabla 1, Figura 1). La inflación subyacente (PN01279PM) promedió 3.55 % frente a 4.08 % de la total en 2019-2024 (diferencia promedio 0.52 p.p.; correlación de niveles 0.89, descriptiva).\n\n**Tabla 1**\n\n*Inflación anual de Lima Metropolitana, 2019-2024 (PN01273PM)*\n\n| Año | Promedio anual (%) | Diciembre (%) |\n|---|---|---|\n| 2019 | 2.14 | 1.90 |\n| 2020 | 1.83 | 1.97 |\n| 2021 | 3.97 | 6.43 |\n| 2022 | 7.86 | 8.46 |\n| 2023 | 6.31 | 3.24 |\n| 2024 | 2.35 | 1.97 |\n\n*Nota.* Variación porcentual a 12 meses del IPC de Lima Metropolitana. Fuente: BCRP, serie PN01273PM, 2019-2024 (`resumen_anual`).\n\n**Hallazgo 2. La actividad cayó en 2020, se recuperó y en 2024 superó el nivel prepandemia.** El PBI global (PN37692AQ) tuvo un mínimo trimestral de 
... [5666 caracteres omitidos]
```

## 45. Resultado

**Resultado de la herramienta:**

```
Exit code 2
/usr/bin/bash: -c: line 19: unexpected EOF while looking for matching `''
```

## 46. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\plan.md",
 "content": "# Plan de investigación\n\n**Pregunta.** ¿Cómo evolucionaron la inflación y la actividad económica del Perú entre 2019 y 2024, y qué brechas territoriales (departamentos; urbano–rural) presentaba la pobreza monetaria en 2024?\n\n**Objetivo.** Describir la trayectoria macroeconómica 2019-2024 y medir las brechas de pobreza monetaria de 2024.\n\n**Delimitación.** Periodo 2019-2024 (BCRP, series nacionales/Lima Metropolitana); corte transversal 2024 (ENAHO); unidad: personas; 25 departamentos (Lima y Callao separados) y área urbana/rural.\n\n**Qué responde cada fuente.**\n- BCRP: inflación (IPC Lima Metropolitana, var. % 12 meses, mensual, PN01273PM; subyacente PN01279PM) y actividad (PBI global, millones S/ de 2007, trimestral, PN37692AQ).\n- ENAHO 2024 (INEI): pobreza monetaria ponderada (factor07 × mieperho) por área y departamento, con IC 95 % y CV.\n\n**Alcance analítico.** La comparación es descriptiva, no causal; los niveles de agregación difieren (nacional/Lima vs. departamentos 2024).\n\n**Herramientas.** MCP bcrp: buscar_series, resumen_anual, resumen, comparar_series, graficar_serie. Skills: limpiando-enaho, graficando-enaho, mapeando-enaho, informando-investigacion.\n"
}
```

## 47. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\plan.md (file state is current in your context — no need to Read it back)
```

## 48. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\afirmaciones.csv",
 "content": "id,afirmacion,fuente,codigo,periodo,agregacion,valor_informe,tolerancia\nf1,\"Inflación de diciembre de 2022 (8.46 %)\",bcrp,PN01273PM,2022-12,valor,8.46,0.01\nf2,\"Inflación de diciembre de 2024 (1.97 %)\",bcrp,PN01273PM,2024-12,valor,1.97,0.01\nf3,\"Inflación promedio de 2021 (3.97 %)\",bcrp,PN01273PM,2021,promedio,3.97,0.01\nf4,\"Pobreza rural (39.30 %)\",enaho,area,Rural,pobreza_monetaria,39.30,0.05\nf5,\"Pobreza urbana (24.81 %)\",enaho,area,Urbana,pobreza_monetaria,24.81,0.05\nf6,\"Pobreza nacional (27.58 %)\",enaho,nacional,Perú,pobreza_monetaria,27.58,0.05\n"
}
```

## 49. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\afirmaciones.csv (file state is current in your context — no need to Read it back)
```

## 50. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\informe_final.md",
 "content": "# Inflación, actividad económica y brechas territoriales de la pobreza monetaria en el Perú, 2019-2024\n\n## Pregunta de investigación\n\n**Tema.** Evolución macroeconómica del Perú (2019-2024) y desigualdad territorial de la pobreza monetaria en 2024.\n\n**Objetivo.** Describir cómo evolucionaron la inflación y la actividad económica entre 2019 y 2024 y medir las brechas de pobreza monetaria entre departamentos y entre áreas urbana y rural en 2024.\n\n**Delimitación.** Periodo 2019-2024 para las series del BCRP; corte transversal 2024 para la ENAHO; unidad de análisis: personas residentes en hogares particulares; 25 unidades departamentales (Lima y Callao por separado).\n\n## Fuentes y metodología\n\n**BCRP** (Banco Central de Reserva del Perú [BCRP], 2026), consultado mediante el servidor MCP del proyecto: PN01273PM (IPC de Lima Metropolitana, variación % a 12 meses, mensual), PN01279PM (IPC subyacente) y PN37692AQ (PBI global, millones de S/ de 2007, trimestral). Fuente de las consultas: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/...`.\n\n**ENAHO 2024** (Instituto Nacional de Estadística e Informática [INEI], 2025a): módulos 34 (sumaria) y 02 (miembros), 33 691 hogares y 108 664 personas. La pobreza monetaria se estima con ponderador factor07 × mieperho (método INEI), con error estándar, IC 95 % y coeficiente de variación (CV); se advierte cuando CV > 15 %. La limpieza pasó 18 de 18 validaciones, incluida la coincidencia de los 25 departamentos con la referencia oficial (INEI, 2025b).\n\n## Resultados\n\n**Hallazgo 1. La inflación subió con fuerza en 2021-2022 y regresó a un nivel bajo en 2024.** La inflación a 12 meses (PN01273PM) cerró diciembre en 1.90 % (2019), 1.97 % (2020), 6.43 % (2021), 8.46 % (2022), 3.24 % (2023) y 1.97 % (2024); el máximo mensual de 2022 fue 8.81 % (junio) y en enero de 2023 llegó a 8.66 % (Tabla 1, Figura 1). La inflación subyacente (PN01279PM) promedió 3.55 % frente a 4.08 % de la total en 2019-2024 (diferencia promedio 0.52 p.p.; correlación de niveles 0.89, descriptiva).\n\n**Tabla 1**\n\n*Inflación anual de Lima Metropolitana, 2019-2024 (PN01273PM)*\n\n| Año | Promedio anual (%) | Diciembre (%) |\n|---|---|---|\n| 2019 | 2.14 | 1.90 |\n| 2020 | 1.83 | 1.97 |\n| 2021 | 3.97 | 6.43 |\n| 2022 | 7.86 | 8.46 |\n| 2023 | 6.31 | 3.24 |\n| 2024 | 2.35 | 1.97 |\n\n*Nota.* Variación porcentual a 12 meses del IPC de Lima Metropolitana. Fuente: BCRP, serie PN01273PM, 2019-2024 (`resumen_anual`).\n\n**Hallazgo 2. La actividad cayó en 2020, se recuperó y en 2024 superó el nivel prepandemia.** El PBI global (PN37692AQ) tuvo un mínimo trimestral de S/ 95 976 millones de 2007 en 2020-T2 y un promedio trimestral de 121 711 en 2020, frente a 136 651 en 2019. En 2024 el promedio trimestral fue de 146 405 y el valor de 2024-T4, 155 868; entre 2019-T4 y 2024-T4 la variación fue de 8.35 % (Tabla 2).\n\n**Tabla 2**\n\n*PBI global trimestral, promedio por año, 2019-2024 (PN37692AQ)*\n\n| Año | Promedio trimestral (millones S/ de 2007) |\n|---|---|\n| 2019 | 136 651 |\n| 2020 | 121 711 |\n| 2021 | 138 040 |\n| 2022 | 141 931 |\n| 2023 | 141 433 |\n| 2024 | 146 405 |\n\n*Nota.* Fuente: BCRP, serie PN37692AQ, 2019-T1 a 2024-T4 (`resumen_anual`).\n\n**Hallazgo 3. En 2024 la pobreza rural superó a la urbana por unos 14.5 puntos porcentuales.** La pobreza monetaria nacional fue 27.58 % (IC 95 %: 26.59-28.57). En el área rural fue 39.30 % (IC 95 %: 37.80-40.81) y en la urbana 24.81 % (IC 95 %: 23.62-25.99); los intervalos no se superponen, por lo que la diferencia es estadísticamente distinguible (Tabla 3, Figura 2). La pobreza extrema fue 15.52 % en el área rural y 3.14 % en la urbana.\n\n**Tabla 3**\n\n*Pobreza monetaria por área, 2024*\n\n| Área | Pobreza (%) | IC 95 % | CV (%) |\n|---|---|---|---|\n| Urbana | 24.81 | 23.62-25.99 | 2.4 |\n| Rural | 39.30 | 37.80-40.81 | 2.0 |\n\n*Nota.* Fu
... [3632 caracteres omitidos]
```

## 51. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\informe_final.md (file state is current in your context — no need to Read it back)
```

## 52. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cp tablas/inflacion_2019_2024.csv tablas/bcrp_ipc.csv; uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv 2>&1 | tail -15",
 "timeout": 500000
}
```

## 53. Resultado

**Resultado de la herramienta:**

```
**Tabla 1**

*Comparación entre las cifras del informe y su verificación independiente*

| Id | Afirmación | Informe | Verificado | Diferencia | Tolerancia | Coincide | Procedimiento |
|:---|:---|---:|---:|---:|---:|:---:|:---|
| f1 | Inflación de diciembre de 2022 (8.46 %) | 8.46 | 8.4592 | 0.0008 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-12/2022-12 |
| f2 | Inflación de diciembre de 2024 (1.97 %) | 1.97 | 1.9663 | 0.0037 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2024-12/2024-12 |
| f3 | Inflación promedio de 2021 (3.97 %) | 3.97 | 3.9724 | -0.0024 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2021-12 |
| f4 | Pobreza rural (39.30 %) | 39.3 | 39.302799224853516 | -0.00279999990016222 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f5 | Pobreza urbana (24.81 %) | 24.81 | 24.80699920654297 | 0.003000000026077032 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f6 | Pobreza nacional (27.58 %) | 27.58 | 27.579500198364258 | 0.0005000000237487257 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |

*Nota.* 6 de 6 afirmaciones coinciden dentro de la tolerancia definida antes de verificar. Diferencia = valor del informe menos valor verificado.
```

## 54. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/informando-investigacion/scripts/publicar.py 2>&1 | tail -8",
 "timeout": 500000
}
```

## 55. Resultado

**Resultado de la herramienta:**

```
Informe HTML: informes\informe_final.html
Tablero: informes\dashboard.html
```

## 56. Asistente (Claude)

Completé el flujo y escribí el informe en `informes/informe_final.md`. La verificación independiente coincidió en las 6 cifras que revisé (3 del BCRP y 3 de la ENAHO), y publiqué las versiones HTML.

## Hallazgos

1. **Inflación (BCRP, PN01273PM, Lima Metropolitana):** la variación a 12 meses cerró diciembre en 1.90 % en 2019, 6.43 % en 2021, 8.46 % en 2022, 3.24 % en 2023 y 1.97 % en 2024. El pico fue 8.81 % en junio de 2022.
2. **Actividad (PN37692AQ, PBI global):** el mínimo trimestral fue S/ 95 976 millones de 2007 en 2020-T2. Entre 2019-T4 y 2024-T4 el PBI subió 8.35 %, así que en 2024 superó el nivel prepandemia.
3. **Pobreza urbano-rural en 2024 (ENAHO):** la pobreza monetaria nacional fue 27.58 %. En el área rural fue 39.30 % (IC 95 %: 37.80–40.81) y en la urbana 24.81 % (23.62–25.99). Los intervalos no se superponen, así que la brecha de unos 14.5 puntos es distinguible.
4. **Pobreza entre departamentos en 2024:** va de Ica (6.01 %) a Cajamarca (45.01 %), con intervalos que no se superponen. Ica, Moquegua y Madre de Dios tienen CV > 15 %, por lo que sus estimaciones son menos precisas.

La relación entre los datos macroeconómicos y la pobreza se presenta como descriptiva, no causal.

## Verificación y limitaciones
- **Validación de la ENAHO:** la limpieza pasó 18 de 18 validaciones. El mapa departamental coincide con la referencia oficial en los 25 departamentos.
- **Búsqueda sin resultados:** no encontré una serie de variación % del PBI. Usé el PBI en niveles y no calculé tasas anuales a mano.
- **Herramientas:** ninguna herramienta del MCP falló.
- **Datos regenerados:** las salidas de `salidas/`, `figuras/` y `tablas/` estaban borradas en el repositorio; las regeneré.

## Archivos
- **Informes:** `informes/plan.md`, `informe_final.md` y `informe_final.html`, más `dashboard.html`.
- **Verificación:** `informes/afirmaciones.csv`, `verificacion.md` y `verificacion.csv`.
- **Figuras y mapa:** `figuras/inflacion_2019_2024.png`, `figuras/pobreza_area.png` y `mapas/pobreza_departamento.png`.
- **Datos:** `tablas/*.csv` y `salidas/indicadores.csv`.

Usé las herramientas del MCP `buscar_series`, `resumen_anual`, `resumen`, `comparar_series` y `graficar_serie`. También usé las skills `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho` e `informando-investigacion`.

No hice ningún commit.

## Resultado final

- Turnos: 28
- Duración: 137 s
- Error: False

Completé el flujo y escribí el informe en `informes/informe_final.md`. La verificación independiente coincidió en las 6 cifras que revisé (3 del BCRP y 3 de la ENAHO), y publiqué las versiones HTML.

## Hallazgos

1. **Inflación (BCRP, PN01273PM, Lima Metropolitana):** la variación a 12 meses cerró diciembre en 1.90 % en 2019, 6.43 % en 2021, 8.46 % en 2022, 3.24 % en 2023 y 1.97 % en 2024. El pico fue 8.81 % en junio de 2022.
2. **Actividad (PN37692AQ, PBI global):** el mínimo trimestral fue S/ 95 976 millones de 2007 en 2020-T2. Entre 2019-T4 y 2024-T4 el PBI subió 8.35 %, así que en 2024 superó el nivel prepandemia.
3. **Pobreza urbano-rural en 2024 (ENAHO):** la pobreza monetaria nacional fue 27.58 %. En el área rural fue 39.30 % (IC 95 %: 37.80–40.81) y en la urbana 24.81 % (23.62–25.99). Los intervalos no se superponen, así que la brecha de unos 14.5 puntos es distinguible.
4. **Pobreza entre departamentos en 2024:** va de Ica (6.01 %) a Cajamarca (45.01 %), con intervalos que no se superponen. Ica, Moquegua y Madre de Dios tienen CV > 15 %, por lo que sus estimaciones son menos precisas.

La relación entre los datos macroeconómicos y la pobreza se presenta como descriptiva, no causal.

## Verificación y limitaciones
- **Validación de la ENAHO:** la limpieza pasó 18 de 18 validaciones. El mapa departamental coincide con la referencia oficial en los 25 departamentos.
- **Búsqueda sin resultados:** no encontré una serie de variación % del PBI. Usé el PBI en niveles y no calculé tasas anuales a mano.
- **Herramientas:** ninguna herramienta del MCP falló.
- **Datos regenerados:** las salidas de `salidas/`, `figuras/` y `tablas/` estaban borradas en el repositorio; las regeneré.

## Archivos
- **Informes:** `informes/plan.md`, `informe_final.md` y `informe_final.html`, más `dashboard.html`.
- **Verificación:** `informes/afirmaciones.csv`, `verificacion.md` y `verificacion.csv`.
- **Figuras y mapa:** `figuras/inflacion_2019_2024.png`, `figuras/pobreza_area.png` y `mapas/pobreza_departamento.png`.
- **Datos:** `tablas/*.csv` y `salidas/indicadores.csv`.

Usé las herramientas del MCP `buscar_series`, `resumen_anual`, `resumen`, `comparar_series` y `graficar_serie`. También usé las skills `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho` e `informando-investigacion`.

No hice ningún commit.
