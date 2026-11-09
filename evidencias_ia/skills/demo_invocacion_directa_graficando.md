# Invocación directa: /graficando-enaho sexo 6

Fuente: `demo_invocacion_directa_graficando.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

> Nota. En la invocación directa con `/graficando-enaho sexo 6`, Claude Code carga el cuerpo de `SKILL.md` como
> instrucción (con `$ARGUMENTS` = `sexo 6`), por lo que no aparece una llamada a la herramienta `Skill`; la
> evidencia es que el agente ejecuta exactamente el script de la skill con esos argumentos. La activación por
> lenguaje natural (llamada a la herramienta `Skill`) está en `demo_mapa_lenguaje_natural.md`.

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: []
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Task, Bash, CronCreate, CronDelete, CronList, DesignSync, Edit, EnterWorktree, ExitWorktree, Glob, Grep, ListAgents, Monitor, NotebookEdit, PowerShell, PushNotification, Read, RemoteTrigger, ReportFindings, ScheduleWakeup, SendMessage, Skill, TaskStop, ToolSearch, WebFetch, WebSearch, Workflow, Write

## 1. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "ls salidas/personas_2024.parquet salidas/indicadores.csv && uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo sexo --numero 6"
}
```

## 2. Resultado

**Resultado de la herramienta:**

```
salidas/indicadores.csv
salidas/personas_2024.parquet
Figura 6: figuras\pobreza_sexo.png  |  tabla: tablas/pobreza_sexo.csv

categoria  valor_pct  ee_pct  ic95_inf  ic95_sup  cv_pct  n_muestral  poblacion_expandida

   Hombre      27.37    0.54     26.32     28.42    1.96       52587             16453003

    Mujer      27.68    0.52     26.66     28.69    1.87       56077             17694764
```

## 3. Asistente (Claude)

Generé la Figura 6 y la guardé en `figuras/pobreza_sexo.png`. La tabla de cifras está en `tablas/pobreza_sexo.csv`.

**Pobreza monetaria por sexo** (INEI, ENAHO 2024, ponderador `facpob07`):

| Sexo | Pobreza (%) | IC 95 % | CV (%) | n muestral |
|---|---|---|---|---|
| Hombre | 27,37 | 26,32 – 28,42 | 1,96 | 52 587 |
| Mujer | 27,68 | 26,66 – 28,69 | 1,87 | 56 077 |

- **Diferencia:** los intervalos de confianza se superponen casi por completo. La diferencia puntual es de solo 0,31 puntos porcentuales, así que no puedo afirmar que la pobreza sea distinta entre hombres y mujeres.
- **Precisión:** ambos CV están muy por debajo del 15 %, por lo que las estimaciones son precisas.
- **Alcance:** las cifras son descriptivas y no indican causas.

## Resultado final

- Turnos: 2
- Duración: 11 s
- Error: False

Generé la Figura 6 y la guardé en `figuras/pobreza_sexo.png`. La tabla de cifras está en `tablas/pobreza_sexo.csv`.

**Pobreza monetaria por sexo** (INEI, ENAHO 2024, ponderador `facpob07`):

| Sexo | Pobreza (%) | IC 95 % | CV (%) | n muestral |
|---|---|---|---|---|
| Hombre | 27,37 | 26,32 – 28,42 | 1,96 | 52 587 |
| Mujer | 27,68 | 26,66 – 28,69 | 1,87 | 56 077 |

- **Diferencia:** los intervalos de confianza se superponen casi por completo. La diferencia puntual es de solo 0,31 puntos porcentuales, así que no puedo afirmar que la pobreza sea distinta entre hombres y mujeres.
- **Precisión:** ambos CV están muy por debajo del 15 %, por lo que las estimaciones son precisas.
- **Alcance:** las cifras son descriptivas y no indican causas.
