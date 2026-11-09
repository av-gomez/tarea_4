"""Descarga los microdatos oficiales de la ENAHO 2024 (INEI) y el GeoJSON departamental a datos/.

    uv run .claude/skills/limpiando-enaho/scripts/descargar.py
"""
from pathlib import Path

import httpx

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
ARCHIVOS = {
    "966-Modulo34.zip": "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip",
    "966-Modulo02.zip": "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip",
    "peru_departamental_simple.geojson": "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
                                         "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson",
}

if __name__ == "__main__":
    datos = RAIZ / "datos"
    datos.mkdir(exist_ok=True)
    for nombre, url in ARCHIVOS.items():
        destino = datos / nombre
        if destino.exists() and destino.stat().st_size > 0:
            print(f"Ya existe datos/{nombre} ({destino.stat().st_size / 1e6:.1f} MB)")
            continue
        print(f"Descargando {url} ...")
        with httpx.stream("GET", url, timeout=300, follow_redirects=True) as r:
            r.raise_for_status()
            with open(destino, "wb") as f:
                for parte in r.iter_bytes():
                    f.write(parte)
        print(f"  -> datos/{nombre} ({destino.stat().st_size / 1e6:.1f} MB)")
