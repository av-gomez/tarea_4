---
name: graficando-enaho
description: Genera gráficos en formato APA 7 (Times New Roman, título en cursiva, nota con fuente) de la pobreza monetaria de la ENAHO 2024 del INEI por área urbana y rural, sexo, grupo de edad, sexo del jefe de hogar, región natural, dominio o departamento, con estimaciones ponderadas e intervalos de confianza. Úsala cuando pidan graficar, visualizar o comparar la pobreza en el Perú entre grupos o regiones con la ENAHO.
argument-hint: "[area|sexo|edad|sexo_jefe|region|dominio|departamento|extrema|todos] [numero de figura]"
---

# Graficar la pobreza con la ENAHO 2024

1. Si no existen `salidas/personas_2024.parquet` y `salidas/indicadores.csv`, usa primero la skill
   `limpiando-enaho` (ejecuta `uv run .claude/skills/limpiando-enaho/scripts/limpiar.py`) y comprueba que su
   validación esté aprobada. Si el script de gráficos sale con código 2, es por esto.
2. Traduce el pedido a un tipo de gráfico:

   | Pedido | `--tipo` |
   |---|---|
   | urbano y rural, área de residencia | `area` |
   | hombres y mujeres, sexo, género | `sexo` |
   | niños, jóvenes, adultos mayores, edad | `edad` |
   | hogares con jefa o jefe | `sexo_jefe` |
   | costa, sierra, selva | `region` |
   | dominios, Lima Metropolitana | `dominio` |
   | departamentos, regiones, ranking territorial | `departamento` |
   | pobreza extrema | `extrema` |

3. Ejecuta, con el número APA que corresponda a la figura en el documento:

   ```bash
   uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo <tipo> --numero <n>
   ```

4. El script imprime la tabla de cifras (también guardada en `tablas/<figura>.csv`). Describe la figura solo con
   esas cifras e indica si los intervalos de confianza se superponen: si se superponen, no afirmes que hay una
   diferencia. No presentes asociaciones como causas.

## Reglas de visualización (las aplica el script)

- Estimaciones ponderadas (`factor07 × mieperho` para territorio y jefatura; `facpob07` para sexo y edad).
- Barras desde cero, un solo tono, valor escrito en cada barra, línea del promedio nacional.
- Barras de error con IC 95 % por linealización de Taylor.
- Figura APA 7: "Figura n" en negrita, título en cursiva, nota con unidad, método y fuente
  ("INEI, ENAHO 2024"). PNG a 200 dpi en `figuras/`.
