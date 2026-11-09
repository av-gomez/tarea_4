# Evaluación: mixta_gasto_usd_modoB

Fuente: `mixta_gasto_usd_modoB.jsonl` (convertido con evidencias_ia/convertir.py; rutas personales, correos y tokens ocultados).

## Configuración de la sesión

- Modelo: claude-sonnet-5-5
- Servidores MCP: [{"name": "bcrp", "status": "connected", "source": "dynamic"}]
- Skills: graficando-enaho, informando-investigacion, limpiando-enaho, mapeando-enaho, deep-research, cowork-plugin-management:cowork-plugin-customizer, cowork-plugin-management:create-cowork-plugin, data:analyze, data:build-dashboard, data:create-viz, data:data-context-extractor, data:explore-data, data:validate-data, data:write-query, design, design-sync, dataviz, update-config, verify, debug, code-review, simplify, batch, fewer-permission-prompts, doctor, loop, schedule, claude-api, workflow-authoring, run, run-skill-generator, plugin-authoring, anthropic-skills:built-in-browser, anthropic-skills:chrome-browser, anthropic-skills:computer-use, anthropic-skills:deep-research, anthropic-skills:docs, anthropic-skills:docx, anthropic-skills:google-workspace, anthropic-skills:import-memory, anthropic-skills:morning, anthropic-skills:pdf, anthropic-skills:pptx, anthropic-skills:skill-creator, anthropic-skills:xlsx
- Herramientas: Bash, Glob, Grep, Read, Skill, StructuredOutput, mcp__bcrp__buscar_series, mcp__bcrp__comparar_series, mcp__bcrp__graficar_serie, mcp__bcrp__resumen, mcp__bcrp__resumen_anual, mcp__bcrp__serie

## 1. Asistente (Claude)

**Herramienta:** `mcp__bcrp__serie`

```json
{
 "codigo": "PN01206PM",
 "desde": "2024-01",
 "hasta": "2024-12"
}
```

## 2. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cd C:/Users/[usuario]/Documents/tarea_4 && ls; ls salidas datos 2>/dev/null | head -50; cat .claude/skills/limpiando-enaho/scripts/limpiar.py | head -60"
}
```

## 3. Resultado

**Resultado de la herramienta:**

```
{"codigo":"PN01206PM","nombre":"Tipo de cambio - promedio del periodo (S/ por US$) - Interbancario - Venta","frecuencia":"Mensual","n":12,"datos":[{"periodo":"2024-01","valor":3.74190952380952},{"periodo":"2024-02","valor":3.82895238095238},{"periodo":"2024-03","valor":3.71003684210526},{"periodo":"2024-04","valor":3.7167},{"periodo":"2024-05","valor":3.73287727272727},{"periodo":"2024-06","valor":3.78837894736842},{"periodo":"2024-07","valor":3.76611},{"periodo":"2024-08","valor":3.742925},{"periodo":"2024-09","valor":3.76989523809524},{"periodo":"2024-10","valor":3.75581363636364},{"periodo":"2024-11","valor":3.780265},{"periodo":"2024-12","valor":3.73655789473684}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01206PM/json/2024-1/2024-12"}
```

## 4. Resultado

**Resultado de la herramienta:**

```
CLAUDE.md
comun
datos
evaluacion
evidencias_ia
figuras
informes
mapas
mcp
pyproject.toml
referencias
salidas
tablas
tests
uv.lock
datos:
966-Modulo02.zip
966-Modulo34.zip
cache_bcrp
catalogo_bcrp.csv
peru_departamental_simple.geojson

salidas:
hogares_2024.parquet
indicadores.csv
personas_2024.parquet
validacion.txt
validacion_mapa.txt
"""Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024 y valida contra el INEI.

    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py            # año 2024 (código INEI 966)
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --forzar   # rehace aunque exista la base

Pipeline (siempre en este orden; ver reference.md):
  1. Leer los .dta dentro de los zip con convert_categoricals=False y llaves como texto (sin perder ceros).
  2. Normalizar nombres de columnas (minúsculas, "aÑo" -> "anio").
  3. Filtrar residentes habituales: ((p204==1)&(p205==2)) | ((p204==2)&(p206==1)).
  4. Unir personas (m) con hogares (1) por conglome, vivienda, hogar con validate="m:1".
  5. Construir departamento = ubigeo[:2], área (estrato<=5 urbano), pobre = pobreza<=2, etc.
  6. Estimar indicadores ponderados (facpob07) con error de muestreo -> salidas/indicadores.csv.
  7. Validar contra cifras oficiales -> salidas/validacion.txt. Si una validación esencial falla, sale con
     código 1 y NO guarda la base: nunca se ajustan resultados para que coincidan.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def _raiz() -> Path:
    p = Path(__file__).resolve()
    for d in p.parents:
        if (d / "pyproject.toml").exists():
            return d
    return Path.cwd()


RAIZ = _raiz()
sys.path.insert(0, str(RAIZ))
from comun.estimacion import por_grupo, proporcion  # noqa: E402

CODIGOS_INEI = {2024: 966}
LLAVES = ["conglome", "vivienda", "hogar"]
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios",
    "18": "Moquegua", "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna",
    "24": "Tumbes", "25": "Ucayali",
}
DOMINIOS = {1: "Costa Norte", 2: "Costa Centro", 3: "Costa Sur", 4: "Sierra Norte", 5: "Sierra Centro",
            6: "Sierra Sur", 7: "Selva", 8: "Lima Metropolitana"}
REGION_NATURAL = {1: "Costa", 2: "Costa", 3: "Costa", 8: "Costa", 4: "Sierra", 5: "Sierra", 6: "Sierra",
                  7: "Selva"}
# Cifras oficiales publicadas para 2024 (INEI, 2025; sesión 16 del curso)
REFERENCIA = {"pobreza_nacional": 27.6, "residentes": 108_664, "filas_modulo02": 117_721, "hogares": 33_691,
              "urbana": 24.8, "rural": 39.3, "extrema": 5.5, "departamentos": 25}
TOL_NACIONAL = 0.1     # puntos porcentuales (exigencia de la tarea)
TOL_AREA = 0.15        # redondeo a un decimal de la cifra publicada
```

## 5. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cd C:/Users/[usuario]/Documents/tarea_4 && python -I -c \"\nimport pandas as pd\nfor f in ['salidas/hogares_2024.parquet','salidas/personas_2024.parquet']:\n    d=pd.read_parquet(f); print(f,d.shape,[c for c in d.columns if c in('gashog2d','mieperho','factor07','facpob07')])\n\""
}
```

## 6. Resultado

**Resultado de la herramienta:**

```
This Bash command contains multiple operations. The following part requires approval: python -I -c '
import pandas as pd
for f in ['\''salidas/hogares_2024.parquet'\'','\''salidas/personas_2024.parquet'\'']:
    d=pd.read_parquet(f); print(f,d.shape,[c for c in d.columns if c in('\''gashog2d'\'','\''mieperho'\'','\''factor07'\'','\''facpob07'\'')])
'
```

## 7. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cd C:/Users/[usuario]/Documents/tarea_4 && uv run python -c \"\nimport pandas as pd\nfor f in ['salidas/hogares_2024.parquet','salidas/personas_2024.parquet']:\n    d=pd.read_parquet(f); print(f,d.shape,[c for c in d.columns if c in('gashog2d','mieperho','factor07','facpob07')])\n\""
}
```

## 8. Resultado

**Resultado de la herramienta:**

```
salidas/hogares_2024.parquet (33691, 23) ['mieperho', 'factor07']
salidas/personas_2024.parquet (108664, 30) ['mieperho', 'facpob07', 'factor07']
```

## 9. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cd C:/Users/[usuario]/Documents/tarea_4 && uv run python -c \"\nimport zipfile,io,pandas as pd\nz=zipfile.ZipFile('datos/966-Modulo34.zip');print([n for n in z.namelist() if n.lower().endswith('.dta')])\nn=[n for n in z.namelist() if n.lower().endswith('.dta') and 'sumaria' in n.lower()][0]\nd=pd.read_stata(io.BytesIO(z.read(n)),convert_categoricals=False)\nd.columns=[c.lower() for c in d.columns]\nprint(d.shape,d[['gashog2d','mieperho','factor07']].describe())\nd=d[d.gashog2d.notna()&(d.mieperho>0)]\nw=d.factor07*d.mieperho\npc=d.gashog2d/(12*d.mieperho)\nm=(pc*w).sum()/w.sum()\ntc=sum([3.74190952380952,3.82895238095238,3.71003684210526,3.7167,3.73287727272727,3.78837894736842,3.76611,3.742925,3.76989523809524,3.75581363636364,3.780265,3.73655789473684])/12\nprint(len(d),m,tc,m/tc)\n\""
}
```

## 10. Resultado

**Resultado de la herramienta:**

```
['966-Modulo34/sumaria-2024-12g.dta', '966-Modulo34/sumaria-2024.dta']
(33691, 242)             gashog2d      mieperho      factor07
count   33691.000000  33691.000000  33691.000000
mean    29454.134372      3.260277    307.524628
std     22123.533158      1.762953    314.511841
min       825.153381      1.000000      1.116235
25%     14451.278809      2.000000    120.713737
50%     23945.349609      3.000000    230.468079
75%     37582.527344      4.000000    352.102783
max    308555.781250     17.000000   1996.372314
33691 774.6574032092744 3.7558684780132143 206.25253726111677
```

## 11. Asistente (Claude)

**Herramienta:** `Bash`

```json
{
 "command": "cd C:/Users/[usuario]/Documents/tarea_4 && grep -n \"sumaria\" .claude/skills/limpiando-enaho/scripts/limpiar.py | head; uv run python -c \"\nimport zipfile,io,pandas as pd\nz=zipfile.ZipFile('datos/966-Modulo34.zip')\nfor n in ['966-Modulo34/sumaria-2024.dta','966-Modulo34/sumaria-2024-12g.dta']:\n    d=pd.read_stata(io.BytesIO(z.read(n)),convert_categoricals=False);d.columns=[c.lower() for c in d.columns]\n    w=d.factor07*d.mieperho;print(n,d.shape,((d.gashog2d/(12*d.mieperho))*w).sum()/w.sum())\n\""
}
```

## 12. Resultado

**Resultado de la herramienta:**

```
1:"""Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO 2024 y valida contra el INEI.
83:        nombre = sorted(nombres, key=len)[0]          # sumaria-2024.dta antes que sumaria-2024-12g.dta
104:    hog, n34 = leer_dta(zip34, "sumaria")
106:    meta = {"archivo_sumaria": n34, "archivo_miembros": n02}
113:    chequear("Hogares en la sumaria", len(hog) == REFERENCIA["hogares"],
115:    chequear("Llaves de hogar únicas en la sumaria", not hog.duplicated(LLAVES).any(),
136:             f"{n_antes:,} personas antes y {len(base):,} después; {sin_hogar} sin hogar en la sumaria")
185:    # Pobreza: dos estimadores (oficial con la sumaria y alternativo con personas)
189:    chequear("Pobreza monetaria nacional (sumaria, factor07 x mieperho; metodo INEI) a <= 0.1 p.p. de 27.6 %",
230:    Desagregaciones territoriales y por jefatura: sumaria con factor07 x mieperho (metodo oficial INEI).
966-Modulo34/sumaria-2024.dta (33691, 163) 774.6574030352047
966-Modulo34/sumaria-2024-12g.dta (33691, 242) 774.6574032092744
```

## 13. Asistente (Claude)

**Herramienta:** `StructuredOutput`

```json
{
 "valor": 206.25,
 "unidad": "US$ por persona al mes",
 "fuente": "INEI, ENAHO 2024 (módulo 34 Sumaria, datos/966-Modulo34.zip, sumaria-2024.dta, 33 691 hogares): gasto per cápita mensual = gashog2d/(12×mieperho), promedio ponderado por factor07×mieperho = S/ 774.66. BCRP, serie PN01206PM (tipo de cambio interbancario venta, promedio mensual), promedio simple de los 12 meses de 2024 (2024-01 a 2024-12) = 3.7559 S/ por US$. Resultado: 774.66 / 3.7559 = US$ 206.25."
}
```

## 14. Resultado

**Resultado de la herramienta:**

```
Structured output provided successfully
```

## Resultado final

- Turnos: 8
- Duración: 32 s
- Error: False

{"valor":206.25,"unidad":"US$ por persona al mes","fuente":"INEI, ENAHO 2024 (módulo 34 Sumaria, datos/966-Modulo34.zip, sumaria-2024.dta, 33 691 hogares): gasto per cápita mensual = gashog2d/(12×mieperho), promedio ponderado por factor07×mieperho = S/ 774.66. BCRP, serie PN01206PM (tipo de cambio interbancario venta, promedio mensual), promedio simple de los 12 meses de 2024 (2024-01 a 2024-12) = 3.7559 S/ por US$. Resultado: 774.66 / 3.7559 = US$ 206.25."}
