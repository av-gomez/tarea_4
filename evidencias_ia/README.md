# Evidencias del uso de inteligencia artificial

Todo el proyecto se desarrolló con Claude Code (modelo Claude Opus 5.5 en la sesión de desarrollo; Claude Sonnet
en las ejecuciones del agente y en la evaluación). Cada registro se conserva en su formato original (JSONL) y
convertido a Markdown con `convertir.py`, que oculta rutas personales, correos y tokens. No se usaron claves API:
Claude Code se autentica con la sesión del usuario y las APIs del BCRP e INEI son públicas.

| Carpeta | Archivo | Qué documenta |
|---|---|---|
| `desarrollo/` | `sesion_desarrollo.md` (el JSONL original no se publica porque contiene datos de la cuenta) | Conversación completa de desarrollo: lectura del enunciado y de las sesiones 04 y 16, plan, servidor MCP, pruebas, Skills, correcciones (estimador departamental, diseño APA, búsqueda de series, numeración de figuras), evaluación, informe y README |
| `mcp/` | `pytest_resultado.txt` | Ejecución de las 13 pruebas (10 del servidor MCP y 3 de las Skills) |
| `mcp/` | `robustez_datos_inexistentes.md` | El agente consulta un periodo sin datos y una serie inexistente e informa el error sin inventar cifras |
| `skills/` | `demo_mapa_lenguaje_natural.md` | "Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024": activa `mapeando-enaho`, detecta que falta la base y ejecuta `limpiando-enaho` |
| `skills/` | `demo_invocacion_directa_graficando.md` | Invocación individual `/graficando-enaho sexo 6` |
| `integracion/` | `ejecucion_integrada.md` | Ejecución definitiva: 4 herramientas MCP y 4 Skills en una misma ejecución, desde cero hasta el informe |
| `integracion/ejecucion_1/` | `ejecucion_integrada.md`, `productos/` | Primera ejecución y sus productos; motivó dos correcciones (búsqueda de la serie del PBI y numeración de figuras) |
| `evaluacion/` | `<pregunta>_modo<A|B>.md` | Las 20 llamadas del experimento comparativo, con herramientas usadas y respuesta |
