# Agente de investigación socioeconómica del Perú: MCP del BCRP y Skills de ENAHO 2024

Tarea 4 del curso Python Intermedio. Proyecto individual.

## 1. Objetivo

Construir un agente de investigación, coordinado por Claude Code, que responda preguntas sobre la realidad
socioeconómica peruana con datos oficiales y produzca resultados verificables y reproducibles. El agente
combina:

- **Banco Central de Reserva del Perú (BCRP):** series macroeconómicas (inflación, actividad, tipo de cambio,
  tasa de referencia) consultadas mediante un servidor MCP propio construido con FastMCP.
- **Instituto Nacional de Estadística e Informática (INEI), ENAHO 2024:** microdatos de los módulos 34
  (sumaria) y 02 (miembros), procesados por Skills de Claude Code con factores de expansión y error de muestreo.

Ninguna cifra se escribe de memoria: cada número sale de una herramienta MCP, de un script de una Skill o de un
archivo generado por ellas, y las cifras del informe se verifican con un procedimiento independiente. Todos los
productos (figuras, mapas, tablas e informes) siguen el formato APA 7 con tipografía Times New Roman.

## 2. Arquitectura

```text
                         Pregunta en lenguaje natural
                                      |
                                      v
     +---------------------------- Claude Code ----------------------------+
     |  CLAUDE.md (reglas: sin cifras de memoria, ponderar, citar, APA 7)  |
     |                                                                      |
     |  Skill orquestadora: informando-investigacion                        |
     |    plan -> datos BCRP -> datos ENAHO -> informe -> verificación      |
     +-----------+------------------------------------------+--------------+
                 |                                          |
                 v                                          v
     Servidor MCP "bcrp" (mcp/server.py)        Skills de ENAHO (.claude/skills/)
     buscar_series, serie, resumen,             limpiando-enaho  -> salidas/*.parquet,
     resumen_anual, comparar_series,                                indicadores.csv, validacion.txt
     graficar_serie                             graficando-enaho -> figuras/, tablas/
     recursos bcrp://serie/{codigo},            mapeando-enaho   -> mapas/, validacion_mapa.txt
     bcrp://series-clave
     prompts informe, interpretar_indicador
                 |                                          |
                 v                                          v
     API pública del BCRP                       Microdatos INEI (datos/, no versionados)
                 \                                          /
                  +----------> comun/apa.py  <-------------+
                               comun/estimacion.py
                  (estilo APA 7 y estimadores ponderados compartidos)
                                      |
                                      v
     informes/informe_final.md, informe_final.html, dashboard.html,
     verificacion.md (control independiente de cifras)
```

Los componentes comparten dos módulos para que los resultados sean coherentes entre sí:

- `comun/apa.py`: tipografía Times New Roman, paleta de un solo tono, numeración de figuras ("Figura n" en
  negrita, título en cursiva, nota con la fuente), tablas con reglas horizontales y referencias APA 7.
- `comun/estimacion.py`: proporciones ponderadas con error estándar por linealización de Taylor (unidades
  primarias `conglome`, estratos departamento × estrato), intervalo de confianza al 95 % y coeficiente de
  variación.

## 3. Servidor MCP del BCRP (`mcp/server.py`)

| Tipo | Nombre | Función |
|---|---|---|
| Herramienta | `buscar_series` | Busca en el catálogo oficial (17 mil series) por palabras clave, con sinónimos (PBI, var%, crecimiento) y filtro de frecuencia |
| Herramienta | `serie` | Descarga los datos de una serie entre dos periodos (diaria, mensual, trimestral o anual) con la URL de la fuente |
| Herramienta | `resumen` | Primero, último, cambio, variación %, promedio, desviación estándar, máximo y mínimo con su periodo |
| Herramienta propia | `resumen_anual` | Agrega una serie por año calendario: promedio, fin de periodo, extremos y si el año está completo |
| Herramienta propia | `comparar_series` | Alinea dos series en periodos comunes; correlación en niveles y en primeras diferencias, diferencias promedio y extremas; rechaza frecuencias incompatibles |
| Herramienta propia | `graficar_serie` | Figura APA 7 de hasta cuatro series en `figuras/` y sus datos en `tablas/` |
| Recurso | `bcrp://serie/{codigo}` | Ficha descriptiva: nombre, categoría, frecuencia, inicio, actualización, URL de API y web, cita APA |
| Recurso | `bcrp://series-clave` | Series de uso frecuente con su código oficial |
| Prompt | `informe(tema)` | Plantilla para un informe breve y verificable con datos del BCRP |
| Prompt | `interpretar_indicador(codigo, desde, hasta)` | Plantilla para interpretar una serie con sus cifras calculadas |

Detalles de implementación: conversión de periodos (`Ene.2025`, `01.Oct.26`, `T1.25`, `Set`), omisión de
valores `n.d.`, reintentos ante respuestas HTML de la API, caché en disco de 12 horas y errores explícitos
(`ToolError`) cuando un código no existe, no hay datos en el periodo o las frecuencias son incompatibles.

**Pruebas:** `mcp/test_server.py` contiene las 8 pruebas originales de la sesión 04 sin modificaciones y 2
pruebas propias (`resumen_anual` con valores obtenidos directamente de la API y `comparar_series`, incluido su
rechazo de frecuencias incompatibles). Resultado: `10 passed`. `tests/test_skills.py` agrega 3 pruebas de las
Skills (validación, indicadores ponderados y unión del mapa).

## 4. Skills de Claude Code (`.claude/skills/`)

| Skill | Entrada | Salida | Reglas principales |
|---|---|---|---|
| `limpiando-enaho` | `datos/966-Modulo34.zip`, `datos/966-Modulo02.zip` | `salidas/personas_2024.parquet`, `salidas/hogares_2024.parquet`, `salidas/indicadores.csv`, `salidas/validacion.txt` | Llaves como texto; residentes habituales; `merge(validate="m:1")`; 18 validaciones; se detiene si falla una esencial |
| `graficando-enaho` | `salidas/indicadores.csv` | `figuras/pobreza_*.png`, `tablas/pobreza_*.csv` | Estimaciones ponderadas, IC 95 %, barras desde cero, promedio nacional, nota con fuente |
| `mapeando-enaho` | `salidas/indicadores.csv`, GeoJSON | `mapas/pobreza_departamento.png`, `salidas/validacion_mapa.txt` | Unión `ubigeo[:2]` = `FIRST_IDDP`; 25 unidades; Lima y Callao separados; comparación con la referencia de la sesión 16 |
| `informando-investigacion` | Pregunta de investigación | `informes/plan.md`, `informe_final.md`, `afirmaciones.csv`, `verificacion.md`, `informe_final.html`, `dashboard.html` | Orquesta MCP y Skills; verificación independiente de cifras; publicación HTML APA 7 |

Las Skills de gráficos y mapas comprueban si existe la base procesada; si no existe, indican (y Claude ejecuta)
primero `limpiando-enaho`. La Skill orquestadora invoca las demás con la herramienta `Skill`.

### Decisiones metodológicas

- **Ponderador.** Los indicadores territoriales (nacional, área, región, dominio, departamento) y por jefatura
  del hogar se estiman con la sumaria y `factor07 × mieperho`, el procedimiento oficial del INEI, que reproduce
  exactamente las cifras publicadas (27.58 % nacional; 25 de 25 departamentos). Las características
  individuales (sexo, edad) se estiman con los residentes habituales del módulo 02 y `facpob07` (27.53 %
  nacional; diferencia de 0.05 puntos por la calibración del factor poblacional, documentada en
  `salidas/validacion.txt`).
- **Precisión.** Cada indicador incluye error estándar, IC 95 % y CV; las estimaciones con CV > 15 % se marcan
  como poco precisas (por ejemplo, Madre de Dios).
- **Causalidad.** Las relaciones entre variables macroeconómicas y pobreza se presentan como asociaciones
  descriptivas, con fuentes de distinto nivel de agregación y periodo.

## 5. Fuentes y descarga de datos

| Fuente | Datos | Enlace |
|---|---|---|
| INEI | ENAHO 2024, módulo 34 (sumaria) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip |
| INEI | ENAHO 2024, módulo 02 (miembros) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip |
| Repositorio del curso | Límites departamentales | https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson |
| BCRP | Series estadísticas (API pública) | https://estadisticas.bcrp.gob.pe/estadisticas/series/ |
| Curso, sesión 16 | Pobreza departamental de referencia | `referencias/pobreza_departamento_2024.csv` |

Los microdatos no se versionan (`datos/` está en `.gitignore`). Se descargan con:

```bash
uv run .claude/skills/limpiando-enaho/scripts/descargar.py
```

## 6. Instalación con uv

Requisitos: Python 3.11 a 3.13, `uv`, Claude Code con sesión iniciada y conexión a internet.

```bash
git clone https://github.com/av-gomez/tarea_4.git
cd tarea_4
uv sync
uv run .claude/skills/limpiando-enaho/scripts/descargar.py
```

## 7. Conexión del MCP a Claude Code

El servidor ya está declarado en `.mcp.json` (alcance de proyecto):

```json
{ "mcpServers": { "bcrp": { "type": "stdio", "command": "uv", "args": ["run", "mcp/server.py"] } } }
```

Al abrir `claude` en la carpeta del proyecto, aceptar el servidor `bcrp`. Comprobaciones dentro de Claude Code:

1. `/mcp`: el servidor `bcrp` conectado con 6 herramientas.
2. Recurso: `@bcrp:bcrp://serie/PN01273PM ¿desde cuándo hay datos de esta serie?`
3. Prompt: `/mcp__bcrp__informe inflación`
4. Skills: `/skills` lista las cuatro del proyecto.

Equivalente por línea de comandos: `claude mcp add --scope project bcrp -- uv run mcp/server.py`.

## 8. Reproducir el procesamiento y las pruebas

```bash
uv run pytest -q                                                          # 13 pruebas (10 MCP + 3 Skills)
uv run pytest mcp -q                                                      # 10 pruebas del servidor MCP
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --forzar          # base limpia y validación
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area --numero 3
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento --numero 4
uv run .claude/skills/mapeando-enaho/scripts/mapear.py --numero 5
uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv
uv run .claude/skills/informando-investigacion/scripts/publicar.py         # HTML y tablero
uv run evaluacion/verdades.py                                             # respuestas esperadas
uv run evaluacion/evaluar.py                                              # experimento (20 llamadas a claude -p)
uv run evaluacion/resumir.py                                              # tablas y figura de la evaluación
```

### Validación de la ENAHO 2024 (`salidas/validacion.txt`)

| Indicador | Referencia | Resultado |
|---|---:|---:|
| Pobreza monetaria nacional | 27.6 % | 27.58 % (IC 95 %: 26.59-28.57) |
| Residentes habituales | 108,664 | 108,664 |
| Unidades territoriales del mapa | 25 | 25 de 25 (todas iguales a la referencia) |
| Pobreza urbana | 24.8 % | 24.81 % |
| Pobreza rural | 39.3 % | 39.30 % |
| Pobreza extrema | 5.5 % | 5.50 % |

## 9. Resultados de la evaluación

Diez preguntas con respuesta verificada de forma independiente (4 BCRP, 4 ENAHO, 2 combinadas), el mismo
modelo (`sonnet`) y la misma instrucción, en sesiones independientes. Detalle en `evaluacion/comparacion.md`.

| Modo | Correctas | Incorrectas | Sin respuesta | Segundos (media) |
|---|---:|---:|---:|---:|
| A: sin MCP ni Skills | 3 | 3 | 4 | 6.6 |
| B: con MCP y Skills | 10 | 0 | 0 | 22.9 |

Sin herramientas, el modelo acertó solo cifras muy difundidas, dio valores desactualizados o aproximados en tres
casos y se abstuvo en cuatro. Con el MCP y las Skills respondió las diez con su fuente, a costa de un tiempo de
respuesta 3.5 veces mayor.

## 10. Limitaciones y problemas encontrados

- El IPC del BCRP corresponde a Lima Metropolitana; no representa los precios de cada departamento.
- La ENAHO se usa como corte transversal de 2024; el análisis no estima la evolución de la pobreza.
- Las fuentes tienen distinto nivel de agregación (series nacionales frente a estimaciones por área y
  departamento); su yuxtaposición es descriptiva.
- La referencia departamental de la sesión 16 coincide con el estimador de la sumaria (`factor07 × mieperho`)
  y no con el de personas (`facpob07`), que difiere hasta 0.5 puntos en Puno y Huánuco. Se adoptó el estimador
  oficial y se documentó la sensibilidad.
- La API del BCRP responde con HTML cuando recibe muchos pedidos seguidos; el servidor reintenta y guarda caché.
- En la primera ejecución integrada, `buscar_series` no encontró la serie de variación del PBI con la consulta
  "PBI var% anual" y el agente usó el PBI en niveles; se añadieron sinónimos y la frecuencia al texto de búsqueda.
  En esa misma ejecución la numeración APA dentro de los PNG no coincidía con la del informe; se añadió una regla
  de numeración a la Skill orquestadora y se repitió la ejecución (`evidencias_ia/integracion/`).
- En la evaluación, el modo B respondió las preguntas de ENAHO leyendo `salidas/indicadores.csv` (producto de la
  Skill) en lugar de invocar la Skill en cada pregunta.
- La evaluación usa 10 preguntas y una corrida por modo; no permite inferencias estadísticas generales.

## 11. Ejemplo de una ejecución completa

Pregunta de investigación (`evidencias_ia/integracion/pregunta.txt`):

> ¿Cómo evolucionaron la inflación y la actividad económica del Perú entre 2019 y 2024, y qué brechas
> territoriales (entre departamentos y entre áreas urbana y rural) presentaba la pobreza monetaria al cierre de
> ese periodo, en 2024?

Comando (una sola ejecución no interactiva, partiendo sin base procesada):

```bash
claude -p "$(cat evidencias_ia/integracion/pregunta.txt)" --model sonnet --mcp-config .mcp.json \
  --strict-mcp-config --permission-mode acceptEdits --output-format stream-json --verbose \
  --allowedTools "mcp__bcrp__*,Skill,Bash(uv run:*),Read,Write,Edit,Glob,Grep" \
  > evidencias_ia/integracion/ejecucion_integrada.jsonl
```

En esa ejecución (27 turnos, unos dos minutos) Claude Code cargó la Skill `informando-investigacion`; consultó
el BCRP con cuatro herramientas MCP distintas (`buscar_series`, `resumen_anual`, `resumen` y `graficar_serie`);
invocó con la herramienta `Skill` las Skills `limpiando-enaho`, `graficando-enaho` y `mapeando-enaho` (la base
procesada no existía, por lo que la limpieza se ejecutó primero); redactó el informe con cuatro hallazgos, dos
figuras del BCRP, dos figuras de ENAHO y el mapa; verificó seis cifras de forma independiente (6 de 6
coincidencias) y publicó las versiones HTML. El registro completo, legible, está en
`evidencias_ia/integracion/ejecucion_integrada.md`.

Productos:

- Informe: [`informes/informe_final.md`](informes/informe_final.md) y `informes/informe_final.html`
- Tablero interactivo: `informes/dashboard.html` (abrir en el navegador)
- Verificación automática de cifras: [`informes/verificacion.md`](informes/verificacion.md)
- Verificación manual de cinco afirmaciones y manejo de errores: [`informes/verificacion_manual.md`](informes/verificacion_manual.md)
- Plan: [`informes/plan.md`](informes/plan.md)

## 12. Evidencias del uso de inteligencia artificial

Todas las conversaciones están en `evidencias_ia/`, en formato JSONL original y convertidas a Markdown con
`evidencias_ia/convertir.py` (rutas personales, correos y tokens ocultos):

| Carpeta | Contenido |
|---|---|
| `evidencias_ia/desarrollo/` | Sesión completa de Claude Code con la que se desarrolló todo el proyecto: plan, servidor MCP, Skills, pruebas, correcciones, evaluación e informe |
| `evidencias_ia/mcp/` | Pruebas del servidor y extracto de la sesión dedicado al MCP |
| `evidencias_ia/skills/` | Activación por lenguaje natural ("Haz un mapa...", que encadena `mapeando-enaho` y `limpiando-enaho`) e invocación directa `/graficando-enaho` |
| `evidencias_ia/integracion/` | Ejecución integrada definitiva y la primera ejecución (con los problemas que motivaron correcciones) |
| `evidencias_ia/evaluacion/` | Las 20 llamadas del experimento (10 por modo) y sus registros |

## Estructura del repositorio

```text
tarea_4/
├── README.md, CLAUDE.md, pyproject.toml, uv.lock, .mcp.json, .gitignore
├── mcp/                 server.py, test_server.py
├── comun/               apa.py (estilo APA 7), estimacion.py (estimadores con error de muestreo)
├── .claude/skills/      limpiando-enaho, graficando-enaho, mapeando-enaho, informando-investigacion
├── datos/               microdatos (ignorados por Git)
├── referencias/         pobreza_departamento_2024.csv (sesión 16)
├── salidas/             validacion.txt, validacion_mapa.txt, indicadores.csv
├── figuras/  mapas/  tablas/
├── evaluacion/          preguntas.csv, resultados.csv, comparacion.md, verdades.py, evaluar.py, resumir.py
├── informes/            plan.md, informe_final.md/.html, dashboard.html, afirmaciones.csv, verificacion.md
├── tests/               test_skills.py
└── evidencias_ia/       desarrollo, mcp, skills, integracion, evaluacion
```

## Referencias

Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos].
https://estadisticas.bcrp.gob.pe/estadisticas/series/

D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub.
https://github.com/d2cml-ai/Data-Science-Python

Instituto Nacional de Estadística e Informática. (2025). *Encuesta Nacional de Hogares sobre Condiciones de
Vida y Pobreza 2024* [Base de datos: módulos 02 y 34]. https://proyectos.inei.gob.pe/microdatos/

Wolter, K. M. (2007). *Introduction to variance estimation* (2nd ed.). Springer.
