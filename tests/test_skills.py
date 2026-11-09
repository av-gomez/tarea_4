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


OFICIALES = {2019: 20.2, 2020: 30.1, 2021: 25.9, 2022: 27.5, 2023: 29.0, 2024: 27.6, 2025: 25.7}


@pytest.mark.skipif(not (RAIZ / "salidas" / "serie_indicadores.csv").exists(), reason="falta la serie 2019-2025")
def test_serie_multianual_reproduce_al_inei():
    s = pd.read_csv(RAIZ / "salidas" / "serie_indicadores.csv", dtype={"codigo": str})
    nac = s[(s.indicador == "pobreza_monetaria") & (s.desagregacion == "nacional")].set_index("anio").valor_pct
    for anio, oficial in OFICIALES.items():
        if anio in nac.index:
            assert nac[anio] == pytest.approx(oficial, abs=0.1), anio
    dep = s[(s.indicador == "pobreza_monetaria") & (s.desagregacion == "departamento")]
    assert (dep.groupby("anio").codigo.nunique() == 25).all()


@pytest.mark.skipif(not (RAIZ / "datos" / "966-Modulo01.zip").exists() and
                    not (RAIZ / "datos" / "1031-Modulo01.zip").exists(), reason="falta un módulo 01")
def test_unir_otro_modulo_sin_duplicar():
    sys.path.insert(0, str(RAIZ))
    from comun import enaho
    anio = 2025 if (RAIZ / "datos" / "1031-Modulo01.zip").exists() else 2024
    mod, nivel, _ = enaho.leer(anio, "01", columnas=["p110"])
    assert nivel == "hogar"
    base = pd.read_parquet(RAIZ / "salidas" / f"personas_{anio}.parquet", columns=enaho.LLAVES_PERSONA)
    unida = enaho.unir(base, mod.drop(columns="anio"), nivel)
    assert len(unida) == len(base) and unida.p110.notna().mean() > 0.95
    with pytest.raises(ValueError, match="agrégalo"):
        enaho.unir(base, mod.drop(columns="anio"), "detalle")
