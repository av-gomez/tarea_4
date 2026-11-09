# Verificación manual de afirmaciones numéricas del informe final

Complementa la verificación automática (`informes/verificacion.md`, 6 de 6 coincidencias). Aquí se comprueban a
mano cinco afirmaciones de `informes/informe_final.md`, de ambas fuentes, con procedimientos que no usan el
servidor MCP ni las Skills: consulta directa a la API pública del BCRP con `curl` y comparación con la referencia
oficial de pobreza departamental (`referencias/pobreza_departamento_2024.csv`, sesión 16 del curso, con cifras
del INEI). Fecha de comprobación: 8 de noviembre de 2026.

**Tabla 1**

*Afirmaciones del informe comprobadas manualmente*

| N.º | Afirmación del informe | Valor del informe | Valor comprobado | Fuente o procedimiento | Coincide | Diferencia observada |
|:---|:---|---:|---:|:---|:---:|:---|
| 1 | El índice del PBI llegó a 195.0 en 2024-T4, +8.35 % frente a 2019-T4 (Hallazgo 2) | 195.0; 8.35 % | 195.0226 y 180.0002; 195.0226 / 180.0002 − 1 = 8.346 % | `curl https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN02516AQ/json/2019-4/2024-4` y cálculo con calculadora | Sí | Ninguna (redondeo a dos decimales) |
| 2 | Mínimo del PBI de 120.1 en 2020-T2 (Hallazgo 2) | 120.1 | 120.0850 | Misma consulta, periodo `T2.20` | Sí | Ninguna (redondeo a un decimal) |
| 3 | Máximo de la inflación a 12 meses: 8.81 % en junio de 2022 (Hallazgo 1) | 8.81 % | 8.8126 % | `curl .../api/PN01273PM/json/2022-6/2022-6`; página web: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html | Sí | Ninguna |
| 4 | Pobreza monetaria de Callao en 2024: 33.86 % (Hallazgo 4) | 33.86 % | 33.9 % | `referencias/pobreza_departamento_2024.csv`, código 07 | Sí | 0.04 p.p. por redondeo de la referencia a un decimal |
| 5 | Pobreza monetaria de Ica en 2024: 6.01 %, la menor del país (Hallazgo 4) | 6.01 % | 6.0 % y mínimo de los 25 valores | `referencias/pobreza_departamento_2024.csv`, código 11; orden de la columna `pobreza_pct` | Sí | 0.01 p.p. por redondeo |

*Nota.* Las afirmaciones 1 a 3 provienen del BCRP y las 4 y 5 de la ENAHO 2024 (INEI). La tolerancia aceptada es
el redondeo de la cifra publicada (0.05 para valores con un decimal). Ninguna afirmación verificada difiere de su
fuente más allá del redondeo.

## Manejo de errores y datos inexistentes

- El servidor responde con un error explícito cuando un código de serie no existe
  (`test_codigo_inexistente_da_un_error_claro`), cuando no hay datos en el periodo pedido o cuando se comparan
  series de frecuencias incompatibles (`test_comparar_series_alinea_y_rechaza_frecuencias_distintas`).
- `evidencias_ia/mcp/robustez_datos_inexistentes.md` registra una consulta real al agente por la inflación de
  diciembre de 2030 y por una serie inexistente: el agente recibe el error de la herramienta y lo informa en lugar
  de inventar una cifra.
- `limpiar.py` se detiene con código de salida 1 y no guarda la base si una validación esencial falla; esto
  ocurrió en el desarrollo cuando la pobreza departamental se estimó con `facpob07` (diferencia de 0.5 p.p. con la
  referencia): se corrigió el método (estimador oficial `factor07 × mieperho`), no las cifras.
