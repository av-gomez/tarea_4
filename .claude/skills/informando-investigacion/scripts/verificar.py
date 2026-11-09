"""Verificación independiente de las afirmaciones numéricas de un informe.

    uv run .claude/skills/informando-investigacion/scripts/verificar.py informes/afirmaciones.csv

Cada fila de afirmaciones.csv describe una cifra del informe:

    id,afirmacion,fuente,codigo,periodo,agregacion,valor_informe,tolerancia
    f1,"La inflación de 2022 cerró en 8.5 %",bcrp,PN01273PM,2022-12,valor,8.46,0.01
    f2,"Inflación promedio de 2022",bcrp,PN01273PM,2022,promedio,7.88,0.01
    f3,"Pobreza rural",enaho,area,Rural,pobreza_monetaria,39.3,0.05

La verificación NO usa el servidor MCP ni la skill de limpieza, para que sea un control independiente:
  - bcrp: consulta directamente la API pública (https://estadisticas.bcrp.gob.pe/estadisticas/series/api)
    y toma el valor del periodo (agregacion = valor) o el promedio / último dato del año (promedio, fin).
  - enaho: vuelve a leer el .dta original de la sumaria y calcula con pandas puro
    sum(factor07*mieperho*pobre)/sum(factor07*mieperho) para nacional, area, departamento (código), dominio
    o region. En agregacion se indica pobreza_monetaria o pobreza_extrema.
Escribe informes/verificacion.md (tabla APA 7) e informes/verificacion.csv. Sale con código 1 si alguna
afirmación no coincide, para que el agente la corrija o la reporte como limitación.
"""
from __future__ import annotations

import io
import sys
import time
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAIZ = next(d for d in Path(__file__).resolve().parents if (d / "pyproject.toml").exists())
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9,
         "Oct": 10, "Nov": 11, "Dic": 12}


def _bcrp(codigo: str, desde: str, hasta: str) -> pd.DataFrame:
    url = f"{API}/{codigo}/json/{desde}/{hasta}"
    for i in range(5):
        r = httpx.get(url, timeout=60, headers={"User-Agent": "verificacion-tarea4/1.0"})
        if r.text.strip().startswith("{"):
            filas = []
            for p in r.json()["periods"]:
                try:
                    filas.append({"nombre": p["name"], "valor": float(p["values"][0])})
                except (ValueError, TypeError):
                    pass
            return pd.DataFrame(filas), url
        time.sleep(3 + 3 * i)
    raise RuntimeError(f"La API del BCRP no respondió con datos: {url}")


def valor_bcrp(codigo: str, periodo: str, agregacion: str):
    periodo = str(periodo)
    if len(periodo) == 4:                                   # año completo
        if codigo.endswith("A"):                            # serie anual
            df, url = _bcrp(codigo, periodo, periodo)
            return df.valor.iloc[0], url
        if codigo.endswith("Q"):
            df, url = _bcrp(codigo, f"{periodo}-1", f"{periodo}-4")
        else:
            df, url = _bcrp(codigo, f"{periodo}-1", f"{periodo}-12")
        return (df.valor.mean() if agregacion == "promedio" else df.valor.iloc[-1]), url
    anio, mes = periodo.split("-")[:2]
    if len(periodo) == 10:                                  # diaria
        df, url = _bcrp(codigo, periodo, periodo)
    else:
        df, url = _bcrp(codigo, f"{anio}-{int(mes)}", f"{anio}-{int(mes)}")
    return df.valor.iloc[0], url


_SUMARIA = None


def sumaria() -> pd.DataFrame:
    global _SUMARIA
    if _SUMARIA is None:
        with zipfile.ZipFile(RAIZ / "datos" / "966-Modulo34.zip") as z:
            s = pd.read_stata(io.BytesIO(z.read("966-Modulo34/sumaria-2024.dta")), convert_categoricals=False)
        s["w"] = s.factor07 * s.mieperho
        s["dep"] = s.ubigeo.astype(str).str[:2]
        s["area"] = s.estrato.map(lambda e: "Urbana" if e <= 5 else "Rural")
        s["region"] = s.dominio.map({1: "Costa", 2: "Costa", 3: "Costa", 8: "Costa", 4: "Sierra", 5: "Sierra",
                                     6: "Sierra", 7: "Selva"})
        s["dominio_nombre"] = s.dominio.map({1: "Costa Norte", 2: "Costa Centro", 3: "Costa Sur",
                                             4: "Sierra Norte", 5: "Sierra Centro", 6: "Sierra Sur", 7: "Selva",
                                             8: "Lima Metropolitana"})
        _SUMARIA = s
    return _SUMARIA


def valor_enaho(desagregacion: str, categoria: str, indicador: str):
    s = sumaria()
    y = (s.pobreza <= 2) if indicador == "pobreza_monetaria" else (s.pobreza == 1)
    col = {"area": "area", "departamento": "dep", "region": "region", "region_natural": "region",
           "dominio": "dominio_nombre", "dominio_nombre": "dominio_nombre"}.get(desagregacion)
    m = pd.Series(True, index=s.index) if desagregacion == "nacional" else (
        s[col].astype(str) == (str(categoria).zfill(2) if col == "dep" else str(categoria)))
    if not m.any():
        raise ValueError(f"Categoría no encontrada: {desagregacion}={categoria}")
    return 100 * (s.w[m] * y[m]).sum() / s.w[m].sum(), "datos/966-Modulo34.zip: sumaria-2024.dta"


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ruta = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "informes" / "afirmaciones.csv")
    af = pd.read_csv(ruta, dtype=str)
    filas = []
    for r in af.itertuples():
        try:
            if r.fuente.strip().lower() == "bcrp":
                v, src = valor_bcrp(r.codigo.strip(), r.periodo.strip(), (r.agregacion or "valor").strip())
            else:
                v, src = valor_enaho(r.codigo.strip(), r.periodo.strip(), (r.agregacion or "").strip())
            v = float(v)
            dif = float(r.valor_informe) - v
            ok = abs(dif) <= float(r.tolerancia)
            filas.append({"id": r.id, "afirmacion": r.afirmacion, "valor_informe": float(r.valor_informe),
                          "valor_verificado": round(v, 4), "diferencia": round(dif, 4),
                          "tolerancia": float(r.tolerancia), "coincide": "Sí" if ok else "No",
                          "procedimiento": src})
        except Exception as e:  # se reporta, no se inventa
            filas.append({"id": r.id, "afirmacion": r.afirmacion, "valor_informe": r.valor_informe,
                          "valor_verificado": None, "diferencia": None, "tolerancia": r.tolerancia,
                          "coincide": "Error", "procedimiento": f"Error: {e}"})
    res = pd.DataFrame(filas)
    res.to_csv(ruta.parent / "verificacion.csv", index=False, encoding="utf-8")
    n_ok = (res.coincide == "Sí").sum()
    md = ["# Verificación independiente de cifras del informe", "",
          f"Generado con `.claude/skills/informando-investigacion/scripts/verificar.py` a partir de `{ruta.name}`. "
          "Las cifras del BCRP se consultaron directamente en la API pública (sin el servidor MCP) y las de la "
          "ENAHO se recalcularon desde el archivo .dta original de la sumaria con pandas, sin la skill de "
          "limpieza.", "", "**Tabla 1**", "", "*Comparación entre las cifras del informe y su verificación "
          "independiente*", "",
          "| Id | Afirmación | Informe | Verificado | Diferencia | Tolerancia | Coincide | Procedimiento |",
          "|:---|:---|---:|---:|---:|---:|:---:|:---|"]
    for f in filas:
        md.append(f"| {f['id']} | {f['afirmacion']} | {f['valor_informe']} | {f['valor_verificado']} | "
                  f"{f['diferencia']} | {f['tolerancia']} | {f['coincide']} | {f['procedimiento']} |")
    md += ["", f"*Nota.* {n_ok} de {len(res)} afirmaciones coinciden dentro de la tolerancia definida antes de "
           "verificar. Diferencia = valor del informe menos valor verificado.", ""]
    (ruta.parent / "verificacion.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    sys.exit(0 if n_ok == len(res) else 1)


if __name__ == "__main__":
    main()
