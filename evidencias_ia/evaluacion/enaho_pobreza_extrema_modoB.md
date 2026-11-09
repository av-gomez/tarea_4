# Evaluación: enaho_pobreza_extrema_modoB

Fuente: `enaho_pobreza_extrema_modoB.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: [{"name": "bcrp", "status": "connected", "source": "dynamic"}]
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Bash, Glob, Grep, Read, Skill, StructuredOutput, mcp__bcrp__buscar_series, mcp__bcrp__comparar_series, mcp__bcrp__graficar_serie, mcp__bcrp__resumen, mcp__bcrp__resumen_anual, mcp__bcrp__serie

## 1. Asistente (Claude)

**Herramienta:** `Grep`

```json
{
 "pattern": "extrem",
 "path": "C:/Users/[usuario]\\Documents\\tarea_4\\salidas\\indicadores.csv",
 "output_mode": "content",
 "-i": true,
 "head_limit": 20
}
```

## 2. Resultado

**Resultado de la herramienta:**

```
51:pobreza_extrema,nacional,,Perú,5.505,0.233,5.049,5.96,4.226,33691,34482700,factor07*mieperho,True
52:pobreza_extrema,area,,Rural,15.518,0.602,14.339,16.698,3.878,11660,6595188,factor07*mieperho,True
53:pobreza_extrema,area,,Urbana,3.136,0.249,2.649,3.624,7.932,22031,27887512,factor07*mieperho,True
54:pobreza_extrema,region_natural,,Costa,2.591,0.305,1.993,3.19,11.776,14411,19548500,factor07*mieperho,True
55:pobreza_extrema,region_natural,,Selva,7.943,0.625,6.717,9.168,7.873,7211,4360930,factor07*mieperho,True
56:pobreza_extrema,region_natural,,Sierra,9.885,0.431,9.041,10.729,4.356,12069,10573269,factor07*mieperho,True
57:pobreza_extrema,dominio_nombre,,Costa Centro,1.084,0.269,0.556,1.612,24.851,3287,2307204,factor07*mieperho,False
58:pobreza_extrema,dominio_nombre,,Costa Norte,1.921,0.335,1.264,2.577,17.438,4751,5104587,factor07*mieperho,False
59:pobreza_extrema,dominio_nombre,,Costa Sur,1.139,0.335,0.483,1.795,29.381,2283,705004,factor07*mieperho,False
60:pobreza_extrema,dominio_nombre,,Lima Metropolitana,3.285,0.493,2.318,4.251,15.012,4090,11431706,factor07*mieperho,False
61:pobreza_extrema,dominio_nombre,,Selva,7.943,0.625,6.717,9.168,7.873,7211,4360930,factor07*mieperho,True
62:pobreza_extrema,dominio_nombre,,Sierra Centro,8.773,0.601,7.595,9.952,6.855,5531,4057362,factor07*mieperho,True
63:pobreza_extrema,dominio_nombre,,Sierra Norte,21.757,1.411,18.992,24.521,6.484,2015,1899899,factor07*mieperho,True
64:pobreza_extrema,dominio_nombre,,Sierra Sur,5.975,0.572,4.853,7.098,9.581,4523,4616008,factor07*mieperho,True
65:pobreza_extrema,departamento,01,Amazonas,6.012,1.28,3.502,8.522,21.299,1243,442355,factor07*mieperho,False
66:pobreza_extrema,departamento,02,Áncash,5.8,0.841,4.152,7.448,14.499,1393,1212494,factor07*mieperho,True
67:pobreza_extrema,departamento,03,Apurímac,5.237,1.241,2.805,7.67,23.698,913,494188,factor07*mieperho,False
68:pobreza_extrema,departamento,04,Arequipa,1.646,0.474,0.716,2.576,28.818,1506,1421684,factor07*mieperho,False
69:pobreza_extrema,departamento,05,Ayacucho,9.086,1.357,6.427,11.745,14.933,1160,775447,factor07*mieperho,True
70:pobreza_extrema,departamento,06,Cajamarca,19.715,1.737,16.311,23.12,8.81,1469,1554586,factor07*mieperho,True

[Showing results with pagination = limit: 20]
```

## 3. Asistente (Claude)

**Herramienta:** `StructuredOutput`

```json
{
 "valor": 5.505,
 "unidad": "% de la población",
 "fuente": "INEI, ENAHO 2024, estimación ponderada (factor07*mieperho) en salidas/indicadores.csv, fila pobreza_extrema/nacional/Perú, generada por la skill limpiando-enaho. IC 95 %: 5,049–5,960; CV = 4,2 % (menor a 15 %)."
}
```

## 4. Resultado

**Resultado de la herramienta:**

```
Structured output provided successfully
```

## Resultado final

- Turnos: 3
- Duración: 6 s
- Error: False

{"valor":5.505,"unidad":"% de la población","fuente":"INEI, ENAHO 2024, estimación ponderada (factor07*mieperho) en salidas/indicadores.csv, fila pobreza_extrema/nacional/Perú, generada por la skill limpiando-enaho. IC 95 %: 5,049–5,960; CV = 4,2 % (menor a 15 %)."}
