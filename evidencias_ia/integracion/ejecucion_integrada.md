# Ejecución integrada definitiva: MCP del BCRP + Skills de ENAHO

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

Invoca cada skill con la herramienta `Skill` (no ejecutes sus scripts sin cargarla), para que sus reglas se
apliquen y quede registro de la coordinación:

1. `limpiando-enaho`: si no existe `salidas/indicadores.csv`, invócala y confirma la validación.
2. `graficando-enaho`: al menos un gráfico (p. ej. `--tipo area` o `--tipo departamento`).
3. `mapeando-enaho`: el mapa departamental.
4. Toma las cifras de `salidas/indicadores.csv` con su IC 95 %; si los IC se superponen, no afirmes diferencia.

**Numeración de figuras.** Decide primero el orden de las figuras del informe y pasa a cada script o herramienta
su número (`--numero n` o `numero_figura`). No uses `--tipo todos` para el informe: renumeraría las figuras desde
1. Cada PNG ya contiene número, título y nota APA, por lo que en el Markdown solo se inserta la imagen
(`![Figura n](../figuras/archivo.png)`), sin repetir el pie.

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

**Herramienta:** `Bash`

```json
{
 "command": "ls; ls salidas informes figuras tablas 2>&1 | head -30; ls .claude/skills/*/scripts; sed -n 1,40p .claude/skills/informando-investigacion/scripts/verificar.py; grep -n \"REFERENCIAS_APA\" -A25 comun/apa.py | head -50"
}
```

## 5. Asistente (Claude)

**Herramienta:** `ToolSearch`

```json
{
 "query": "select:mcp__bcrp__buscar_series,mcp__bcrp__resumen_anual,mcp__bcrp__resumen,mcp__bcrp__comparar_series,mcp__bcrp__graficar_serie",
 "max_results": 5
}
```

## 6. Resultado

**Resultado de la herramienta:**

```
[imagen]
[imagen]
[imagen]
[imagen]
[imagen]
```

## 7. Resultado

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
tests
uv.lock
figuras:

informes:

salidas:

tablas:
.claude/skills/graficando-enaho/scripts:
graficar.py

.claude/skills/informando-investigacion/scripts:
publicar.py
verificar.py

.claude/skills/limpiando-enaho/scripts:
__pycache__
descargar.py
limpiar.py

.claude/skills/mapeando-enaho/scripts:
mapear.py
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
```

## 8. Asistente (Claude)

**Herramienta:** `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc 12 meses",
 "limite": 5
}
```

## 9. Asistente (Claude)

**Herramienta:** `mcp__bcrp__buscar_series`

```json
{
 "texto": "producto bruto interno",
 "limite": 10
}
```

## 10. Resultado

**Resultado de la herramienta:**

```
{"result":[{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1950","actualizada":"2026-10-08"},{"codigo":"PN09821PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Importado","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01281PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01283PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"}]}
```

## 11. Resultado

**Resultado de la herramienta:**

```
{"result":[{"codigo":"PN02509AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Pesca","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37685AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Pesca","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02514AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Comercio","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02515AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Servicios","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02516AQ","nombre":"Producto bruto interno (índice 2007 = 100) - PBI Global","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37690AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Comercio","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02511AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Manufactura","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN37691AQ","nombre":"Producto bruto interno (millones S/ de 2007) - Servicios","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02508AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Agropecuario","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"},{"codigo":"PN02513AQ","nombre":"Producto bruto interno (índice 2007 = 100) - Construcción","categoria":"PBI por sectores","frecuencia":"Trimestral","inicio":"T1-1980","actualizada":"2026-08-20"}]}
```

## 12. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen_anual`

```json
{
 "codigo": "PN01273PM",
 "desde_anio": 2019,
 "hasta_anio": 2024
}
```

## 13. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","anios":[{"anio":2019,"promedio":2.136886,"fin_de_periodo":{"periodo":"2019-12","valor":1.900092},"maximo":{"periodo":"2019-05","valor":2.725128},"minimo":{"periodo":"2019-09","valor":1.851007},"n":12,"completo":true},{"anio":2020,"promedio":1.827263,"fin_de_periodo":{"periodo":"2020-12","valor":1.973232},"maximo":{"periodo":"2020-11","valor":2.14221},"minimo":{"periodo":"2020-06","valor":1.598732},"n":12,"completo":true},{"anio":2021,"promedio":3.972447,"fin_de_periodo":{"periodo":"2021-12","valor":6.430387},"maximo":{"periodo":"2021-12","valor":6.430387},"minimo":{"periodo":"2021-04","valor":2.383698},"n":12,"completo":true},{"anio":2022,"promedio":7.864561,"fin_de_periodo":{"periodo":"2022-12","valor":8.459162},"maximo":{"periodo":"2022-06","valor":8.812633},"minimo":{"periodo":"2022-01","valor":5.684917},"n":12,"completo":true},{"anio":2023,"promedio":6.312536,"fin_de_periodo":{"periodo":"2023-12","valor":3.237383},"maximo":{"periodo":"2023-01","valor":8.664267},"minimo":{"periodo":"2023-12","valor":3.237383},"n":12,"completo":true},{"anio":2024,"promedio":2.354973,"fin_de_periodo":{"periodo":"2024-12","valor":1.966303},"maximo":{"periodo":"2024-02","valor":3.294067},"minimo":{"periodo":"2024-09","valor":1.775011},"n":12,"completo":true}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12","nota":"Promedio = media aritmética de las observaciones del año; fin de periodo = última observación."}
```

## 14. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen_anual`

```json
{
 "codigo": "PN02516AQ",
 "desde_anio": 2019,
 "hasta_anio": 2024
}
```

## 15. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen`

```json
{
 "codigo": "PN01273PM",
 "desde": "2019-01",
 "hasta": "2024-12"
}
```

## 16. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","n":72,"primero":{"periodo":"2019-01","valor":2.129158},"ultimo":{"periodo":"2024-12","valor":1.966303},"cambio":-0.162855,"variacion_pct":-7.648806,"promedio":4.078111,"desviacion_estandar":2.543611,"maximo":{"periodo":"2022-06","valor":8.812633},"minimo":{"periodo":"2020-06","valor":1.598732},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12"}
```

## 17. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN02516AQ","nombre":"Producto bruto interno (índice 2007 = 100) - PBI Global","frecuencia":"Trimestral","anios":[{"anio":2019,"promedio":170.978095,"fin_de_periodo":{"periodo":"2019-T4","valor":180.000209},"maximo":{"periodo":"2019-T4","valor":180.000209},"minimo":{"periodo":"2019-T1","valor":159.56927},"n":4,"completo":true},{"anio":2020,"promedio":152.284536,"fin_de_periodo":{"periodo":"2020-T4","valor":177.515674},"maximo":{"periodo":"2020-T4","valor":177.515674},"minimo":{"periodo":"2020-T2","valor":120.085017},"n":4,"completo":true},{"anio":2021,"promedio":172.716012,"fin_de_periodo":{"periodo":"2021-T4","valor":183.664699},"maximo":{"periodo":"2021-T4","valor":183.664699},"minimo":{"periodo":"2021-T1","valor":160.373532},"n":4,"completo":true},{"anio":2022,"promedio":177.583494,"fin_de_periodo":{"periodo":"2022-T4","valor":187.345534},"maximo":{"periodo":"2022-T4","valor":187.345534},"minimo":{"periodo":"2022-T1","valor":166.679443},"n":4,"completo":true},{"anio":2023,"promedio":176.960709,"fin_de_periodo":{"periodo":"2023-T4","valor":186.727299},"maximo":{"periodo":"2023-T4","valor":186.727299},"minimo":{"periodo":"2023-T1","valor":166.645195},"n":4,"completo":true},{"anio":2024,"promedio":183.181365,"fin_de_periodo":{"periodo":"2024-T4","valor":195.022579},"maximo":{"periodo":"2024-T4","valor":195.022579},"minimo":{"periodo":"2024-T1","valor":169.127703},"n":4,"completo":true}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN02516AQ/json/2019-1/2024-4","nota":"Promedio = media aritmética de las observaciones del año; fin de periodo = última observación."}
```

## 18. Asistente (Claude)

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
 "etiqueta_referencia": "Límite superior del rango meta (3 %)",
 "archivo": "inflacion_2019_2024.png",
 "numero_figura": 1
}
```

## 19. Asistente (Claude)

**Herramienta:** `mcp__bcrp__graficar_serie`

```json
{
 "codigos": [
  "PN02516AQ"
 ],
 "desde": "2019-T1",
 "hasta": "2024-T4",
 "titulo": "Producto bruto interno trimestral del Perú (índice 2007 = 100), 2019-2024",
 "archivo": "pbi_2019_2024.png",
 "numero_figura": 2
}
```

## 20. Asistente (Claude)

**Herramienta:** `mcp__bcrp__resumen`

```json
{
 "codigo": "PN02516AQ",
 "desde": "2019-T4",
 "hasta": "2024-T4"
}
```

## 21. Resultado

**Resultado de la herramienta:**

```
{"archivo":"figuras/inflacion_2019_2024.png","datos":"tablas/inflacion_2019_2024.csv","codigos":["PN01273PM"],"desde":"2019-01","hasta":"2024-12","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-1/2024-12"]}
```

## 22. Resultado

**Resultado de la herramienta:**

```
{"archivo":"figuras/pbi_2019_2024.png","datos":"tablas/pbi_2019_2024.csv","codigos":["PN02516AQ"],"desde":"2019-T1","hasta":"2024-T4","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN02516AQ/json/2019-1/2024-4"]}
```

## 23. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN02516AQ","nombre":"Producto bruto interno (índice 2007 = 100) - PBI Global","frecuencia":"Trimestral","n":21,"primero":{"periodo":"2019-T4","valor":180.000209},"ultimo":{"periodo":"2024-T4","valor":195.022579},"cambio":15.022369,"variacion_pct":8.345751,"promedio":172.900222,"desviacion_estandar":15.95927,"maximo":{"periodo":"2024-T4","valor":195.022579},"minimo":{"periodo":"2020-T2","valor":120.085017},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN02516AQ/json/2019-4/2024-4"}
```

## 24. Asistente (Claude)

Datos del BCRP listos y dos figuras generadas; ahora cargo la skill de limpieza de la ENAHO.

## 25. Asistente (Claude)

**Herramienta:** `Skill`

```json
{
 "skill": "limpiando-enaho"
}
```

## 26. Resultado

**Resultado de la herramienta:**

```
Launching skill: limpiando-enaho
```

## 27. Usuario

Base directory for this skill: C:/Users/[usuario]\Documents\tarea_4\.claude\skills\limpiando-enaho

# Limpiar y validar la ENAHO 2024

Esta skill es la base del sistema: las skills `graficando-enaho`, `mapeando-enaho` e `informando-investigacion`
consumen lo que produce. Toda cifra de ENAHO del proyecto sale de aquí; nunca se escriben cifras a mano.

## Pasos

1. Si faltan `datos/966-Modulo34.zip` o `datos/966-Modulo02.zip`, descárgalos (código 966 = ENAHO 2024):

   ```bash
   uv run .claude/skills/limpiando-enaho/scripts/descargar.py
   ```

2. Ejecuta exactamente (añade `--forzar` solo si piden rehacer la base):

   ```bash
   uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 
   ```

3. Lee `salidas/validacion.txt`. Si dice `FALLO DE VALIDACION ESENCIAL`, detente e informa cuál verificación
   falló. No ajustes filtros, ponderadores ni cifras para forzar la coincidencia con el INEI.
4. Responde con las cifras de `salidas/indicadores.csv` (columna `valor_pct`, con su IC 95 % y CV), citando
   "INEI, ENAHO 2024" y el ponderador usado. Si el CV supera 15 %, advierte que la estimación es poco precisa.
5. Para una variable que no está en las bases, lee primero `reference.md` (diccionario y reglas).

## Qué produce

| Archivo | Contenido |
|---|---|
| `salidas/personas_2024.parquet` | 108,664 residentes habituales, una fila por persona, con `facpob07` |
| `salidas/hogares_2024.parquet` | 33,691 hogares, con `pondera = factor07 × mieperho` |
| `salidas/indicadores.csv` | Pobreza total y extrema por área, región, dominio, departamento, sexo, edad y jefatura |
| `salidas/validacion.txt` | 18 verificaciones, cada una APROBADA, FALLIDA o ADVERTENCIA |

## Reglas que el script aplica (no se discuten)

- Lectura con `convert_categoricals=False`; `conglome`, `vivienda`, `hogar`, `codperso` y `ubigeo` como texto.
- Residentes habituales: `((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))`.
- Unión personas-hogares por `conglome`, `vivienda`, `hogar` con `merge(..., validate="m:1")`, comprobando que
  no se pierdan ni dupliquen filas.
- `departamento = ubigeo[:2]`, `urbano = estrato <= 5`, `pobre = pobreza <= 2`, `pobre_extremo = pobreza == 1`.
- Indicadores territoriales con la sumaria y `factor07 × mieperho` (método oficial del INEI); indicadores
  individuales (sexo, edad) con personas y `facpob07`. Nunca promedios simples.
- Error estándar por linealización de Taylor con UPM `conglome` y estratos departamento × estrato.


## 28. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls datos && uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 2>&1 | tail -30; cat salidas/validacion.txt | tail -30",
 "timeout": 600000
}
```

## 29. Resultado

**Resultado de la herramienta:**

```
966-Modulo02.zip
966-Modulo34.zip
cache_bcrp
catalogo_bcrp.csv
peru_departamental_simple.geojson
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
           0 duplicados
[APROBADA] Residentes habituales
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
```

## 30. Asistente (Claude)

Validación 18/18. Ahora las skills de gráficos y mapa.

## 31. Asistente (Claude)

**Herramienta:** `Skill`

```json
{
 "skill": "graficando-enaho"
}
```

## 32. Resultado

**Resultado de la herramienta:**

```
Launching skill: graficando-enaho
```

## 33. Usuario

Base directory for this skill: C:/Users/[usuario]\Documents\tarea_4\.claude\skills\graficando-enaho

# Graficar la pobreza con la ENAHO 2024

1. Si no existen `salidas/personas_2024.parquet` y `salidas/indicadores.csv`, usa primero la skill
   `limpiando-enaho` (ejecuta `uv run .claude/skills/limpiando-enaho/scripts/limpiar.py`) y comprueba que su
   validación esté aprobada. Si el script de gráficos sale con código 2, es por esto.
2. Traduce el pedido a un tipo de gráfico:

   | Pedido | `--tipo` |
   |---|---|
   | urbano y rural, área de residencia | `area` |
   | hombres y mujeres, sexo, género | `sexo` |
   | niños, jóvenes, adultos mayores, edad | `edad` |
   | hogares con jefa o jefe | `sexo_jefe` |
   | costa, sierra, selva | `region` |
   | dominios, Lima Metropolitana | `dominio` |
   | departamentos, regiones, ranking territorial | `departamento` |
   | pobreza extrema | `extrema` |

3. Ejecuta, con el número APA que corresponda a la figura en el documento:

   ```bash
   uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo <tipo> --numero <n>
   ```

4. El script imprime la tabla de cifras (también guardada en `tablas/<figura>.csv`). Describe la figura solo con
   esas cifras e indica si los intervalos de confianza se superponen: si se superponen, no afirmes que hay una
   diferencia. No presentes asociaciones como causas.

## Reglas de visualización (las aplica el script)

- Estimaciones ponderadas (`factor07 × mieperho` para territorio y jefatura; `facpob07` para sexo y edad).
- Barras desde cero, un solo tono, valor escrito en cada barra, línea del promedio nacional.
- Barras de error con IC 95 % por linealización de Taylor.
- Figura APA 7: "Figura n" en negrita, título en cursiva, nota con unidad, método y fuente
  ("INEI, ENAHO 2024"). PNG a 200 dpi en `figuras/`.


## 34. Asistente (Claude)

**Herramienta:** `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

## 35. Resultado

**Resultado de la herramienta:**

```
Launching skill: mapeando-enaho
```

## 36. Usuario

Base directory for this skill: C:/Users/[usuario]\Documents\tarea_4\.claude\skills\mapeando-enaho

# Mapear la pobreza departamental

1. Si no existen `salidas/personas_2024.parquet` y `salidas/indicadores.csv`, usa primero la skill
   `limpiando-enaho` (`uv run .claude/skills/limpiando-enaho/scripts/limpiar.py`). Si el script de mapas sale con
   código 2, es por esto.
2. Ejecuta:

   ```bash
   uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero <n>
   ```

   Usa `--indicador pobreza_extrema` si piden pobreza extrema.
3. Lee `salidas/validacion_mapa.txt`: debe decir 25/25 unidades unidas y, para pobreza monetaria, 25/25
   coincidencias con `referencias/pobreza_departamento_2024.csv`. Si no, informa la diferencia; no la corrijas
   a mano.
4. Describe el mapa con las cifras de `salidas/indicadores.csv` (departamentos con mayor y menor pobreza y su
   IC 95 %). El GeoJSON se descarga solo si falta.

## Reglas (las aplica el script)

- Unión por código: `ubigeo[:2]` (texto con cero inicial) con `FIRST_IDDP`; nunca por nombre.
- 25 unidades con dato; Lima (15) y Callao (07) separados; Callao se etiqueta con línea guía.
- Escala secuencial de un solo tono, desde 0 y en cortes de 10 puntos; leyenda "% de personas".
- Figura APA 7 con número, título en cursiva y nota (método, llave de unión y fuente). PNG en `mapas/`.


## 37. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area --numero 3 2>&1 | tail -15; uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento --numero 4 2>&1 | tail -40; uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero 5 2>&1 | tail -10; cat salidas/validacion_mapa.txt | tail -8; ls figuras mapas tablas",
 "timeout": 600000
}
```

## 38. Resultado

**Resultado de la herramienta:**

```
Figura 3: figuras\pobreza_area.png  |  tabla: tablas/pobreza_area.csv
categoria  valor_pct  ee_pct  ic95_inf  ic95_sup  cv_pct  n_muestral  poblacion_expandida
   Urbana      24.81    0.60     23.62     25.99    2.43       22031             27887512
    Rural      39.30    0.77     37.80     40.81    1.96       11660              6595188
Figura 4: figuras\pobreza_departamento.png  |  tabla: tablas/pobreza_departamento.csv
    categoria  valor_pct  ee_pct  ic95_inf  ic95_sup  cv_pct  n_muestral  poblacion_expandida
          Ica       6.01    0.94      4.17      7.85   15.61        1500               854203
     Moquegua      10.97    1.78      7.48     14.46   16.23         963               198386
Madre de Dios      11.15    2.17      6.89     15.41   19.50         603               165992
   Lambayeque      14.04    1.87     10.37     17.71   13.34        1302              1349731
     Arequipa      15.78    1.56     12.73     18.84    9.87        1506              1421684
        Junín      18.50    1.82     14.92     22.08    9.87        1506              1450149
        Cusco      18.54    1.95     14.72     22.36   10.52        1230              1409467
   San Martín      22.02    1.99     18.12     25.92    9.04        1347               947446
       Áncash      22.78    1.84     19.16     26.39    8.09        1393              1212494
     Apurímac      23.96    2.30     19.45     28.47    9.61         913               494188
        Tacna      23.99    2.86     18.38     29.60   11.94        1271               380755
     Amazonas      25.75    2.46     20.92     30.58    9.57        1243               442355
       Tumbes      26.90    2.45     22.10     31.70    9.10         842               261959
         Lima      27.07    1.20     24.71     29.43    4.45        4544             11279908
      Ucayali      27.07    2.20     22.76     31.38    8.12        1119               558484
  La Libertad      30.19    1.83     26.61     33.77    6.05        1509              2080789
        Piura      31.86    1.65     28.62     35.10    5.19        1611              1988570
     Ayacucho      32.76    2.24     28.36     37.16    6.85        1160               775447
 Huancavelica      33.40    2.19     29.12     37.69    6.55        1042               543103
       Callao      33.86    2.40     29.16     38.56    7.08        1027              1142618
      Huánuco      38.96    2.54     33.98     43.94    6.52        1244               926653
        Pasco      38.97    2.53     34.01     43.94    6.50         865               327776
         Puno      39.94    2.30     35.43     44.45    5.76        1123              1586886
       Loreto      42.97    2.12     38.81     47.13    4.94        1359              1129071
    Cajamarca      45.01    2.12     40.84     49.17    4.72        1469              1554586
  19 PASCO           calculado  39.0  referencia  39.0  dif +0.0
  20 PIURA           calculado  31.9  referencia  31.9  dif +0.0
  21 PUNO            calculado  39.9  referencia  39.9  dif +0.0
  22 SAN MARTIN      calculado  22.0  referencia  22.0  dif +0.0
  23 TACNA           calculado  24.0  referencia  24.0  dif +0.0
  24 TUMBES          calculado  26.9  referencia  26.9  dif +0.0
  25 UCAYALI         calculado  27.1  referencia  27.1  dif +0.0
RESULTADO: APROBADA

Mapa: mapas\pobreza_departamento.png (25 unidades territoriales)
  19 PASCO           calculado  39.0  referencia  39.0  dif +0.0
  20 PIURA           calculado  31.9  referencia  31.9  dif +0.0
  21 PUNO            calculado  39.9  referencia  39.9  dif +0.0
  22 SAN MARTIN      calculado  22.0  referencia  22.0  dif +0.0
  23 TACNA           calculado  24.0  referencia  24.0  dif +0.0
  24 TUMBES          calculado  26.9  referencia  26.9  dif +0.0
  25 UCAYALI         calculado  27.1  referencia  27.1  dif +0.0
RESULTADO: APROBADA
figuras:
inflacion_2019_2024.png
pbi_2019_2024.png
pobreza_area.p
... [153 caracteres omitidos]
```

## 39. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "mkdir -p informes && cat > informes/plan.md <<'EOF'\n# Plan de investigación\n\n## Pregunta reformulada\n¿Cómo evolucionaron la inflación (IPC de Lima Metropolitana) y la actividad económica (PBI trimestral) del Perú entre 2019 y 2024, y qué brechas territoriales (departamentos; urbano–rural) mostraba la pobreza monetaria en 2024?\n\n**Objetivo.** Describir la trayectoria macroeconómica 2019-2024 y cuantificar la desigualdad territorial de la pobreza monetaria en 2024.\n**Delimitación.** Periodo 2019-2024 (BCRP); corte transversal 2024 (ENAHO); nivel nacional, 25 departamentos (Lima y Callao separados) y área urbana/rural; unidad de análisis: personas (pobreza por gasto, ponderador `factor07 × mieperho`).\n\n## Qué responde cada fuente\n- **BCRP** (series nacionales): PN01273PM (inflación 12 meses, mensual) y PN02516AQ (PBI global, índice 2007 = 100, trimestral).\n- **ENAHO 2024, INEI** (personas y hogares): pobreza monetaria por área y departamento, con IC 95 %.\n- La comparación entre ambas es **descriptiva y no causal**: distintos niveles de agregación y periodos.\n\n## Herramientas\n- MCP `bcrp`: `buscar_series`, `resumen_anual`, `resumen`, `graficar_serie`.\n- Skills: `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho`, `informando-investigacion` (verificar.py, publicar.py).\n\n## Figuras\n1 inflación; 2 PBI; 3 pobreza por área; 4 pobreza por departamento; 5 mapa.\nEOF\ncat > informes/afirmaciones.csv <<'EOF'\nid,afirmacion,fuente,codigo,periodo,agregacion,valor_informe,tolerancia\nf1,Inflación de diciembre de 2022 (8.46 %),bcrp,PN01273PM,2022-12,valor,8.46,0.01\nf2,Inflación de diciembre de 2024 (1.97 %),bcrp,PN01273PM,2024-12,valor,1.97,0.01\nf3,Inflación promedio de 2022 (7.86 %),bcrp,PN01273PM,2022,promedio,7.86,0.01\nf4,Pobreza rural 2024 (39.30 %),enaho,area,Rural,pobreza_monetaria,39.3,0.05\nf5,Pobreza urbana 2024 (24.81 %),enaho,area,Urbana,pobreza_monetaria,24.81,0.05\nf6,Pobreza en Cajamarca 2024 (45.01 %),enaho,departamento,06,pobreza_monetaria,45.01,0.05\nEOF\nhead -3 tablas/inflacion_2019_2024.csv; grep -n \"REFERENCIAS\\|def \" comun/apa.py | head -20"
}
```

## 40. Resultado

**Resultado de la herramienta:**

```
Parser skipped input between top-level statements
```

## 41. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\plan.md",
 "content": "# Plan de investigación\n\n## Pregunta reformulada\n¿Cómo evolucionaron la inflación (IPC de Lima Metropolitana) y la actividad económica (PBI trimestral) del Perú entre 2019 y 2024, y qué brechas territoriales (departamentos; urbano–rural) mostraba la pobreza monetaria en 2024?\n\n**Objetivo.** Describir la trayectoria macroeconómica 2019-2024 y cuantificar la desigualdad territorial de la pobreza monetaria en 2024.\n\n**Delimitación.** Periodo 2019-2024 (BCRP); corte transversal 2024 (ENAHO); nivel nacional, 25 departamentos (Lima y Callao separados) y área urbana/rural; unidad de análisis: personas (ponderador `factor07 × mieperho`).\n\n## Qué responde cada fuente\n- **BCRP** (series nacionales): PN01273PM (inflación a 12 meses, mensual) y PN02516AQ (PBI global, índice 2007 = 100, trimestral).\n- **ENAHO 2024, INEI** (personas y hogares): pobreza monetaria por área y departamento, con IC 95 %.\n- La comparación entre ambas fuentes es **descriptiva y no causal**: difieren el nivel de agregación y el periodo.\n\n## Herramientas\n- MCP `bcrp`: `buscar_series`, `resumen_anual`, `resumen`, `graficar_serie`.\n- Skills: `limpiando-enaho`, `graficando-enaho`, `mapeando-enaho`, `informando-investigacion` (verificar.py, publicar.py).\n\n## Figuras\n1 inflación; 2 PBI; 3 pobreza por área; 4 pobreza por departamento; 5 mapa.\n"
}
```

## 42. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\plan.md (file state is current in your context — no need to Read it back)
```

## 43. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\afirmaciones.csv",
 "content": "id,afirmacion,fuente,codigo,periodo,agregacion,valor_informe,tolerancia\nf1,Inflación de diciembre de 2022 (8.46 %),bcrp,PN01273PM,2022-12,valor,8.46,0.01\nf2,Inflación de diciembre de 2024 (1.97 %),bcrp,PN01273PM,2024-12,valor,1.97,0.01\nf3,Inflación promedio de 2022 (7.86 %),bcrp,PN01273PM,2022,promedio,7.86,0.01\nf4,Pobreza rural 2024 (39.30 %),enaho,area,Rural,pobreza_monetaria,39.3,0.05\nf5,Pobreza urbana 2024 (24.81 %),enaho,area,Urbana,pobreza_monetaria,24.81,0.05\nf6,Pobreza en Cajamarca 2024 (45.01 %),enaho,departamento,06,pobreza_monetaria,45.01,0.05\n"
}
```

## 44. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\afirmaciones.csv (file state is current in your context — no need to Read it back)
```

## 45. Asistente (Claude)

**Herramienta:** `Write`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\informes\\informe_final.md",
 "content": "# Inflación, actividad económica y brechas territoriales de la pobreza en el Perú, 2019-2024\n\n## 1. Pregunta de investigación\n\n**Tema.** Evolución de la inflación y de la actividad económica del Perú entre 2019 y 2024, y brechas territoriales de la pobreza monetaria en 2024.\n\n**Objetivo.** Describir la trayectoria de ambas variables macroeconómicas y cuantificar la desigualdad de la pobreza entre departamentos y entre áreas urbana y rural al cierre del periodo.\n\n**Delimitación.** Series nacionales 2019-2024 (BCRP); corte transversal 2024 (ENAHO); 25 departamentos (Lima y Callao por separado); personas residentes habituales.\n\n## 2. Fuentes y metodología\n\n**BCRP** (Banco Central de Reserva del Perú, 2026): PN01273PM, inflación a 12 meses del IPC de Lima Metropolitana (mensual); PN02516AQ, PBI global, índice 2007 = 100 (trimestral). Cifras obtenidas con el servidor MCP (`resumen_anual`, `resumen`, `graficar_serie`).\n\n**ENAHO 2024** (Instituto Nacional de Estadística e Informática, 2025): módulos 34 (sumaria) y 02 (miembros), residentes habituales, pobreza monetaria (`pobreza ≤ 2`), ponderador `factor07 × mieperho`. Error estándar por linealización de Taylor (UPM `conglome`, estratos departamento × estrato); IC 95 %. La validación de la skill `limpiando-enaho` aprobó 18 de 18 verificaciones (nacional 27.58 %, IC 95 % 26.59-28.57; CV 1.8 %).\n\nTodas las comparaciones son descriptivas y no causales.\n\n## 3. Resultados\n\n**Hallazgo 1. La inflación se disparó en 2021-2022 y volvió al rango meta en 2024.** La inflación a 12 meses cerró en 1.90 % en diciembre de 2019 y en 1.97 % en diciembre de 2020; subió a 6.43 % (diciembre de 2021) y a 8.46 % (diciembre de 2022); bajó a 3.24 % (diciembre de 2023) y a 1.97 % (diciembre de 2024). El promedio anual fue 7.86 % en 2022 y 2.35 % en 2024. El máximo del periodo fue 8.81 % en junio de 2022 (PN01273PM, 2019-01 a 2024-12; Figura 1).\n\n**Hallazgo 2. La actividad cayó en 2020 y en 2024 superaba su nivel prepandemia.** El índice del PBI pasó de 180.0 en 2019-T4 a un mínimo de 120.1 en 2020-T2, y llegó a 195.0 en 2024-T4, una variación de +8.35 % frente a 2019-T4 (PN02516AQ, 2019-T4 a 2024-T4; Figura 2). El promedio anual fue 170.98 en 2019, 152.28 en 2020 y 183.18 en 2024. El PBI de 2023 (176.96 promedio) quedó por debajo del de 2022 (177.58).\n\n**Hallazgo 3. La pobreza rural supera a la urbana en 14.5 puntos porcentuales.** En 2024 la pobreza monetaria fue 39.30 % en el área rural (IC 95 %: 37.80-40.81) y 24.81 % en la urbana (IC 95 %: 23.62-25.99); los intervalos no se superponen (INEI, ENAHO 2024, `factor07 × mieperho`; Figura 3).\n\n**Hallazgo 4. Entre departamentos hay una brecha amplia, con grupos estadísticamente indistinguibles.** Cajamarca tuvo la mayor pobreza (45.01 %; IC 95 %: 40.84-49.17) e Ica la menor (6.01 %; IC 95 %: 4.17-7.85), una diferencia de 39.0 puntos con intervalos separados. Sin embargo, el IC de Cajamarca se superpone con los de Loreto (42.97 %; 38.81-47.13) y Puno (39.94 %; 35.43-44.45), por lo que no se afirma que Cajamarca supere a esos departamentos. Lima registró 27.07 % (24.71-29.43) y Callao 33.86 % (29.16-38.56) (Figuras 4 y 5). **Advertencia:** el CV supera 15 % en Ica (15.61 %), Moquegua (16.23 %; 10.97 %) y Madre de Dios (19.50 %; 11.15 %); sus estimaciones son poco precisas.\n\n## 4. Visualizaciones\n\n![Figura 1](../figuras/inflacion_2019_2024.png)\n\n![Figura 2](../figuras/pbi_2019_2024.png)\n\n![Figura 3](../figuras/pobreza_area.png)\n\n![Figura 4](../figuras/pobreza_departamento.png)\n\n![Figura 5](../mapas/pobreza_departamento.png)\n\n## 5. Interpretación\n\nEl periodo combina un choque de actividad en 2020, una aceleración de precios en 2021-2022 y una normalización posterior. En 2024 la inflación (1.97 %) y la actividad convivían con una pobreza territorialmente muy desigual: la rural y los departamentos del norte y sur andino y de
... [2026 caracteres omitidos]
```

## 46. Resultado

**Resultado de la herramienta:**

```
File created successfully at: C:/Users/[usuario]\Documents\tarea_4\informes\informe_final.md (file state is current in your context — no need to Read it back)
```

## 47. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv 2>&1 | tail -20",
 "timeout": 300000
}
```

## 48. Resultado

**Resultado de la herramienta:**

```
# Verificación independiente de cifras del informe

Generado con `.claude/skills/informando-investigacion/scripts/verificar.py` a partir de `afirmaciones.csv`. Las cifras del BCRP se consultaron directamente en la API pública (sin el servidor MCP) y las de la ENAHO se recalcularon desde el archivo .dta original de la sumaria con pandas, sin la skill de limpieza.

**Tabla 1**

*Comparación entre las cifras del informe y su verificación independiente*

| Id | Afirmación | Informe | Verificado | Diferencia | Tolerancia | Coincide | Procedimiento |
|:---|:---|---:|---:|---:|---:|:---:|:---|
| f1 | Inflación de diciembre de 2022 (8.46 %) | 8.46 | 8.4592 | 0.0008 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-12/2022-12 |
| f2 | Inflación de diciembre de 2024 (1.97 %) | 1.97 | 1.9663 | 0.0037 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2024-12/2024-12 |
| f3 | Inflación promedio de 2022 (7.86 %) | 7.86 | 7.8646 | -0.0046 | 0.01 | Sí | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2022-1/2022-12 |
| f4 | Pobreza rural 2024 (39.30 %) | 39.3 | 39.302799224853516 | -0.00279999990016222 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f5 | Pobreza urbana 2024 (24.81 %) | 24.81 | 24.80699920654297 | 0.003000000026077032 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |
| f6 | Pobreza en Cajamarca 2024 (45.01 %) | 45.01 | 45.006900787353516 | 0.003100000089034438 | 0.05 | Sí | datos/966-Modulo34.zip: sumaria-2024.dta |

*Nota.* 6 de 6 afirmaciones coinciden dentro de la tolerancia definida antes de verificar. Diferencia = valor del informe menos valor verificado.
```

## 49. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/informando-investigacion/scripts/publicar.py 2>&1 | tail -8; ls informes",
 "timeout": 300000
}
```

## 50. Resultado

**Resultado de la herramienta:**

```
Informe HTML: informes\informe_final.html
Tablero: informes\dashboard.html
afirmaciones.csv
dashboard.html
informe_final.html
informe_final.md
plan.md
verificacion.csv
verificacion.md
```

## 51. Asistente (Claude)

Terminé el informe final y su versión HTML. Las 6 cifras que verifiqué (3 del BCRP y 3 de la ENAHO) coinciden con su fuente dentro de la tolerancia que fijé antes de verificar.

**Qué encontré**
1. **Inflación (BCRP, PN01273PM):** cerró en 1.90 % en diciembre de 2019 y subió a 8.46 % en diciembre de 2022 (máximo de 8.81 % en junio de 2022). Luego bajó a 3.24 % en 2023 y a 1.97 % en diciembre de 2024.
2. **Actividad (BCRP, PN02516AQ):** el índice del PBI tocó un mínimo de 120.1 en 2020-T2. En 2024-T4 llegó a 195.0, un 8.35 % por encima de 2019-T4.
3. **Brecha urbano–rural (INEI, ENAHO 2024):** la pobreza fue 39.30 % en el área rural y 24.81 % en la urbana, 14.5 puntos de diferencia. Los intervalos de confianza al 95 % no se superponen.
4. **Brecha entre departamentos:** va de 45.01 % en Cajamarca a 6.01 % en Ica. Cajamarca, Loreto y Puno tienen intervalos que se superponen, así que el informe no afirma que Cajamarca supere a los otros dos. Ica, Moquegua y Madre de Dios tienen un coeficiente de variación mayor a 15 %, y el informe lo advierte.

Las asociaciones entre estas series son descriptivas, no causales; el informe lo dice. La validación de la limpieza de la ENAHO aprobó 18 de 18 verificaciones, con pobreza nacional de 27.58 %.

**Una limitación:** las cifras del PBI no pasaron por la verificación independiente, solo las de inflación y pobreza. Las tomé de las herramientas del servidor MCP del BCRP.

**Archivos**
- `informes/plan.md`
- `informes/informe_final.md` y `informes/informe_final.html`
- `informes/dashboard.html`
- `informes/afirmaciones.csv`, `informes/verificacion.md` y `informes/verificacion.csv`
- Figuras 1 y 2 (inflación y PBI), 3 (pobreza por área) y 4 (pobreza por departamento) en `figuras/`.
- Figura 5, el mapa departamental, en `mapas/pobreza_departamento.png`.
- Las tablas de datos están en `tablas/`.

**Herramientas usadas**
- **Servidor MCP del BCRP:** `buscar_series`, `resumen_anual`, `resumen` y `graficar_serie`.
- **Skills:** `informando-investigacion` (con sus scripts de verificación y publicación), `limpiando-enaho`, `graficando-enaho` y `mapeando-enaho`.

## Resultado final

- Turnos: 27
- Duración: 103 s
- Error: False

Terminé el informe final y su versión HTML. Las 6 cifras que verifiqué (3 del BCRP y 3 de la ENAHO) coinciden con su fuente dentro de la tolerancia que fijé antes de verificar.

**Qué encontré**
1. **Inflación (BCRP, PN01273PM):** cerró en 1.90 % en diciembre de 2019 y subió a 8.46 % en diciembre de 2022 (máximo de 8.81 % en junio de 2022). Luego bajó a 3.24 % en 2023 y a 1.97 % en diciembre de 2024.
2. **Actividad (BCRP, PN02516AQ):** el índice del PBI tocó un mínimo de 120.1 en 2020-T2. En 2024-T4 llegó a 195.0, un 8.35 % por encima de 2019-T4.
3. **Brecha urbano–rural (INEI, ENAHO 2024):** la pobreza fue 39.30 % en el área rural y 24.81 % en la urbana, 14.5 puntos de diferencia. Los intervalos de confianza al 95 % no se superponen.
4. **Brecha entre departamentos:** va de 45.01 % en Cajamarca a 6.01 % en Ica. Cajamarca, Loreto y Puno tienen intervalos que se superponen, así que el informe no afirma que Cajamarca supere a los otros dos. Ica, Moquegua y Madre de Dios tienen un coeficiente de variación mayor a 15 %, y el informe lo advierte.

Las asociaciones entre estas series son descriptivas, no causales; el informe lo dice. La validación de la limpieza de la ENAHO aprobó 18 de 18 verificaciones, con pobreza nacional de 27.58 %.

**Una limitación:** las cifras del PBI no pasaron por la verificación independiente, solo las de inflación y pobreza. Las tomé de las herramientas del servidor MCP del BCRP.

**Archivos**
- `informes/plan.md`
- `informes/informe_final.md` y `informes/informe_final.html`
- `informes/dashboard.html`
- `informes/afirmaciones.csv`, `informes/verificacion.md` y `informes/verificacion.csv`
- Figuras 1 y 2 (inflación y PBI), 3 (pobreza por área) y 4 (pobreza por departamento) en `figuras/`.
- Figura 5, el mapa departamental, en `mapas/pobreza_departamento.png`.
- Las tablas de datos están en `tablas/`.

**Herramientas usadas**
- **Servidor MCP del BCRP:** `buscar_series`, `resumen_anual`, `resumen` y `graficar_serie`.
- **Skills:** `informando-investigacion` (con sus scripts de verificación y publicación), `limpiando-enaho`, `graficando-enaho` y `mapeando-enaho`.
