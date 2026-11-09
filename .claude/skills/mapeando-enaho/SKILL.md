---
name: mapeando-enaho
description: Construye un mapa coroplético APA 7 de la pobreza monetaria (o extrema) por departamento del Perú con la ENAHO 2019-2025 del INEI (un año, mosaico de todos los años con escala común o mapa de cambio), uniendo por código ubigeo con el GeoJSON departamental (25 unidades, Lima y Callao separados) y validando contra la referencia oficial. Úsala cuando pidan un mapa, una distribución territorial o geográfica, o diferencias entre departamentos o regiones del Perú.
argument-hint: "[pobreza_monetaria|pobreza_extrema] [numero de figura]"
---

# Mapear la pobreza departamental

Varios años: `uv run .claude/skills/mapeando-enaho/scripts/mapas_series.py mosaico --numero <n>` (un mapa por
año con la misma escala) y `mapas_series.py cambio --desde 2019 --hasta 2025 --numero <n>` (escala divergente
centrada en 0). Requieren `salidas/serie_indicadores.csv`.

1. Si no existen `salidas/personas_2024.parquet` y `salidas/indicadores.csv`, usa primero la skill
   `limpiando-enaho` (`uv run .claude/skills/limpiando-enaho/scripts/limpiar.py`). Si el script de mapas sale con
   código 2, es por esto.
2. Ejecuta:

   ```bash
   uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_monetaria --numero <n>
   ```

   Usa `--indicador pobreza_extrema` si piden pobreza extrema.
3. Lee `salidas/validacion_mapa.txt`: debe decir 25/25 unidades unidas y, para pobreza monetaria, 25/25
   coincidencias con `referencias/pobreza_departamento_2024.csv`. Si no, informa la diferencia; no la corrijas
   a mano.
4. Describe el mapa con las cifras de `salidas/indicadores.csv` (departamentos con mayor y menor pobreza y su
   IC 95 %). El GeoJSON se descarga solo si falta.

## Reglas (las aplica el script)

- Unión por código: `ubigeo[:2]` (texto con cero inicial) con `FIRST_IDDP`; nunca por nombre.
- 25 unidades con dato; Lima (15) y Callao (07) separados; Callao se etiqueta con línea guía.
- Escala secuencial de un solo tono, desde 0 y en cortes de 10 puntos; leyenda "% de personas".
- Figura APA 7 con número, título en cursiva y nota (método, llave de unión y fuente). PNG en `mapas/`.
