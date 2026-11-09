# Plan de investigación

## Pregunta reformulada

¿Cómo evolucionaron la pobreza monetaria y sus brechas territoriales (área, región natural, departamento) y
sociales (edad, sexo, jefatura del hogar, acceso a servicios, seguro, educación y empleo) en el Perú entre 2019
y 2025, y cómo se compara esa trayectoria con la inflación y el crecimiento de la actividad económica del mismo
periodo?

**Objetivo.** Describir la trayectoria anual de la pobreza monetaria 2019-2025 y de sus brechas, y ponerla en
paralelo con la evolución de los precios y del PBI.

**Delimitación.** Periodo 2019-2025; Perú, nivel nacional, área urbana/rural, región natural y 25 departamentos
(Lima y Callao por separado); unidad de análisis: personas residentes habituales (ponderador
`factor07 × mieperho` para pobreza; `facpob07` para grupos de personas e indicadores de otros módulos).

## Qué aporta cada fuente

- **BCRP** (series nacionales, servidor MCP `bcrp`):
  - PN01273PM: inflación a 12 meses del IPC de Lima Metropolitana, mensual, 2019-01 a 2025-12.
  - PM04923AA: PBI, variación porcentual real anual, 2019-2025.
- **ENAHO 2019-2025, INEI** (microdatos): pobreza monetaria y extrema con IC 95 % por año y desagregación
  (módulos 34 y 02); brechas entre pobres y no pobres con los módulos 01 (agua, desagüe, electricidad),
  03 (secundaria completa), 04 (EsSalud, SIS) y 05 (ocupación).
- La comparación entre fuentes es **descriptiva y no causal**: difieren la cobertura (IPC de Lima frente a
  pobreza nacional), la frecuencia (mensual/anual) y no se modela ningún mecanismo.

## Herramientas

- MCP `bcrp`: `graficar_serie` (Figuras 1 y 2), `resumen_anual`, `resumen`, `serie`.
- Skills: `limpiando-enaho` (`--anios 2019 … 2025`, validación contra el INEI), `explorando-enaho`
  (`explorar.py diccionario` e `indicador --por pobre`), `graficando-enaho` (`visualizar.py`),
  `mapeando-enaho` (`mapas_series.py mosaico` y `cambio`), `informando-investigacion` (`verificar.py`,
  `publicar.py`).

## Figuras y tablas (orden de aparición)

1 inflación (BCRP); 2 crecimiento del PBI (BCRP); Tabla 1 indicadores macroeconómicos; 3 inflación y pobreza;
Tabla 2 pobreza por área; 4 distribución gasto/línea; 5 waffle 2025; 6 evolución por área; Tabla 3 grupos
sociales; 7 calor departamental; 8 pendiente 2019-2025; 9 mosaico de mapas; 10 mapa de cambio; Tabla 4
departamentos con cambio significativo; 11 perfil de brechas; Tabla 5 brechas pobres/no pobres.
