---
name: explorando-enaho
description: Explora y usa cualquiera de los 29 módulos de la ENAHO del INEI (2019-2025) - vivienda, educación, salud, empleo e ingresos, gastos, programas sociales, gobernabilidad - buscando variables en el diccionario oficial y estimando indicadores ponderados con intervalos de confianza por año, área, departamento, sexo, edad o condición de pobreza. Úsala cuando pidan analizar educación, salud, seguro, empleo, informalidad, ingresos, servicios básicos, programas sociales u otra característica de hogares o personas con la ENAHO, o comparar pobres y no pobres.
argument-hint: "[tema o variable] [años]"
---

# Explorar cualquier módulo de la ENAHO

1. Catálogo de módulos y años: `uv run .claude/skills/explorando-enaho/scripts/explorar.py modulos`.
2. Encuentra la variable en el diccionario oficial del archivo (descarga el módulo si falta):

   ```bash
   uv run .claude/skills/explorando-enaho/scripts/explorar.py diccionario --anio 2025 --modulo 04 --buscar seguro
   ```

   Lee la etiqueta y los códigos de valores antes de decidir la condición. Si un año no tiene la variable,
   dilo; no la sustituyas sin explicarlo.
3. Estima el indicador (se une a la base limpia del año; si falta, ejecuta primero `limpiando-enaho`):

   ```bash
   uv run .claude/skills/explorando-enaho/scripts/explorar.py indicador --modulo 04 --variable p4191 \
       --condicion "==1" --nombre afiliacion_essalud --anios 2019 2025 --por pobre
   ```

   - `--condicion` crea un indicador 0/1 (porcentaje); sin ella se estima la media (p. ej. ingresos).
   - `--universo "edad >= 25"` restringe la población; `--por` desagrega (area, departamento, sexo, grupo_edad,
     region_natural, pobre, sexo_jefe).
   - Módulos de detalle (07 gastos y otros con varias filas por hogar): `--agregar sum|mean|max|count` y
     `--unidad hogar`.
4. Usa las cifras de `tablas/indicador_<nombre>.csv` con su IC 95 % y CV; advierte si CV > 15 %. Para graficar
   pobres frente a no pobres usa `graficando-enaho` (`visualizar.py perfil --indicadores <nombres>`).

Reglas que aplica el script: llaves como texto, unión validada (m:1 o 1:1) sin duplicar filas, códigos de
"no sabe" (99, 999999...) excluidos e informados, ponderador `facpob07` (personas) o `factor07` (hogares) y
error estándar por linealización de Taylor.
