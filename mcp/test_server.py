"""El contrato del servidor: si estas pruebas pasan, Claude Code y evaluar.py pueden usarlo.

    uv run pytest -q

Llaman al servidor en memoria, igual que lo haría Claude Code, y piden datos reales al BCRP.
"""
import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from server import mcp


async def _con_cliente(f):
    async with Client(mcp) as c:
        return await f(c)


def llamar(herramienta, **args):
    return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta, args))).data


def test_buscar_encuentra_el_ipc():
    r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
    assert "PN01273PM" in [x["codigo"] for x in r]
    assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()


def test_cuatro_herramientas_como_minimo():
    nombres = {t.name for t in asyncio.run(_con_cliente(lambda c: c.list_tools()))}
    assert {"buscar_series", "serie", "resumen"} <= nombres
    assert len(nombres) >= 4, "falta su herramienta propia"


def test_serie_mensual():
    r = llamar("serie", codigo="PN01271PM", desde="2025-01", hasta="2025-12")
    assert len(r["datos"]) == 12
    assert r["datos"][0]["periodo"] == "2025-01"
    assert r["datos"][2]["valor"] == pytest.approx(0.81, abs=0.01)   # IPC de Lima, marzo de 2025
    assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


def test_serie_diaria():
    r = llamar("serie", codigo="PD04638PD", desde="2026-10-01", hasta="2026-10-15")
    assert r["datos"][0]["periodo"] == "2026-10-01"
    assert r["datos"][-1] == {"periodo": "2026-10-15", "valor": pytest.approx(3.428, abs=0.001)}


def test_resumen_sin_cuentas_a_mano():
    r = llamar("resumen", codigo="PN01273PM", desde="2025-12", hasta="2026-09")
    assert r["primero"]["valor"] == pytest.approx(1.51, abs=0.01)
    assert r["ultimo"]["valor"] == pytest.approx(4.55, abs=0.01)
    assert r["maximo"]["periodo"] == "2026-09"
    assert {"cambio", "variacion_pct", "promedio", "minimo"} <= r.keys()


def test_codigo_inexistente_da_un_error_claro():
    with pytest.raises(ToolError, match="XX999"):
        llamar("serie", codigo="XX999", desde="2025-01", hasta="2025-02")


def test_un_recurso():
    async def contar(c):
        return len(await c.list_resources()) + len(await c.list_resource_templates())
    assert asyncio.run(_con_cliente(contar)) >= 1


def test_un_prompt():
    assert len(asyncio.run(_con_cliente(lambda c: c.list_prompts()))) >= 1


# --------------------------------------------------------------------------------------------------------------
# Pruebas propias (Tarea 4). Las cifras esperadas se tomaron directamente de la API pública del BCRP con curl,
# no del servidor: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2019-12/2024-12


def test_resumen_anual_inflacion_de_diciembre():
    r = llamar("resumen_anual", codigo="PN01273PM", desde_anio=2020, hasta_anio=2024)
    anios = {a["anio"]: a for a in r["anios"]}
    assert sorted(anios) == [2020, 2021, 2022, 2023, 2024]
    assert anios[2022]["fin_de_periodo"] == {"periodo": "2022-12", "valor": pytest.approx(8.459, abs=0.01)}
    assert anios[2024]["fin_de_periodo"]["valor"] == pytest.approx(1.966, abs=0.01)
    assert all(a["n"] == 12 and a["completo"] for a in r["anios"])
    assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")
    with pytest.raises(ToolError, match="mayor o igual"):
        llamar("resumen_anual", codigo="PN01273PM", desde_anio=2024, hasta_anio=2020)


def test_comparar_series_alinea_y_rechaza_frecuencias_distintas():
    r = llamar("comparar_series", codigo_a="PN01273PM", codigo_b="PN01279PM", desde="2020-01", hasta="2024-12")
    assert r["periodos_comunes"] == 60
    assert -1 <= r["correlacion_niveles"] <= 1
    assert r["correlacion_niveles"] > 0.5            # inflación total y subyacente se mueven juntas
    assert r["maxima_diferencia"]["valor"] >= r["diferencia_promedio"] >= r["minima_diferencia"]["valor"]
    assert "causal" in r["advertencia"]
    with pytest.raises(ToolError, match="Frecuencias incompatibles"):
        llamar("comparar_series", codigo_a="PN01273PM", codigo_b="PM04923AA", desde="2020-01", hasta="2024-12")
