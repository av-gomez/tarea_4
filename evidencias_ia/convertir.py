"""Convierte transcripciones de Claude Code (JSONL de sesiones o de `claude -p --output-format stream-json`)
a Markdown legible, ocultando rutas personales, correos y tokens.

    uv run evidencias_ia/convertir.py entrada.jsonl salida.md [--titulo "..."]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATRONES = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[correo oculto]"),
    (re.compile(r"(gh[opsu]_|sk-ant-|sk-)[A-Za-z0-9_\-]{8,}"), "[token oculto]"),
    (re.compile(r"(?i)C:[\\/]+Users[\\/]+[^\\/\s\"']+"), "C:/Users/[usuario]"),
    (re.compile(r"/c/Users/[^/\s\"']+"), "/c/Users/[usuario]"),
    (re.compile(r"(?i)VVILLA~1"), "[usuario]"),
]
MAX = 4000


def limpiar(t: str) -> str:
    for p, r in PATRONES:
        t = p.sub(r, t)
    return t


def bloque(texto: str, lenguaje: str = "") -> str:
    texto = str(texto)
    if len(texto) > MAX:
        texto = texto[:MAX] + f"\n... [{len(texto) - MAX} caracteres omitidos]"
    return f"```{lenguaje}\n{texto.replace('```', '` ` `')}\n```"


def contenido(c) -> list[str]:
    if isinstance(c, str):
        return [c]
    partes = []
    for b in c or []:
        t = b.get("type")
        if t == "text":
            partes.append(b["text"])
        elif t == "thinking":
            continue
        elif t == "tool_use":
            partes.append(f"**Herramienta:** `{b['name']}`\n\n" + bloque(json.dumps(b.get("input", {}),
                                                                                   ensure_ascii=False, indent=1),
                                                                        "json"))
        elif t == "tool_result":
            r = b.get("content")
            if isinstance(r, list):
                r = "\n".join(x.get("text", "[imagen]") if isinstance(x, dict) else str(x) for x in r)
            partes.append("**Resultado de la herramienta:**\n\n" + bloque(r))
        elif t == "image":
            partes.append("[imagen]")
    return partes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--titulo", default="Transcripción de Claude Code")
    a = ap.parse_args()
    md = [f"# {a.titulo}", "", f"Fuente: `{Path(a.entrada).name}` (convertido con evidencias_ia/convertir.py; "
          "rutas personales, correos y tokens ocultados).", ""]
    n = 0
    for linea in Path(a.entrada).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev = json.loads(linea)
        except json.JSONDecodeError:
            continue
        tipo = ev.get("type")
        if tipo in ("user", "assistant") and "message" in ev:
            partes = contenido(ev["message"].get("content"))
            if not partes:
                continue
            n += 1
            quien = "Usuario" if tipo == "user" else "Asistente (Claude)"
            if tipo == "user" and all(p.startswith("**Resultado") for p in partes):
                quien = "Resultado"
            md += [f"## {n}. {quien}", "", *[p + "\n" for p in partes]]
        elif tipo == "result":
            md += ["## Resultado final", "", f"- Turnos: {ev.get('num_turns')}",
                   f"- Duración: {ev.get('duration_ms', 0) / 1000:.0f} s", f"- Error: {ev.get('is_error')}", "",
                   str(ev.get("result", "")), ""]
        elif tipo == "system" and ev.get("subtype") == "init":
            md += ["## Configuración de la sesión", "", f"- Modelo: {ev.get('model')}",
                   f"- Servidores MCP: {json.dumps(ev.get('mcp_servers'), ensure_ascii=False)}",
                   f"- Skills: {', '.join(ev.get('skills', []) or [])}",
                   f"- Herramientas: {', '.join(ev.get('tools', []))}", ""]
    Path(a.salida).write_text(limpiar("\n".join(md)), encoding="utf-8")
    print(f"{a.salida}: {n} mensajes")


if __name__ == "__main__":
    main()
