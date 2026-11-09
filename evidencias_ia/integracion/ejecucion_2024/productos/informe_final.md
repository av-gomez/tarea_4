# Inflación, actividad económica y brechas territoriales de la pobreza en el Perú, 2019-2024

## 1. Pregunta de investigación

**Tema.** Evolución de la inflación y de la actividad económica del Perú entre 2019 y 2024, y brechas territoriales de la pobreza monetaria en 2024.

**Objetivo.** Describir la trayectoria de ambas variables macroeconómicas y cuantificar la desigualdad de la pobreza entre departamentos y entre áreas urbana y rural al cierre del periodo.

**Delimitación.** Series nacionales 2019-2024 (BCRP); corte transversal 2024 (ENAHO); 25 departamentos (Lima y Callao por separado); personas residentes habituales.

## 2. Fuentes y metodología

**BCRP** (Banco Central de Reserva del Perú, 2026): PN01273PM, inflación a 12 meses del IPC de Lima Metropolitana (mensual); PN02516AQ, PBI global, índice 2007 = 100 (trimestral). Cifras obtenidas con el servidor MCP (`resumen_anual`, `resumen`, `graficar_serie`).

**ENAHO 2024** (Instituto Nacional de Estadística e Informática, 2025): módulos 34 (sumaria) y 02 (miembros), residentes habituales, pobreza monetaria (`pobreza ≤ 2`), ponderador `factor07 × mieperho`. Error estándar por linealización de Taylor (UPM `conglome`, estratos departamento × estrato); IC 95 %. La validación de la skill `limpiando-enaho` aprobó 18 de 18 verificaciones (nacional 27.58 %, IC 95 % 26.59-28.57; CV 1.8 %).

Todas las comparaciones son descriptivas y no causales.

## 3. Resultados

**Hallazgo 1. La inflación se disparó en 2021-2022 y volvió al rango meta en 2024.** La inflación a 12 meses cerró en 1.90 % en diciembre de 2019 y en 1.97 % en diciembre de 2020; subió a 6.43 % (diciembre de 2021) y a 8.46 % (diciembre de 2022); bajó a 3.24 % (diciembre de 2023) y a 1.97 % (diciembre de 2024). El promedio anual fue 7.86 % en 2022 y 2.35 % en 2024. El máximo del periodo fue 8.81 % en junio de 2022 (PN01273PM, 2019-01 a 2024-12; Figura 1).

**Hallazgo 2. La actividad cayó en 2020 y en 2024 superaba su nivel prepandemia.** El índice del PBI pasó de 180.0 en 2019-T4 a un mínimo de 120.1 en 2020-T2, y llegó a 195.0 en 2024-T4, una variación de +8.35 % frente a 2019-T4 (PN02516AQ, 2019-T4 a 2024-T4; Figura 2). El promedio anual fue 170.98 en 2019, 152.28 en 2020 y 183.18 en 2024. El PBI de 2023 (176.96 promedio) quedó por debajo del de 2022 (177.58).

**Hallazgo 3. La pobreza rural supera a la urbana en 14.5 puntos porcentuales.** En 2024 la pobreza monetaria fue 39.30 % en el área rural (IC 95 %: 37.80-40.81) y 24.81 % en la urbana (IC 95 %: 23.62-25.99); los intervalos no se superponen (INEI, ENAHO 2024, `factor07 × mieperho`; Figura 3).

**Hallazgo 4. Entre departamentos hay una brecha amplia, con grupos estadísticamente indistinguibles.** Cajamarca tuvo la mayor pobreza (45.01 %; IC 95 %: 40.84-49.17) e Ica la menor (6.01 %; IC 95 %: 4.17-7.85), una diferencia de 39.0 puntos con intervalos separados. Sin embargo, el IC de Cajamarca se superpone con los de Loreto (42.97 %; 38.81-47.13) y Puno (39.94 %; 35.43-44.45), por lo que no se afirma que Cajamarca supere a esos departamentos. Lima registró 27.07 % (24.71-29.43) y Callao 33.86 % (29.16-38.56) (Figuras 4 y 5). **Advertencia:** el CV supera 15 % en Ica (15.61 %), Moquegua (16.23 %; 10.97 %) y Madre de Dios (19.50 %; 11.15 %); sus estimaciones son poco precisas.

## 4. Visualizaciones

![Figura 1](../figuras/inflacion_2019_2024.png)

![Figura 2](../figuras/pbi_2019_2024.png)

![Figura 3](../figuras/pobreza_area.png)

![Figura 4](../figuras/pobreza_departamento.png)

![Figura 5](../mapas/pobreza_departamento.png)

## 5. Interpretación

El periodo combina un choque de actividad en 2020, una aceleración de precios en 2021-2022 y una normalización posterior. En 2024 la inflación (1.97 %) y la actividad convivían con una pobreza territorialmente muy desigual: la rural y los departamentos del norte y sur andino y de la Amazonía (Cajamarca, Loreto, Puno, Pasco, Huánuco) concentran los valores altos, y la costa sur (Ica, Moquegua) los bajos. Estos patrones son asociaciones descriptivas: la ENAHO es un corte transversal de 2024 y no permite atribuir la pobreza a la inflación ni al PBI.

## 6. Limitaciones

- El IPC cubre solo Lima Metropolitana, y el PBI es nacional; la ENAHO se desagrega por departamento: los niveles de agregación difieren.
- Corte transversal 2024: no se estima la evolución de la pobreza 2019-2024 con microdatos.
- Error muestral: varios departamentos tienen IC superpuestos y tres tienen CV > 15 %.
- Las herramientas MCP y las skills no fallaron. Las cifras del PBI no se verificaron con `verificar.py` (solo inflación y pobreza).

## 7. Reproducibilidad

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area --numero 3
uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento --numero 4
uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero 5
uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv
uv run .claude/skills/informando-investigacion/scripts/publicar.py
```

Series: PN01273PM, PN02516AQ (https://estadisticas.bcrp.gob.pe/estadisticas/series/api). Tablas en `tablas/`, indicadores en `salidas/indicadores.csv`. Las Figuras 1 y 2 se generaron con la herramienta `graficar_serie` del MCP.

## 8. Referencias

Banco Central de Reserva del Perú. (2026). *BCRPData: Series estadísticas* [Base de datos]. https://estadisticas.bcrp.gob.pe/estadisticas/series/

D2CML. (2024). *Límites departamentales del Perú* [Archivo GeoJSON]. GitHub. https://github.com/d2cml-ai/Data-Science-Python

Instituto Nacional de Estadística e Informática. (2025). *Encuesta Nacional de Hogares sobre Condiciones de Vida y Pobreza 2024* [Base de datos: módulos 02 y 34]. https://proyectos.inei.gob.pe/microdatos/
