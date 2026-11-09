# Activación por lenguaje natural: mapeando-enaho encadena limpiando-enaho

Fuente: `demo_mapa_lenguaje_natural.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: []
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Task, Bash, CronCreate, CronDelete, CronList, DesignSync, Edit, EnterWorktree, ExitWorktree, Glob, Grep, ListAgents, Monitor, NotebookEdit, PowerShell, PushNotification, Read, RemoteTrigger, ReportFindings, ScheduleWakeup, SendMessage, Skill, TaskStop, ToolSearch, WebFetch, WebSearch, Workflow, Write

## 1. Asistente (Claude)

**Herramienta:** `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

## 2. Resultado

**Resultado de la herramienta:**

```
Launching skill: mapeando-enaho
```

## 3. Usuario

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


## 4. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls salidas mapas 2>&1 | head -30"
}
```

## 5. Resultado

**Resultado de la herramienta:**

```
mapas:

salidas:
```

## 6. Asistente (Claude)

Faltan los archivos de salida, así que primero ejecuto la limpieza.

## 7. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/limpiando-enaho/scripts/limpiar.py 2>&1 | tail -30",
 "timeout": 600000
}
```

## 8. Resultado

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

## 9. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero 1 2>&1 | tail -15; cat salidas/validacion_mapa.txt; python -c \"\nimport pandas as pd\nd=pd.read_csv('salidas/indicadores.csv');print(d.columns.tolist());print(d.head(3))\"",
 "timeout": 300000
}
```

## 10. Resultado

**Resultado de la herramienta:**

```
This Bash command contains multiple operations. The following part requires approval: tail -15; cat salidas/validacion_mapa.txt; python -c "
import pandas as pd
d=pd.read_csv('salidas/indicadores.csv');print(d.columns.tolist());print(d.head(3))"
```

## 11. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero 1",
 "timeout": 300000
}
```

## 12. Asistente (Claude)

**Herramienta:** `Read`

```json
{
 "file_path": "C:/Users/[usuario]\\Documents\\tarea_4\\salidas\\validacion_mapa.txt"
}
```

## 13. Asistente (Claude)

**Herramienta:** `Grep`

```json
{
 "pattern": "departamento",
 "path": "C:/Users/[usuario]\\Documents\\tarea_4\\salidas\\indicadores.csv",
 "output_mode": "content",
 "head_limit": 40
}
```

## 14. Resultado

**Resultado de la herramienta:**

```
VALIDACION DEL MAPA (pobreza_monetaria)
============================================================
Union: ubigeo[:2] (indicadores.csv) = FIRST_IDDP (GeoJSON); unidades unidas: 25/25
Coinciden con referencias/pobreza_departamento_2024.csv (|dif| <= 0.1 p.p.): 25/25
  01 AMAZONAS        calculado  25.7  referencia  25.7  dif +0.0
  02 ANCASH          calculado  22.8  referencia  22.8  dif +0.0
  03 APURIMAC        calculado  24.0  referencia  24.0  dif +0.0
  04 AREQUIPA        calculado  15.8  referencia  15.8  dif +0.0
  05 AYACUCHO        calculado  32.8  referencia  32.8  dif +0.0
  06 CAJAMARCA       calculado  45.0  referencia  45.0  dif +0.0
  07 CALLAO          calculado  33.9  referencia  33.9  dif +0.0
  08 CUSCO           calculado  18.5  referencia  18.5  dif +0.0
  09 HUANCAVELICA    calculado  33.4  referencia  33.4  dif +0.0
  10 HUANUCO         calculado  39.0  referencia  39.0  dif +0.0
  11 ICA             calculado   6.0  referencia   6.0  dif +0.0
  12 JUNIN           calculado  18.5  referencia  18.5  dif +0.0
  13 LA LIBERTAD     calculado  30.2  referencia  30.2  dif +0.0
  14 LAMBAYEQUE      calculado  14.0  referencia  14.0  dif +0.0
  15 LIMA            calculado  27.1  referencia  27.1  dif +0.0
  16 LORETO          calculado  43.0  referencia  43.0  dif +0.0
  17 MADRE DE DIOS   calculado  11.1  referencia  11.1  dif +0.0
  18 MOQUEGUA        calculado  11.0  referencia  11.0  dif +0.0
  19 PASCO           calculado  39.0  referencia  39.0  dif +0.0
  20 PIURA           calculado  31.9  referencia  31.9  dif +0.0
  21 PUNO            calculado  39.9  referencia  39.9  dif +0.0
  22 SAN MARTIN      calculado  22.0  referencia  22.0  dif +0.0
  23 TACNA           calculado  24.0  referencia  24.0  dif +0.0
  24 TUMBES          calculado  26.9  referencia  26.9  dif +0.0
  25 UCAYALI         calculado  27.1  referencia  27.1  dif +0.0
RESULTADO: APROBADA

Mapa: mapas\pobreza_departamento.png (25 unidades territoriales)
```

## 15. Resultado

**Resultado de la herramienta:**

```
1	VALIDACION DEL MAPA (pobreza_monetaria)
2	============================================================
3	Union: ubigeo[:2] (indicadores.csv) = FIRST_IDDP (GeoJSON); unidades unidas: 25/25
4	Coinciden con referencias/pobreza_departamento_2024.csv (|dif| <= 0.1 p.p.): 25/25
5	  01 AMAZONAS        calculado  25.7  referencia  25.7  dif +0.0
6	  02 ANCASH          calculado  22.8  referencia  22.8  dif +0.0
7	  03 APURIMAC        calculado  24.0  referencia  24.0  dif +0.0
8	  04 AREQUIPA        calculado  15.8  referencia  15.8  dif +0.0
9	  05 AYACUCHO        calculado  32.8  referencia  32.8  dif +0.0
10	  06 CAJAMARCA       calculado  45.0  referencia  45.0  dif +0.0
11	  07 CALLAO          calculado  33.9  referencia  33.9  dif +0.0
12	  08 CUSCO           calculado  18.5  referencia  18.5  dif +0.0
13	  09 HUANCAVELICA    calculado  33.4  referencia  33.4  dif +0.0
14	  10 HUANUCO         calculado  39.0  referencia  39.0  dif +0.0
15	  11 ICA             calculado   6.0  referencia   6.0  dif +0.0
16	  12 JUNIN           calculado  18.5  referencia  18.5  dif +0.0
17	  13 LA LIBERTAD     calculado  30.2  referencia  30.2  dif +0.0
18	  14 LAMBAYEQUE      calculado  14.0  referencia  14.0  dif +0.0
19	  15 LIMA            calculado  27.1  referencia  27.1  dif +0.0
20	  16 LORETO          calculado  43.0  referencia  43.0  dif +0.0
21	  17 MADRE DE DIOS   calculado  11.1  referencia  11.1  dif +0.0
22	  18 MOQUEGUA        calculado  11.0  referencia  11.0  dif +0.0
23	  19 PASCO           calculado  39.0  referencia  39.0  dif +0.0
24	  20 PIURA           calculado  31.9  referencia  31.9  dif +0.0
25	  21 PUNO            calculado  39.9  referencia  39.9  dif +0.0
26	  22 SAN MARTIN      calculado  22.0  referencia  22.0  dif +0.0
27	  23 TACNA           calculado  24.0  referencia  24.0  dif +0.0
28	  24 TUMBES          calculado  26.9  referencia  26.9  dif +0.0
29	  25 UCAYALI         calculado  27.1  referencia  27.1  dif +0.0
30	RESULTADO: APROBADA
31	
```

## 16. Resultado

**Resultado de la herramienta:**

```
16:pobreza_monetaria,departamento,01,Amazonas,25.749,2.464,20.92,30.578,9.569,1243,442355,factor07*mieperho,True
17:pobreza_monetaria,departamento,02,Áncash,22.775,1.843,19.162,26.387,8.093,1393,1212494,factor07*mieperho,True
18:pobreza_monetaria,departamento,03,Apurímac,23.959,2.303,19.446,28.472,9.61,913,494188,factor07*mieperho,True
19:pobreza_monetaria,departamento,04,Arequipa,15.784,1.558,12.73,18.838,9.871,1506,1421684,factor07*mieperho,True
20:pobreza_monetaria,departamento,05,Ayacucho,32.763,2.245,28.363,37.164,6.853,1160,775447,factor07*mieperho,True
21:pobreza_monetaria,departamento,06,Cajamarca,45.007,2.123,40.845,49.168,4.718,1469,1554586,factor07*mieperho,True
22:pobreza_monetaria,departamento,07,Callao,33.86,2.399,29.158,38.562,7.085,1027,1142618,factor07*mieperho,True
23:pobreza_monetaria,departamento,08,Cusco,18.541,1.951,14.718,22.364,10.52,1230,1409467,factor07*mieperho,True
24:pobreza_monetaria,departamento,09,Huancavelica,33.403,2.187,29.118,37.689,6.546,1042,543103,factor07*mieperho,True
25:pobreza_monetaria,departamento,10,Huánuco,38.963,2.541,33.983,43.943,6.521,1244,926653,factor07*mieperho,True
26:pobreza_monetaria,departamento,11,Ica,6.014,0.939,4.174,7.854,15.61,1500,854203,factor07*mieperho,False
27:pobreza_monetaria,departamento,12,Junín,18.499,1.825,14.922,22.077,9.866,1506,1450149,factor07*mieperho,True
28:pobreza_monetaria,departamento,13,La Libertad,30.19,1.827,26.609,33.772,6.053,1509,2080789,factor07*mieperho,True
29:pobreza_monetaria,departamento,14,Lambayeque,14.041,1.873,10.369,17.713,13.343,1302,1349731,factor07*mieperho,True
30:pobreza_monetaria,departamento,15,Lima,27.069,1.205,24.708,29.43,4.451,4544,11279908,factor07*mieperho,True
31:pobreza_monetaria,departamento,16,Loreto,42.973,2.122,38.813,47.132,4.938,1359,1129071,factor07*mieperho,True
32:pobreza_monetaria,departamento,17,Madre de Dios,11.148,2.174,6.887,15.408,19.499,603,165992,factor07*mieperho,False
33:pobreza_monetaria,departamento,18,Moquegua,10.968,1.78,7.479,14.457,16.231,963,198386,factor07*mieperho,False
34:pobreza_monetaria,departamento,19,Pasco,38.972,2.534,34.005,43.939,6.503,865,327776,factor07*mieperho,True
35:pobreza_monetaria,departamento,20,Piura,31.861,1.654,28.618,35.104,5.193,1611,1988570,factor07*mieperho,True
36:pobreza_monetaria,departamento,21,Puno,39.938,2.302,35.427,44.449,5.763,1123,1586886,factor07*mieperho,True
37:pobreza_monetaria,departamento,22,San Martín,22.021,1.991,18.119,25.924,9.043,1347,947446,factor07*mieperho,True
38:pobreza_monetaria,departamento,23,Tacna,23.989,2.863,18.377,29.601,11.936,1271,380755,factor07*mieperho,True
39:pobreza_monetaria,departamento,24,Tumbes,26.901,2.449,22.102,31.7,9.102,842,261959,factor07*mieperho,True
40:pobreza_monetaria,departamento,25,Ucayali,27.07,2.198,22.762,31.378,8.119,1119,558484,factor07*mieperho,True
65:pobreza_extrema,departamento,01,Amazonas,6.012,1.28,3.502,8.522,21.299,1243,442355,factor07*mieperho,False
66:pobreza_extrema,departamento,02,Áncash,5.8,0.841,4.152,7.448,14.499,1393,1212494,factor07*mieperho,True
67:pobreza_extrema,departamento,03,Apurímac,5.237,1.241,2.805,7.67,23.698,913,494188,factor07*mieperho,False
68:pobreza_extrema,departamento,04,Arequipa,1.646,0.474,0.716,2.576,28.818,1506,1421684,factor07*mieperho,False
69:pobreza_extrema,departamento,05,Ayacucho,9.086,1.357,6.427,11.745,14.933,1160,775447,factor07*mieperho,True
70:pobreza_extrema,departamento,06,Cajamarca,19.715,1.737,16.311,23.12,8.81,1469,1554586,factor07*mieperho,True
71:pobreza_extrema,departamento,07,Callao,5.039,1.1,2.884,7.195,21.82,1027,1142618,factor07*mieperho,False
72:pobreza_extrema,departamento,08,Cusco,2.104,0.6,0.928,3.28,28.525,1230,1409467,factor07*mieperho,False
73:pobreza_extrema,departamento,09,Huancavelica,11.16,1.537,8.149,14.172,13.768,1042,543103,factor07*mieperho,True
74:pobreza_extrema,departamento,10,Huánuco,12.199,1.733,8.803,15.595,14.204,1244,926653,factor07*mieperho,True
75:pobreza_extrema,departamento,11,Ica,0.148,0.148,-0.142,0.438,99.992,
... [528 caracteres omitidos]
```

## 17. Asistente (Claude)

Hice el mapa de la pobreza monetaria por departamento con la ENAHO 2024. Lo guardé en `mapas/pobreza_departamento.png`. No lo abrí para revisarlo a ojo. Las validaciones del script sí pasaron.

Al empezar no existían `salidas/personas_2024.parquet` ni `salidas/indicadores.csv`, así que primero ejecuté `limpiando-enaho`. Pasaron las 18 verificaciones. La pobreza monetaria nacional es 27,58 % (IC 95 %: 26,59–28,57; CV 1,8 %).

**Validación del mapa** (`salidas/validacion_mapa.txt`):
- Se unieron 25 de 25 unidades por `ubigeo[:2]` con `FIRST_IDDP`. Lima y Callao quedan separados.
- Los 25 departamentos coinciden con `referencias/pobreza_departamento_2024.csv`, con diferencia de 0,0 p.p.

**Lectura del mapa** (% de personas en pobreza; fuente: INEI, ENAHO 2024, ponderador `factor07*mieperho`):

| | Departamento | % | IC 95 % |
|---|---|---|---|
| Mayor | Cajamarca | 45,0 | 40,8–49,2 |
| | Loreto | 43,0 | 38,8–47,1 |
| | Puno | 39,9 | 35,4–44,4 |
| | Pasco | 39,0 | 34,0–43,9 |
| | Huánuco | 39,0 | 34,0–43,9 |
| Menor | Ica | 6,0 | 4,2–7,9 |
| | Moquegua | 11,0 | 7,5–14,5 |
| | Madre de Dios | 11,1 | 6,9–15,4 |
| | Lambayeque | 14,0 | 10,4–17,7 |
| | Arequipa | 15,8 | 12,7–18,8 |

- **Advertencia de precisión:** las estimaciones de Ica (CV 15,6 %), Moquegua (16,2 %) y Madre de Dios (19,5 %) superan el CV de 15 %. Son menos precisas.
- **Diferencias entre departamentos:** los IC de varios departamentos se superponen. Por ejemplo, Cajamarca y Loreto, o Pasco y Huánuco. Por eso no conviene interpretar el orden entre vecinos cercanos del ranking como diferencia significativa.
- **Alcance:** el mapa describe la distribución territorial. No explica causas.

## Resultado final

- Turnos: 9
- Duración: 34 s
- Error: False

Hice el mapa de la pobreza monetaria por departamento con la ENAHO 2024. Lo guardé en `mapas/pobreza_departamento.png`. No lo abrí para revisarlo a ojo. Las validaciones del script sí pasaron.

Al empezar no existían `salidas/personas_2024.parquet` ni `salidas/indicadores.csv`, así que primero ejecuté `limpiando-enaho`. Pasaron las 18 verificaciones. La pobreza monetaria nacional es 27,58 % (IC 95 %: 26,59–28,57; CV 1,8 %).

**Validación del mapa** (`salidas/validacion_mapa.txt`):
- Se unieron 25 de 25 unidades por `ubigeo[:2]` con `FIRST_IDDP`. Lima y Callao quedan separados.
- Los 25 departamentos coinciden con `referencias/pobreza_departamento_2024.csv`, con diferencia de 0,0 p.p.

**Lectura del mapa** (% de personas en pobreza; fuente: INEI, ENAHO 2024, ponderador `factor07*mieperho`):

| | Departamento | % | IC 95 % |
|---|---|---|---|
| Mayor | Cajamarca | 45,0 | 40,8–49,2 |
| | Loreto | 43,0 | 38,8–47,1 |
| | Puno | 39,9 | 35,4–44,4 |
| | Pasco | 39,0 | 34,0–43,9 |
| | Huánuco | 39,0 | 34,0–43,9 |
| Menor | Ica | 6,0 | 4,2–7,9 |
| | Moquegua | 11,0 | 7,5–14,5 |
| | Madre de Dios | 11,1 | 6,9–15,4 |
| | Lambayeque | 14,0 | 10,4–17,7 |
| | Arequipa | 15,8 | 12,7–18,8 |

- **Advertencia de precisión:** las estimaciones de Ica (CV 15,6 %), Moquegua (16,2 %) y Madre de Dios (19,5 %) superan el CV de 15 %. Son menos precisas.
- **Diferencias entre departamentos:** los IC de varios departamentos se superponen. Por ejemplo, Cajamarca y Loreto, o Pasco y Huánuco. Por eso no conviene interpretar el orden entre vecinos cercanos del ranking como diferencia significativa.
- **Alcance:** el mapa describe la distribución territorial. No explica causas.
