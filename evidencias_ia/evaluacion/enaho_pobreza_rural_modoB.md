# Evaluación: enaho_pobreza_rural_modoB

Fuente: `enaho_pobreza_rural_modoB.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: [{"name": "bcrp", "status": "connected", "source": "dynamic"}]
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Bash, Glob, Grep, Read, Skill, StructuredOutput, mcp__bcrp__buscar_series, mcp__bcrp__comparar_series, mcp__bcrp__graficar_serie, mcp__bcrp__resumen, mcp__bcrp__resumen_anual, mcp__bcrp__serie

## 1. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls salidas 2>/dev/null; grep -i -E \"rural\" salidas/indicadores.csv | head -20"
}
```

## 2. Resultado

**Resultado de la herramienta:**

```
hogares_2024.parquet
indicadores.csv
personas_2024.parquet
validacion.txt
validacion_mapa.txt
pobreza_monetaria,area,,Rural,39.303,0.769,37.796,40.81,1.957,11660,6595188,factor07*mieperho,True
pobreza_extrema,area,,Rural,15.518,0.602,14.339,16.698,3.878,11660,6595188,factor07*mieperho,True
```

## 3. Asistente (Claude)

**Herramienta:** `StructuredOutput`

```json
{
 "valor": 39.3,
 "unidad": "%",
 "fuente": "INEI, ENAHO 2024 (módulos 34 sumaria y 02). Archivo salidas/indicadores.csv, fila pobreza_monetaria, área Rural, generado por la skill limpiando-enaho. Estimación ponderada con factor07*mieperho: 39,303 %, IC 95 % [37,80; 40,81], CV 1,96 %, n = 11 660 personas."
}
```

## 4. Resultado

**Resultado de la herramienta:**

```
Structured output provided successfully
```

## Resultado final

- Turnos: 3
- Duración: 12 s
- Error: False

{"valor":39.3,"unidad":"%","fuente":"INEI, ENAHO 2024 (módulos 34 sumaria y 02). Archivo salidas/indicadores.csv, fila pobreza_monetaria, área Rural, generado por la skill limpiando-enaho. Estimación ponderada con factor07*mieperho: 39,303 %, IC 95 % [37,80; 40,81], CV 1,96 %, n = 11 660 personas."}
