"""Experimento: las mismas 10 preguntas a Claude Code sin y con el MCP del BCRP y las Skills de ENAHO.

    uv run evaluacion/evaluar.py                       # ambos modos, modelo sonnet, 4 en paralelo
    uv run evaluacion/evaluar.py --modos A --paralelo 2

Modo A (sin MCP ni Skills): `claude -p` sin herramientas (--tools ""), sin servidores MCP
    (--strict-mcp-config), con skills y comandos desactivados (--disable-slash-commands) y ejecutado en un
    directorio temporal vacío, de modo que no puede leer CLAUDE.md, las skills ni archivos con resultados.
Modo B (con MCP y Skills): `claude -p` en la raíz del proyecto, con el servidor MCP `bcrp` de .mcp.json
    (--strict-mcp-config excluye cualquier otro MCP), las skills del proyecto y las herramientas Skill, Bash
    (solo `uv run`), Read, Glob y Grep para ejecutar los scripts de las skills.
Ambos modos: mismo modelo, misma instrucción, sesiones independientes (--no-session-persistence) y salida
JSON validada con un esquema. Cada llamada se registra completa en evidencias_ia/evaluacion/.
Califica con la tolerancia fijada en preguntas.csv antes de correr (no se cambia después).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
EVID = RAIZ / "evidencias_ia" / "evaluacion"
ESQUEMA = {"type": "object", "required": ["valor", "fuente"],
           "properties": {"valor": {"type": ["number", "null"]}, "unidad": {"type": "string"},
                          "fuente": {"type": "string"}}}
INSTRUCCION = ("Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo "
               "con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra (fuente oficial, "
               "código de serie o archivo y procedimiento).\n\n")
HERRAMIENTAS_B = ("mcp__bcrp__buscar_series,mcp__bcrp__serie,mcp__bcrp__resumen,mcp__bcrp__resumen_anual,"
                  "mcp__bcrp__comparar_series,mcp__bcrp__graficar_serie,Skill,Bash(uv run:*),Read,Glob,Grep")
MODOS = {
    "A": ["--tools", "", "--strict-mcp-config", "--disable-slash-commands"],
    "B": ["--tools", "Skill,Bash,Read,Glob,Grep", "--strict-mcp-config", "--mcp-config",
          str(RAIZ / ".mcp.json"), "--allowedTools", HERRAMIENTAS_B],
}


def preguntar(qid: str, pregunta: str, modo: str, modelo: str) -> dict:
    cmd = ["claude", "-p", INSTRUCCION + pregunta, "--output-format", "stream-json", "--verbose",
           "--json-schema", json.dumps(ESQUEMA), "--no-session-persistence", "--model", modelo, *MODOS[modo]]
    cwd = RAIZ if modo == "B" else Path(tempfile.mkdtemp(prefix="eval_modoA_"))
    t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900, cwd=cwd)
        salida, error = proc.stdout, proc.stderr.strip()[-300:]
    except subprocess.TimeoutExpired as e:
        salida, error = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (
            e.stdout or ""), "timeout 900 s"
    segundos = round(time.time() - t, 1)
    (EVID / f"{qid}_modo{modo}.jsonl").write_text(salida, encoding="utf-8")
    herramientas, final = [], {}
    for linea in salida.splitlines():
        try:
            ev = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "tool_use":
                    nombre = b["name"]
                    if nombre == "Skill":
                        nombre = f"Skill:{b.get('input', {}).get('skill', '')}"
                    elif nombre == "Bash":
                        nombre = "Bash:" + " ".join(str(b.get("input", {}).get("command", "")).split()[:3])
                    herramientas.append(nombre)
        if ev.get("type") == "result":
            final = ev
    r = final.get("structured_output") or {}
    return {"valor": r.get("valor"), "unidad": r.get("unidad", ""),
            "fuente": r.get("fuente", final.get("result", ""))[:400], "herramientas": ";".join(herramientas),
            "segundos": segundos, "turnos": final.get("num_turns"),
            "error": error if not final or final.get("is_error") else ""}


def calificar(valor, verdad, tolerancia, tipo, fuente) -> str:
    if valor is None:
        return "no responde"
    ok = abs(float(valor) - verdad) <= tolerancia
    if tipo == "mixta":                         # exactitud + coherencia: debe citar ambas fuentes
        f = str(fuente).lower()
        coherente = ("bcrp" in f or "pn0" in f) and ("enaho" in f or "inei" in f)
        return "correcta" if ok and coherente else ("incorrecta" if not ok else "correcta sin citar ambas fuentes")
    return "correcta" if ok else "incorrecta"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modos", nargs="+", default=["A", "B"], choices=list(MODOS))
    p.add_argument("--modelo", default="sonnet")
    p.add_argument("--paralelo", type=int, default=4)
    a = p.parse_args()
    EVID.mkdir(parents=True, exist_ok=True)
    preguntas = pd.read_csv(RAIZ / "evaluacion" / "preguntas.csv")
    casos = [(q, m) for m in a.modos for q in preguntas.itertuples()]
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}...")
    with ThreadPoolExecutor(a.paralelo) as ex:
        resp = list(ex.map(lambda c: preguntar(c[0].id, c[0].pregunta, c[1], a.modelo), casos))
    filas = [{"id": q.id, "tipo": q.tipo, "modo": m, "pregunta": q.pregunta, "verdad": q.verdad,
              "tolerancia": q.tolerancia, **r, "resultado": calificar(r["valor"], q.verdad, q.tolerancia, q.tipo,
                                                                      r["fuente"])}
             for (q, m), r in zip(casos, resp)]
    res = pd.DataFrame(filas)
    destino = RAIZ / "evaluacion" / "resultados.csv"
    if destino.exists() and set(a.modos) != {"A", "B"}:
        prev = pd.read_csv(destino)
        res = pd.concat([prev[~prev.modo.isin(a.modos)], res], ignore_index=True)
    res.to_csv(destino, index=False, encoding="utf-8")
    print(res.pivot(index="id", columns="modo", values="valor").to_string())
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos_promedio"] = res.groupby("modo").segundos.mean().round(1)
    print(tabla.to_string())


if __name__ == "__main__":
    main()
