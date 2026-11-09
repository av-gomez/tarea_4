# Robustez del MCP: periodo sin datos y serie inexistente

Fuente: `robustez_datos_inexistentes.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: [{"name": "bcrp", "status": "connected", "source": "dynamic"}]
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: mcp__bcrp__buscar_series, mcp__bcrp__comparar_series, mcp__bcrp__graficar_serie, mcp__bcrp__resumen, mcp__bcrp__resumen_anual, mcp__bcrp__serie

## 1. Asistente (Claude)

**Herramienta:** `mcp__bcrp__serie`

```json
{
 "codigo": "PN01273PM",
 "desde": "2030-12",
 "hasta": "2030-12"
}
```

## 2. Asistente (Claude)

**Herramienta:** `mcp__bcrp__serie`

```json
{
 "codigo": "XX99999PM",
 "desde": "2024-01",
 "hasta": "2024-01"
}
```

## 3. Resultado

**Resultado de la herramienta:**

```
No existe el código de serie 'XX99999PM'. Búsquenlo con buscar_series.
```

## 4. Resultado

**Resultado de la herramienta:**

```
La serie PN01273PM no tiene datos entre 2030-12 y 2030-12. Revisen el periodo (la serie empieza en Ene-1950 y se actualizó el 2026-10-08).
```

## 5. Asistente (Claude)

No pude darte ninguna de las dos cifras, porque el servidor del BCRP no tiene datos para ninguna de las consultas.

1. **Inflación interanual de Lima Metropolitana, diciembre de 2030.** Consulté la serie `PN01273PM` (inflación a 12 meses de Lima) y no tiene datos para 2030-12. La serie se actualizó por última vez el 2026-10-08, y hoy es 2026-11-08. Diciembre de 2030 todavía no ocurre, así que no existe un dato oficial. No voy a dar una proyección como si fuera un dato.

2. **Serie `XX99999PM`, enero de 2024.** Ese código no existe en el BCRP. No puedo darte un valor para una serie que no existe. Si me dices qué indicador buscas, la busco por nombre con `buscar_series` y consulto el código correcto.

Si quieres, puedo darte la inflación a 12 meses de Lima del último mes disponible o de diciembre de 2025.

## Resultado final

- Turnos: 3
- Duración: 7 s
- Error: False

No pude darte ninguna de las dos cifras, porque el servidor del BCRP no tiene datos para ninguna de las consultas.

1. **Inflación interanual de Lima Metropolitana, diciembre de 2030.** Consulté la serie `PN01273PM` (inflación a 12 meses de Lima) y no tiene datos para 2030-12. La serie se actualizó por última vez el 2026-10-08, y hoy es 2026-11-08. Diciembre de 2030 todavía no ocurre, así que no existe un dato oficial. No voy a dar una proyección como si fuera un dato.

2. **Serie `XX99999PM`, enero de 2024.** Ese código no existe en el BCRP. No puedo darte un valor para una serie que no existe. Si me dices qué indicador buscas, la busco por nombre con `buscar_series` y consulto el código correcto.

Si quieres, puedo darte la inflación a 12 meses de Lima del último mes disponible o de diciembre de 2025.
