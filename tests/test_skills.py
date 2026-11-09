"""Pruebas de las Skills de ENAHO (requieren los microdatos en datos/; se omiten si faltan).

    uv run pytest tests -q
"""
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
SKILLS = RAIZ / ".claude" / "skills"
pytestmark = pytest.mark.skipif(not (RAIZ / "datos" / "966-Modulo34.zip").exists(),
                                reason="faltan los microdatos de la ENAHO en datos/")


def correr(script, *args):
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=RAIZ)


@pytest.fixture(scope="module")
def base():
    r = correr(SKILLS / "limpiando-enaho" / "scripts" / "limpiar.py")
    assert r.returncode == 0, r.stderr
    return pd.read_parquet(RAIZ / "salidas" / "personas_2024.parquet")


def test_validacion_aprobada(base):
    txt = (RAIZ / "salidas" / "validacion.txt").read_text(encoding="utf-8")
    assert "TODAS LAS VALIDACIONES ESENCIALES APROBADAS" in txt
    assert "FALLIDA" not in txt
    assert len(base) == 108_664
    assert base.conglome.str.len().eq(6).all()          # llaves sin perder ceros


def test_indicadores_ponderados(base):
    ind = pd.read_csv(RAIZ / "salidas" / "indicadores.csv", dtype={"codigo": str})
    pm = ind[ind.indicador == "pobreza_monetaria"]
    assert pm[pm.desagregacion == "nacional"].valor_pct.iloc[0] == pytest.approx(27.6, abs=0.1)
    area = pm[pm.desagregacion == "area"].set_index("categoria").valor_pct
    assert area["Urbana"] == pytest.approx(24.8, abs=0.1) and area["Rural"] == pytest.approx(39.3, abs=0.1)
    dep = pm[pm.desagregacion == "departamento"]
    assert len(dep) == 25 and {"07", "15"} <= set(dep.codigo)
    assert 100 * base.pobre.mean() != pytest.approx(27.6, abs=0.5)   # el promedio simple no sirve


def test_mapa_une_25_departamentos_por_codigo(base):
    r = correr(SKILLS / "mapeando-enaho" / "scripts" / "mapear.py", "--archivo", "prueba_mapa.png")
    assert r.returncode == 0, r.stderr
    txt = (RAIZ / "salidas" / "validacion_mapa.txt").read_text(encoding="utf-8")
    assert "unidades unidas: 25/25" in txt and "APROBADA" in txt
    (RAIZ / "mapas" / "prueba_mapa.png").unlink()
