---
name: limpiando-enaho
description: Limpia, une y valida los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2019-2025 del INEI (un año o la serie completa, más cualquier otro módulo) y produce bases de personas y hogares con pobreza monetaria, departamento, área y factores de expansión, más indicadores ponderados con intervalos de confianza. Úsala cuando pidan limpiar o procesar la ENAHO, calcular la pobreza (nacional, urbana, rural, por departamento, sexo o edad), validar cifras del INEI, o cuando otra skill necesite salidas/personas_2024.parquet o salidas/indicadores.csv.
argument-hint: "[--anio 2025 | --anios 2019 ... 2025] [--modulos 03 05] [--forzar]"
---

# Limpiar y validar la ENAHO (2019-2025)

Esta skill es la base del sistema: las skills `graficando-enaho`, `mapeando-enaho` e `informando-investigacion`
consumen lo que produce. Toda cifra de ENAHO del proyecto sale de aquí; nunca se escriben cifras a mano.

## Pasos

1. Si faltan `datos/966-Modulo34.zip` o `datos/966-Modulo02.zip`, descárgalos (código 966 = ENAHO 2024):

   ```bash
   uv run .claude/skills/limpiando-enaho/scripts/descargar.py
   ```

2. Ejecuta exactamente (añade `--forzar` solo si piden rehacer la base). Los zip que falten se descargan solos:

   ```bash
   uv run .claude/skills/limpiando-enaho/scripts/limpiar.py $ARGUMENTS
   uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anios 2019 2020 2021 2022 2023 2024 2025
   uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2025 --modulos 01 03 04 05
   ```

   Años: 2019 (código INEI 687), 2020 (737), 2021 (759), 2022 (784), 2023 (906), 2024 (966), 2025 (1031).
   Cada año se valida contra la pobreza oficial publicada por el INEI (nacional, urbana, rural y extrema).
   `--modulos` une otros módulos a nivel persona u hogar con validación m:1 (los de detalle se agregan con
   `explorando-enaho`).

3. Lee `salidas/validacion.txt`. Si dice `FALLO DE VALIDACION ESENCIAL`, detente e informa cuál verificación
   falló. No ajustes filtros, ponderadores ni cifras para forzar la coincidencia con el INEI.
4. Responde con las cifras de `salidas/indicadores.csv` (columna `valor_pct`, con su IC 95 % y CV), citando
   "INEI, ENAHO 2024" y el ponderador usado. Si el CV supera 15 %, advierte que la estimación es poco precisa.
5. Para una variable que no está en las bases, lee primero `reference.md` (diccionario y reglas).

## Qué produce

| Archivo | Contenido |
|---|---|
| `salidas/personas_2024.parquet` | 108,664 residentes habituales, una fila por persona, con `facpob07` |
| `salidas/hogares_2024.parquet` | 33,691 hogares, con `pondera = factor07 × mieperho` |
| `salidas/indicadores.csv` | Pobreza total y extrema por área, región, dominio, departamento, sexo, edad y jefatura |
| `salidas/validacion.txt` | 18 verificaciones, cada una APROBADA, FALLIDA o ADVERTENCIA |
| `salidas/{personas,hogares}_<año>.parquet`, `indicadores_<año>.csv`, `validacion_<año>.txt` | Lo mismo para cada año 2019-2025 |
| `salidas/serie_indicadores.csv` | Todos los años procesados en una tabla larga (columna `anio`) |

## Reglas que el script aplica (no se discuten)

- Lectura con `convert_categoricals=False`; `conglome`, `vivienda`, `hogar`, `codperso` y `ubigeo` como texto.
- Residentes habituales: `((p204 == 1) & (p205 == 2)) | ((p204 == 2) & (p206 == 1))`.
- Unión personas-hogares por `conglome`, `vivienda`, `hogar` con `merge(..., validate="m:1")`, comprobando que
  no se pierdan ni dupliquen filas.
- `departamento = ubigeo[:2]`, `urbano = estrato <= 5`, `pobre = pobreza <= 2`, `pobre_extremo = pobreza == 1`.
- Indicadores territoriales con la sumaria y `factor07 × mieperho` (método oficial del INEI); indicadores
  individuales (sexo, edad) con personas y `facpob07`. Nunca promedios simples.
- Error estándar por linealización de Taylor con UPM `conglome` y estratos departamento × estrato.
