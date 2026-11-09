"""Servidor MCP del BCRP para el agente de investigación socioeconómica.

    uv run pytest mcp -q                                        # 8 pruebas originales + pruebas propias
    uv run mcp/server.py                                        # el servidor, por stdio
    claude mcp add --scope project bcrp -- uv run mcp/server.py # conectarlo a Claude Code (ya está en .mcp.json)

Herramientas (todas de solo lectura sobre la API pública del BCRP, sin clave):
    buscar_series      palabras clave -> códigos oficiales del catálogo (17 mil series)
    serie              datos de una serie entre dos periodos, con la URL de la fuente
    resumen            primero, último, cambio, variación, promedio, máximo y mínimo
    resumen_anual      (propia) agrega una serie mensual o trimestral por año: promedio, fin de periodo, etc.
    comparar_series    (propia) alinea dos series por periodo y calcula correlación y diferencias
    graficar_serie     (propia) figura APA 7 (Times New Roman) de una o más series, guardada en figuras/

Recursos: bcrp://serie/{codigo} (ficha descriptiva) y bcrp://series-clave (series de uso frecuente).
Prompts: informe(tema) e interpretar_indicador(codigo, desde, hasta).

Las cuentas las hace Python, no el modelo: cada cifra sale de una llamada que se puede repetir.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from functools import cache
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))
CATALOGO = RAIZ / "datos" / "catalogo_bcrp.csv"
CACHE = RAIZ / "datos" / "cache_bcrp"
FIGURAS = RAIZ / "figuras"
URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "sep": 9,
         "oct": 10, "nov": 11, "dic": 12}
SERIES_CLAVE = {
    "PN01273PM": "Inflación de Lima Metropolitana, variación % en 12 meses",
    "PN01271PM": "IPC de Lima Metropolitana, variación % mensual",
    "PN01279PM": "IPC subyacente, variación % en 12 meses",
    "PN01277PM": "IPC sin alimentos y energía, variación % en 12 meses",
    "PM04923AA": "PBI real, variación % anual",
    "PN01728AM": "PBI mensual, variación % interanual",
    "PD04722MM": "Tasa de referencia de la política monetaria (%)",
    "PN01206PM": "Tipo de cambio interbancario venta, promedio mensual (S/ por US$)",
    "PD04638PD": "Tipo de cambio interbancario venta, diario (S/ por US$)",
    "PN00027MM": "Reservas internacionales netas (millones de US$)",
}

mcp = FastMCP("bcrp", instructions=(
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series "
    "(o lee el recurso bcrp://series-clave); luego usa resumen para variaciones, promedios y extremos, "
    "resumen_anual para cifras por año, comparar_series para relacionar dos indicadores, serie para los datos y "
    "graficar_serie para una figura APA. No calcules a mano: cita siempre el código de la serie, el periodo y la "
    "URL de la fuente. Si una herramienta falla o no hay datos, dilo; no inventes cifras."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


# Sinónimos: cada palabra de la consulta se acepta si aparece ella o alguna equivalente en el catálogo.
SINONIMOS = {
    "pbi": ["pbi", "producto bruto interno"], "var%": ["var%", "variacion", "variaciones"],
    "variacion": ["variacion", "variaciones", "var%"], "inflacion": ["inflacion", "var% 12 meses"],
    "anual": ["anual", "12 meses"], "dolar": ["dolar", "us$"], "tc": ["tipo de cambio"],
    "crecimiento": ["variacion", "variaciones", "var%"], "real": ["real", "reales"],
}


@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(parents=True, exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre + " " + df.frecuencia).map(_sin_tildes)
    return df


def _ficha(codigo):
    codigo = str(codigo).strip().upper()
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas internacionales netas",
    "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual", "Trimestral" o "Anual".
    Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras.
    """
    df = catalogo()
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        alternativas = SINONIMOS.get(palabra, [palabra])
        m &= df.texto.str.contains("|".join(re.escape(a) for a in alternativas))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


# ----------------------------------------------------------------------------------------------- fechas
def _tipo(frecuencia: str) -> str:
    f = _sin_tildes(frecuencia)
    for clave in ("diaria", "mensual", "trimestral", "anual"):
        if clave in f:
            return clave
    raise ToolError(f"Frecuencia no soportada: {frecuencia!r}")


def _fecha_api(texto: str, tipo: str) -> str:
    """'2025-01' -> '2025-1' (mensual); '2025-T1' -> '2025-1'; '2025-01-15' (diaria); '2025' (anual)."""
    t = str(texto).strip()
    if tipo == "diaria":
        return pd.Timestamp(t).strftime("%Y-%m-%d")
    if tipo == "anual":
        return t[:4]
    m = re.match(r"^(\d{4})(?:[-./]?(?:T|Q)?(\d{1,2}))?", t, re.I)
    if not m:
        raise ToolError(f"Fecha no válida: {texto!r}. Usen 2025-01, 2025-T1, 2025-01-15 o 2025.")
    anio, sub = m.group(1), m.group(2)
    if sub is None:
        sub = "1"
    return f"{anio}-{int(sub)}"


def _periodo(nombre: str, tipo: str) -> str:
    """Nombres de la API -> 'AAAA-MM', 'AAAA-MM-DD', 'AAAA-Tn' o 'AAAA'."""
    n = nombre.strip()
    if tipo == "mensual":
        mes, anio = n.split(".")
        return f"{int(anio):04d}-{MESES[_sin_tildes(mes)[:3]]:02d}"
    if tipo == "diaria":
        dia, mes, anio = n.split(".")
        anio = int(anio)
        anio = anio + 2000 if anio < 100 else anio
        return f"{anio:04d}-{MESES[_sin_tildes(mes)[:3]]:02d}-{int(dia):02d}"
    if tipo == "trimestral":
        tri, anio = n.upper().split(".")
        anio = int(anio)
        anio = anio + 2000 if anio < 100 else anio
        return f"{anio:04d}-T{int(tri.lstrip('T'))}"
    return n[:4]


def _descargar(url: str) -> dict:
    """GET con reintentos (la API devuelve HTML si recibe muchos pedidos) y caché en disco de 12 horas."""
    CACHE.mkdir(parents=True, exist_ok=True)
    archivo = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if archivo.exists() and time.time() - archivo.stat().st_mtime < 12 * 3600:
        return json.loads(archivo.read_text(encoding="utf-8"))
    ultimo = ""
    for intento in range(5):
        try:
            r = httpx.get(url, timeout=60, headers={"User-Agent": "agente-socioeconomico-peru/1.0"})
            texto = r.content.decode("utf-8", errors="replace").strip()
            if texto.startswith("{"):
                datos = json.loads(texto)
                archivo.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
                return datos
            ultimo = "la API respondió HTML en vez de JSON"
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            ultimo = str(e)
        time.sleep(2 + 3 * intento)
    raise ToolError(f"El BCRP no respondió con datos para {url} ({ultimo}). Reintenten en unos segundos.")


def _datos(codigo: str, desde: str, hasta: str) -> tuple[dict, list[dict], str]:
    ficha = _ficha(codigo)
    tipo = _tipo(ficha["frecuencia"])
    url = f"{API}/{ficha['codigo']}/json/{_fecha_api(desde, tipo)}/{_fecha_api(hasta, tipo)}"
    js = _descargar(url)
    datos = []
    for p in js.get("periods", []):
        v = (p.get("values") or [None])[0]
        try:
            valor = float(v)
        except (TypeError, ValueError):
            continue                                  # "n.d." y vacíos se saltan
        if np.isfinite(valor):
            datos.append({"periodo": _periodo(p["name"], tipo), "valor": valor})
    if not datos:
        raise ToolError(f"La serie {ficha['codigo']} no tiene datos entre {desde} y {hasta}. Revisen el periodo "
                        f"(la serie empieza en {ficha['inicio']} y se actualizó el {ficha['actualizada']}).")
    return ficha, datos, url


def _fuente_web(codigo: str) -> str:
    return f"{WEB}/{'diarias' if codigo.endswith('D') else 'mensuales' if codigo.endswith('M') else 'trimestrales' if codigo.endswith('Q') else 'anuales'}/resultados/{codigo}/html"


@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str) -> dict:
    """Descarga los datos oficiales de una serie del BCRP entre dos periodos (inclusive).

    Formatos de periodo: mensual "2025-01", trimestral "2025-T1", diaria "2025-10-15", anual "2025".
    Devuelve código, nombre, frecuencia, la lista {"periodo", "valor"} y la URL de la fuente.
    Ejemplo: serie("PN01273PM", "2020-01", "2024-12") -> inflación a 12 meses de Lima, mensual.
    """
    ficha, datos, url = _datos(codigo, desde, hasta)
    return {"codigo": ficha["codigo"], "nombre": ficha["nombre"], "frecuencia": ficha["frecuencia"],
            "n": len(datos), "datos": datos, "fuente": url}


def _extremo(df, idx):
    return {"periodo": df.periodo.iloc[idx], "valor": round(float(df.valor.iloc[idx]), 6)}


@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str) -> dict:
    """Resume una serie del BCRP en un periodo: primero, último, cambio absoluto, variación %, promedio,
    desviación estándar, máximo y mínimo (con su periodo). Úsenla en lugar de hacer cuentas a mano.

    Ejemplo: resumen("PN01273PM", "2025-12", "2026-09").
    """
    ficha, datos, url = _datos(codigo, desde, hasta)
    df = pd.DataFrame(datos)
    primero, ultimo = df.valor.iloc[0], df.valor.iloc[-1]
    return {"codigo": ficha["codigo"], "nombre": ficha["nombre"], "frecuencia": ficha["frecuencia"],
            "n": len(df), "primero": _extremo(df, 0), "ultimo": _extremo(df, -1),
            "cambio": round(float(ultimo - primero), 6),
            "variacion_pct": round(float(100 * (ultimo / primero - 1)), 6) if primero else None,
            "promedio": round(float(df.valor.mean()), 6), "desviacion_estandar": round(float(df.valor.std()), 6),
            "maximo": _extremo(df, int(df.valor.values.argmax())),
            "minimo": _extremo(df, int(df.valor.values.argmin())), "fuente": url}


# ----------------------------------------------------------------------------------- herramientas propias
@mcp.tool(annotations=SOLO_LECTURA)
def resumen_anual(codigo: str, desde_anio: int, hasta_anio: int) -> dict:
    """Agrega una serie mensual, trimestral o diaria del BCRP por año calendario.

    Úsenla para preguntas del tipo "¿cómo evolucionó la inflación entre 2020 y 2024?" o "¿cuál fue el tipo de
    cambio promedio de 2023?". Para cada año devuelve: promedio, valor de fin de periodo (diciembre/T4/último
    día), máximo, mínimo y número de observaciones; además, si el año está incompleto, lo marca.
    Para inflación a 12 meses (PN01273PM) el valor de diciembre es la inflación anual oficial del año.
    Ejemplo: resumen_anual("PN01273PM", 2019, 2024).
    """
    if hasta_anio < desde_anio:
        raise ToolError("hasta_anio debe ser mayor o igual que desde_anio.")
    ficha = _ficha(codigo)
    tipo = _tipo(ficha["frecuencia"])
    desde = {"mensual": f"{desde_anio}-01", "trimestral": f"{desde_anio}-T1", "diaria": f"{desde_anio}-01-01"}.get(
        tipo, str(desde_anio))
    hasta = {"mensual": f"{hasta_anio}-12", "trimestral": f"{hasta_anio}-T4", "diaria": f"{hasta_anio}-12-31"}.get(
        tipo, str(hasta_anio))
    ficha, datos, url = _datos(codigo, desde, hasta)
    df = pd.DataFrame(datos)
    df["anio"] = df.periodo.str[:4].astype(int)
    completo = {"mensual": 12, "trimestral": 4}.get(tipo)
    anios = []
    for anio, g in df.groupby("anio"):
        anios.append({"anio": int(anio), "promedio": round(float(g.valor.mean()), 6),
                      "fin_de_periodo": {"periodo": g.periodo.iloc[-1], "valor": round(float(g.valor.iloc[-1]), 6)},
                      "maximo": _extremo(g.reset_index(drop=True), int(g.valor.values.argmax())),
                      "minimo": _extremo(g.reset_index(drop=True), int(g.valor.values.argmin())),
                      "n": int(len(g)), "completo": (len(g) == completo) if completo else True})
    return {"codigo": ficha["codigo"], "nombre": ficha["nombre"], "frecuencia": ficha["frecuencia"],
            "anios": anios, "fuente": url,
            "nota": "Promedio = media aritmética de las observaciones del año; fin de periodo = última observación."}


@mcp.tool(annotations=SOLO_LECTURA)
def comparar_series(codigo_a: str, codigo_b: str, desde: str, hasta: str) -> dict:
    """Compara dos series del BCRP de la misma frecuencia en periodos comunes.

    Alinea por periodo (descarta los periodos sin dato en alguna de las dos), y devuelve: número de periodos
    comunes, correlación de Pearson de los niveles y de las primeras diferencias, promedio de cada serie, la
    diferencia promedio (a - b), y el periodo de mayor y menor diferencia. Es una asociación descriptiva:
    NO implica causalidad. Si las frecuencias no coinciden, devuelve un error explicando la incompatibilidad.
    Ejemplo: comparar_series("PN01273PM", "PN01279PM", "2020-01", "2024-12") (inflación total vs subyacente).
    """
    fa, fb = _ficha(codigo_a), _ficha(codigo_b)
    if _tipo(fa["frecuencia"]) != _tipo(fb["frecuencia"]):
        raise ToolError(f"Frecuencias incompatibles: {fa['codigo']} es {fa['frecuencia']} y {fb['codigo']} es "
                        f"{fb['frecuencia']}. Agreguen la de mayor frecuencia con resumen_anual antes de comparar.")
    _, da, ua = _datos(fa["codigo"], desde, hasta)
    _, db, ub = _datos(fb["codigo"], desde, hasta)
    a = pd.DataFrame(da).set_index("periodo").valor.rename("a")
    b = pd.DataFrame(db).set_index("periodo").valor.rename("b")
    df = pd.concat([a, b], axis=1, join="inner").dropna().sort_index()
    if len(df) < 3:
        raise ToolError(f"Solo hay {len(df)} periodos comunes entre {fa['codigo']} y {fb['codigo']}; "
                        "se necesitan al menos 3 para comparar.")
    dif = df.a - df.b
    d1 = df.diff().dropna()
    return {"serie_a": {"codigo": fa["codigo"], "nombre": fa["nombre"], "promedio": round(float(df.a.mean()), 6)},
            "serie_b": {"codigo": fb["codigo"], "nombre": fb["nombre"], "promedio": round(float(df.b.mean()), 6)},
            "periodos_comunes": int(len(df)), "desde": df.index[0], "hasta": df.index[-1],
            "descartados": int(len(a) + len(b) - 2 * len(df)),
            "correlacion_niveles": round(float(df.a.corr(df.b)), 4),
            "correlacion_diferencias": round(float(d1.a.corr(d1.b)), 4) if len(d1) >= 3 else None,
            "diferencia_promedio": round(float(dif.mean()), 6),
            "maxima_diferencia": {"periodo": dif.idxmax(), "valor": round(float(dif.max()), 6)},
            "minima_diferencia": {"periodo": dif.idxmin(), "valor": round(float(dif.min()), 6)},
            "fuentes": [ua, ub], "advertencia": "Correlación descriptiva; no demuestra una relación causal."}


@mcp.tool(annotations={"readOnlyHint": False, "openWorldHint": True})
def graficar_serie(codigos: list[str], desde: str, hasta: str, titulo: str, numero_figura: int = 1,
                   archivo: str | None = None, linea_referencia: float | None = None,
                   etiqueta_referencia: str | None = None) -> dict:
    """Genera una figura de líneas en formato APA 7 (Times New Roman, número en negrita, título en cursiva y
    nota con la fuente) con una o varias series del BCRP de la misma frecuencia, y la guarda en figuras/.

    titulo: título analítico en cursiva (p. ej. "Inflación anual de Lima Metropolitana, 2019-2024").
    linea_referencia: valor horizontal opcional (p. ej. 3.0 para el techo del rango meta de inflación) con su
    etiqueta_referencia. Devuelve la ruta del PNG, los códigos, el periodo y la fuente.
    Ejemplo: graficar_serie(["PN01273PM", "PN01279PM"], "2019-01", "2024-12", "Inflación total y subyacente").
    """
    from comun import apa
    import matplotlib.pyplot as plt

    if not codigos:
        raise ToolError("Indiquen al menos un código de serie.")
    apa.aplicar_estilo()
    fig, ax = plt.subplots(figsize=(8, 5.2))
    fuentes, nombres, tablas = [], [], []
    estilos = ["-", "--", ":", "-."]
    tipos = set()
    for i, c in enumerate(codigos[:4]):
        ficha, datos, url = _datos(c, desde, hasta)
        tipos.add(_tipo(ficha["frecuencia"]))
        df = pd.DataFrame(datos)
        x = _a_fecha(df.periodo, _tipo(ficha["frecuencia"]))
        etiqueta = SERIES_CLAVE.get(ficha["codigo"], ficha["nombre"])
        ax.plot(x, df.valor, linestyle=estilos[i], color=apa.PALETA[i], linewidth=1.6,
                label=f"{etiqueta} ({ficha['codigo']})")
        fuentes.append(url)
        nombres.append(ficha["codigo"])
        tablas.append(df.assign(codigo=ficha["codigo"], nombre=ficha["nombre"], fuente=url))
    if len(tipos) > 1:
        plt.close(fig)
        raise ToolError("Las series tienen frecuencias distintas; grafíquenlas por separado.")
    if linea_referencia is not None:
        ax.axhline(linea_referencia, color=apa.GRIS, linewidth=0.9, linestyle=(0, (4, 3)))
        if etiqueta_referencia:
            ax.text(ax.get_xlim()[0], linea_referencia, f" {etiqueta_referencia}", va="bottom", fontsize=9,
                    color=apa.GRIS)
    ax.axhline(0, color="#404040", linewidth=0.6)
    ax.set_ylabel(_unidad(nombres[0]))
    ax.legend(loc="upper left", fontsize=9)
    apa.encabezar(fig, numero_figura, titulo,
                  f"Elaboración propia con datos del BCRP ({', '.join(nombres)}), periodo {desde} a {hasta}. "
                  f"Fuente: {apa.FUENTE_BCRP}.", abajo=0.17)
    nombre = archivo or f"bcrp_{'_'.join(nombres)}_{desde}_{hasta}.png"
    ruta = apa.guardar(fig, FIGURAS / Path(nombre).name)
    csv = RAIZ / "tablas" / (Path(nombre).stem + ".csv")
    csv.parent.mkdir(exist_ok=True)
    pd.concat(tablas)[["codigo", "periodo", "valor", "nombre", "fuente"]].to_csv(csv, index=False, encoding="utf-8")
    return {"archivo": str(ruta.relative_to(RAIZ)).replace("\\", "/"),
            "datos": str(csv.relative_to(RAIZ)).replace("\\", "/"), "codigos": nombres, "desde": desde,
            "hasta": hasta, "fuentes": fuentes}


def _a_fecha(periodos: pd.Series, tipo: str) -> pd.Series:
    if tipo == "mensual":
        return pd.to_datetime(periodos + "-01")
    if tipo == "trimestral":
        return pd.PeriodIndex(periodos.str.replace("-T", "Q"), freq="Q").to_timestamp()
    if tipo == "anual":
        return pd.to_datetime(periodos + "-01-01")
    return pd.to_datetime(periodos)


def _unidad(codigo: str) -> str:
    n = _sin_tildes(_ficha(codigo)["nombre"])
    if "var%" in n or "variacion" in n or "tasa" in n or "%" in n:
        return "Porcentaje (%)"
    if "s/ por us$" in n or "tipo de cambio" in n:
        return "Soles por dólar"
    if "millones" in n:
        return "Millones"
    if "indice" in n:
        m = re.search(r"indice ([^)]*=\s*100)", n)
        return f"Índice ({m.group(1)})" if m else "Índice"
    return "Valor"


# -------------------------------------------------------------------------------------- recursos y prompts
@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json")
def ficha_serie(codigo: str) -> dict:
    """Ficha descriptiva de una serie del BCRP: nombre, categoría, frecuencia, inicio, última actualización,
    URL de la API y página web oficial para verificar las cifras a mano."""
    f = _ficha(codigo)
    return {**f, "api": f"{API}/{f['codigo']}/json", "web": _fuente_web(f["codigo"]),
            "como_citar": f"Banco Central de Reserva del Perú. ({datetime.now().year}). {f['nombre']} "
                          f"[Serie {f['codigo']}]. BCRPData. {_fuente_web(f['codigo'])}"}


@mcp.resource("bcrp://series-clave", mime_type="application/json")
def series_clave() -> dict:
    """Series del BCRP de uso frecuente en investigación socioeconómica (inflación, PBI, tipo de cambio, tasa de
    referencia, reservas), con su código oficial."""
    return {"series": [{"codigo": c, "descripcion": d} for c, d in SERIES_CLAVE.items()],
            "nota": "Verifiquen siempre el código con buscar_series o el recurso bcrp://serie/{codigo}."}


@mcp.prompt
def informe(tema: str) -> str:
    """Pide un informe breve y verificable sobre un tema macroeconómico con datos del BCRP."""
    return (f"Elabora un informe breve, en estilo académico (APA 7), sobre «{tema}» en el Perú con datos oficiales "
            "del BCRP.\n1. Busca las series pertinentes con buscar_series (o lee bcrp://series-clave).\n"
            "2. Obtén las cifras con resumen, resumen_anual o comparar_series; no calcules a mano.\n"
            "3. Genera una figura con graficar_serie.\n"
            "4. Para cada cifra cita el código de la serie, el periodo y la URL de la fuente.\n"
            "5. Distingue asociación de causalidad y señala limitaciones (frecuencia, revisiones, cobertura: el IPC "
            "es de Lima Metropolitana).\n6. Si una herramienta falla o no hay datos, dilo explícitamente.")


@mcp.prompt
def interpretar_indicador(codigo: str, desde: str, hasta: str) -> str:
    """Pide interpretar un indicador del BCRP en un periodo, con sus cifras calculadas por las herramientas."""
    return (f"Interpreta la serie {codigo} del BCRP entre {desde} y {hasta}.\n"
            f"Lee primero el recurso bcrp://serie/{codigo} para conocer su definición y unidad. Luego llama a "
            f"resumen('{codigo}', '{desde}', '{hasta}') y, si la serie es mensual, a resumen_anual. Explica en "
            "tres a cinco oraciones: nivel inicial y final, cambio, extremos y su contexto. Cita código, periodo "
            "y fuente para cada cifra y no hagas cuentas a mano.")


if __name__ == "__main__":
    mcp.run()
