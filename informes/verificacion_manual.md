# Verificación manual de afirmaciones numéricas del informe final (2019-2025)

Complementa la verificación automática (`informes/verificacion.md`, 18 de 18 coincidencias). Se comprobaron a
mano siete afirmaciones de `informes/informe_final.md`, de ambas fuentes, con procedimientos que no usan el
servidor MCP ni las Skills: consulta directa a la API pública del BCRP con `curl` y recálculo desde los archivos
`.dta` originales de la sumaria (módulo 34) con pandas, con el ponderador `factor07 × mieperho`. Fecha: 8 de
noviembre de 2026. La verificación manual del informe anterior (ENAHO 2024) se conserva en
`evidencias_ia/integracion/ejecucion_2024/productos/verificacion_manual.md`.

**Tabla 1**

*Afirmaciones del informe final comprobadas manualmente*

| N.º | Afirmación del informe | Valor del informe | Valor comprobado | Procedimiento | Coincide | Diferencia |
|:---|:---|---:|---:|:---|:---:|:---|
| 1 | Máximo de la inflación a 12 meses en junio de 2022 | 8.81 % | 8.8126 % | `curl .../api/PN01273PM/json/2022-6/2022-6` | Sí | Ninguna (redondeo) |
| 2 | Inflación a 12 meses de diciembre de 2025 | 1.51 % | 1.5088 % | `curl .../api/PN01273PM/json/2025-12/2025-12` | Sí | Ninguna (redondeo) |
| 3 | El PBI real cayó 10.93 % en 2020 y creció 13.42 % en 2021 | -10.93 %; 13.42 % | -10.9333 %; 13.4166 % | `curl .../api/PM04923AA/json/2020/2021` | Sí | Ninguna (redondeo) |
| 4 | Pobreza urbana: de 14.58 % (2019) a 23.41 % (2025) | 14.58 %; 23.41 % | 14.575 %; 23.413 % | Sumarias 2019 (687) y 2025 (1031), `estrato <= 5` | Sí | Ninguna (redondeo) |
| 5 | Callao: aumento de 17.81 puntos entre 2019 y 2025 | +17.81 p.p. | 14.344 % -> 32.150 %; +17.805 p.p. | Sumarias 2019 y 2025, `ubigeo[:2] == "07"` | Sí | Ninguna (redondeo) |
| 6 | Amazonas: reducción de 10.10 puntos entre 2019 y 2025 | -10.10 p.p. | 30.489 % -> 20.391 %; -10.098 p.p. | Sumarias 2019 y 2025, `ubigeo[:2] == "01"` | Sí | Ninguna (redondeo) |
| 7 | Ica tuvo la pobreza más baja en 2025 | 4.48 % | 4.480 % | Sumaria 2025, `ubigeo[:2] == "11"` | Sí | Ninguna |

*Nota.* Las afirmaciones 1 a 3 provienen del BCRP y las 4 a 7 de la ENAHO (INEI). Tolerancia: redondeo de la
cifra publicada en el informe. URL base de la API: https://estadisticas.bcrp.gob.pe/estadisticas/series/api.
Página web para comprobar la inflación: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html.

## Manejo de errores y datos inexistentes

- El servidor responde con un error explícito cuando un código de serie no existe
  (`test_codigo_inexistente_da_un_error_claro`), cuando no hay datos en el periodo pedido o cuando se comparan
  series de frecuencias incompatibles (`test_comparar_series_alinea_y_rechaza_frecuencias_distintas`).
- `evidencias_ia/mcp/robustez_datos_inexistentes.md` registra una consulta real al agente por la inflación de
  diciembre de 2030 y por una serie inexistente: el agente recibe el error y lo informa sin inventar cifras.
- `limpiar.py` se detiene con código de salida 1 y no guarda la base si una validación esencial falla. En el
  desarrollo ocurrió cuando la pobreza departamental se estimó con `facpob07` (0.5 p.p. de diferencia con la
  referencia): se corrigió el método (estimador oficial `factor07 × mieperho`), no las cifras.
- `explorar.py` informa las variables inexistentes en un año, excluye y reporta los códigos de "no sabe" y
  rechaza unir módulos de detalle sin agregarlos.
