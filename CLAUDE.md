# Agente de investigación socioeconómica del Perú

Este repositorio es un agente de investigación: Claude Code coordina un servidor MCP con las series oficiales
del BCRP (`mcp/server.py`, configurado en `.mcp.json`) y cuatro skills de `.claude/skills/` que procesan la
ENAHO 2024 del INEI y redactan informes.

## Reglas de trabajo

- Ninguna cifra se escribe de memoria. Las del BCRP salen de las herramientas `mcp__bcrp__*`; las de la ENAHO
  salen de `salidas/indicadores.csv`, generado por la skill `limpiando-enaho`.
- Cita siempre la fuente: código de serie y periodo (BCRP) o "INEI, ENAHO 2024" y ponderador (ENAHO).
- Estimaciones de ENAHO siempre ponderadas; informar IC 95 % y advertir si CV > 15 %.
- Las asociaciones entre variables macroeconómicas y pobreza son descriptivas, no causales.
- Si una herramienta falla o no hay datos, dilo; no inventes resultados.
- Formato APA 7 en todo producto: Times New Roman, figuras y tablas numeradas (número en negrita, título en
  cursiva, nota con la fuente) y referencias con sangría francesa. Usa `comun/apa.py`.

## Comandos

```bash
uv sync                                                        # entorno
uv run pytest mcp -q                                           # 10 pruebas del servidor MCP
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py       # base limpia y validación
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo todos
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
uv run .claude/skills/informando-investigacion/scripts/publicar.py
```
