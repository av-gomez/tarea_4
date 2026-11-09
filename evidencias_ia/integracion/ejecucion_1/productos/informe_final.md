# Inflación, actividad económica y brechas territoriales de la pobreza monetaria en el Perú, 2019-2024

## Pregunta de investigación

**Tema.** Evolución macroeconómica del Perú (2019-2024) y desigualdad territorial de la pobreza monetaria en 2024.

**Objetivo.** Describir cómo evolucionaron la inflación y la actividad económica entre 2019 y 2024 y medir las brechas de pobreza monetaria entre departamentos y entre áreas urbana y rural en 2024.

**Delimitación.** Periodo 2019-2024 para las series del BCRP; corte transversal 2024 para la ENAHO; unidad de análisis: personas residentes en hogares particulares; 25 unidades departamentales (Lima y Callao por separado).

## Fuentes y metodología

**BCRP** (Banco Central de Reserva del Perú [BCRP], 2026), consultado mediante el servidor MCP del proyecto: PN01273PM (IPC de Lima Metropolitana, variación % a 12 meses, mensual), PN01279PM (IPC subyacente) y PN37692AQ (PBI global, millones de S/ de 2007, trimestral). Fuente de las consultas: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/...`.

**ENAHO 2024** (Instituto Nacional de Estadística e Informática [INEI], 2025a): módulos 34 (sumaria) y 02 (miembros), 33 691 hogares y 108 664 personas. La pobreza monetaria se estima con ponderador factor07 × mieperho (método INEI), con error estándar, IC 95 % y coeficiente de variación (CV); se advierte cuando CV > 15 %. La limpieza pasó 18 de 18 validaciones, incluida la coincidencia de los 25 departamentos con la referencia oficial (INEI, 2025b).

## Resultados

**Hallazgo 1. La inflación subió con fuerza en 2021-2022 y regresó a un nivel bajo en 2024.** La inflación a 12 meses (PN01273PM) cerró diciembre en 1.90 % (2019), 1.97 % (2020), 6.43 % (2021), 8.46 % (2022), 3.24 % (2023) y 1.97 % (2024); el máximo mensual de 2022 fue 8.81 % (junio) y en enero de 2023 llegó a 8.66 % (Tabla 1, Figura 1). La inflación subyacente (PN01279PM) promedió 3.55 % frente a 4.08 % de la total en 2019-2024 (diferencia promedio 0.52 p.p.; correlación de niveles 0.89, descriptiva).

**Tabla 1**

*Inflación anual de Lima Metropolitana, 2019-2024 (PN01273PM)*

| Año | Promedio anual (%) | Diciembre (%) |
|---|---|---|
| 2019 | 2.14 | 1.90 |
| 2020 | 1.83 | 1.97 |
| 2021 | 3.97 | 6.43 |
| 2022 | 7.86 | 8.46 |
| 2023 | 6.31 | 3.24 |
| 2024 | 2.35 | 1.97 |

*Nota.* Variación porcentual a 12 meses del IPC de Lima Metropolitana. Fuente: BCRP, serie PN01273PM, 2019-2024 (`resumen_anual`).

**Hallazgo 2. La actividad cayó en 2020, se recuperó y en 2024 superó el nivel prepandemia.** El PBI global (PN37692AQ) tuvo un mínimo trimestral de S/ 95 976 millones de 2007 en 2020-T2 y un promedio trimestral de 121 711 en 2020, frente a 136 651 en 2019. En 2024 el promedio trimestral fue de 146 405 y el valor de 2024-T4, 155 868; entre 2019-T4 y 2024-T4 la variación fue de 8.35 % (Tabla 2).

**Tabla 2**

*PBI global trimestral, promedio por año, 2019-2024 (PN37692AQ)*

| Año | Promedio trimestral (millones S/ de 2007) |
|---|---|
| 2019 | 136 651 |
| 2020 | 121 711 |
| 2021 | 138 040 |
| 2022 | 141 931 |
| 2023 | 141 433 |
| 2024 | 146 405 |

*Nota.* Fuente: BCRP, serie PN37692AQ, 2019-T1 a 2024-T4 (`resumen_anual`).

**Hallazgo 3. En 2024 la pobreza rural superó a la urbana por unos 14.5 puntos porcentuales.** La pobreza monetaria nacional fue 27.58 % (IC 95 %: 26.59-28.57). En el área rural fue 39.30 % (IC 95 %: 37.80-40.81) y en la urbana 24.81 % (IC 95 %: 23.62-25.99); los intervalos no se superponen, por lo que la diferencia es estadísticamente distinguible (Tabla 3, Figura 2). La pobreza extrema fue 15.52 % en el área rural y 3.14 % en la urbana.

**Tabla 3**

*Pobreza monetaria por área, 2024*

| Área | Pobreza (%) | IC 95 % | CV (%) |
|---|---|---|---|
| Urbana | 24.81 | 23.62-25.99 | 2.4 |
| Rural | 39.30 | 37.80-40.81 | 2.0 |

*Nota.* Fuente: INEI, ENAHO 2024; ponderador factor07 × mieperho (`salidas/indicadores.csv`).

**Hallazgo 4. Entre departamentos la pobreza varió de 6.0 % a 45.0 %.** Cajamarca registró la mayor (45.01 %; IC 95 %: 40.84-49.17), seguida de Loreto (42.97 %) y Puno (39.94 %); Ica la menor (6.01 %; IC 95 %: 4.17-7.85), seguida de Moquegua (10.97 %) y Madre de Dios (11.15 %). Los intervalos de Cajamarca e Ica no se superponen. **Advertencia:** Ica, Moquegua y Madre de Dios tienen CV > 15 % (15.6 %, 16.2 % y 19.5 %), por lo que sus estimaciones son menos precisas; cuando los IC de dos departamentos se solapan no se afirma diferencia (Figura 3).

## Visualizaciones

![Figura 1. Inflación anual de Lima Metropolitana, 2019-2024](../figuras/inflacion_2019_2024.png)

**Figura 1**. *Inflación anual de Lima Metropolitana, 2019-2024.* Fuente: BCRP, PN01273PM.

![Figura 2. Pobreza monetaria por área, 2024](../figuras/pobreza_area.png)

**Figura 2**. *Pobreza monetaria por área, ENAHO 2024.* Fuente: INEI, ENAHO 2024.

![Figura 3. Pobreza monetaria por departamento, mapa](../mapas/pobreza_departamento.png)

**Figura 3**. *Pobreza monetaria por departamento, ENAHO 2024.* Fuente: INEI, ENAHO 2024; límites departamentales de D2CML (2024).

## Interpretación

El periodo combina una contracción profunda (2020), un repunte inflacionario (2021-2023) y una normalización en 2024, con la inflación por debajo del techo del rango meta de 3 % y el PBI sobre su nivel de 2019. La pobreza de 2024 muestra una geografía marcada: brecha urbano-rural y valores altos en departamentos de sierra y selva norte (Cajamarca, Loreto, Puno) frente a la costa sur (Ica, Moquegua). La yuxtaposición de ambas fuentes es **descriptiva**: la ENAHO es de un solo año y no permite atribuir los niveles de pobreza a la inflación ni a la actividad; no se afirma causalidad.

## Limitaciones

- El IPC (PN01273PM) cubre Lima Metropolitana y no representa los precios de todos los departamentos.
- La ENAHO es un corte transversal 2024: no hay evolución de la pobreza en este análisis.
- Los niveles de agregación difieren (serie nacional/Lima frente a departamentos y áreas).
- Error de muestreo: Ica, Moquegua y Madre de Dios con CV > 15 %.
- La búsqueda de una serie de variación % del PBI no devolvió resultados; se usó el PBI en niveles (PN37692AQ) y no se calcularon tasas anuales a mano.
- Ninguna herramienta MCP falló en esta ejecución.

## Reproducibilidad

```bash
uv sync
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo todos
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv
uv run .claude/skills/informando-investigacion/scripts/publicar.py
```

Series BCRP: PN01273PM, PN01279PM, PN37692AQ. Archivos: `salidas/indicadores.csv`, `tablas/*.csv`, `figuras/`, `mapas/`, `informes/afirmaciones.csv`.

## Referencias

Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos]. https://estadisticas.bcrp.gob.pe/estadisticas/series/

D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub. https://github.com/d2cml-ai/Data-Science-Python

Instituto Nacional de Estadística e Informática. (2025a). *Encuesta Nacional de Hogares sobre Condiciones de Vida y Pobreza 2024* [Base de datos: módulos 02 y 34]. https://proyectos.inei.gob.pe/microdatos/

Instituto Nacional de Estadística e Informática. (2025b). *Perú: Evolución de la pobreza monetaria 2015-2024. Informe técnico*. INEI.
