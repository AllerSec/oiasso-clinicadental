#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build estático para Clínica Dental Oiasso.
Lee páginas desde _build/pages/*.html (con front-matter JSON entre <!--META ... META-->)
y ensambla cada una con los partials compartidos (head, header, footer, sprite).
Salida en la raíz del repo, en las rutas indicadas por cada página.
"""
import json, re, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "_build" / "partials"
PAGES = ROOT / "_build" / "pages"

HEAD   = (P / "head.html").read_text(encoding="utf-8")
HEADER = (P / "header.html").read_text(encoding="utf-8")
FOOTER = (P / "footer.html").read_text(encoding="utf-8")
SPRITE = (P / "sprite.html").read_text(encoding="utf-8")

HEADER = HEADER.replace("__SPRITE__", SPRITE)

NAV_KEYS = ["A_HOME", "A_CLIN", "A_TRAT", "A_SED", "A_PAC", "A_CASOS", "A_BLOG", "A_CONT"]

def render(meta, body):
    out_rel = meta["out"]                      # p.ej. "tratamientos/implantes-dentales.html"
    depth = out_rel.count("/")
    base = "../" * depth                       # ruta relativa a la raíz
    canon = "" if out_rel == "index.html" else out_rel

    head = HEAD
    repl = {
        "{{TITLE}}": meta["title"],
        "{{DESC}}": meta["desc"],
        "{{KEYWORDS}}": meta.get("keywords", "clínica dental Irún, dentista Irún, Oiasso"),
        "{{CANON}}": canon,
        "{{OGTYPE}}": meta.get("ogtype", "website"),
        "{{OGIMG}}": meta.get("ogimg", "hero/sonrisa-hero.jpg"),
        "{{SCHEMA}}": meta.get("schema", ""),
        "{{BASE}}": base,
    }
    for k, v in repl.items():
        head = head.replace(k, v)

    header = HEADER.replace("{{BASE}}", base)
    active = meta.get("nav", "")
    for key in NAV_KEYS:
        token = "{{" + key + "}}"
        if key == active:
            header = header.replace(token, ' data-current="page"')
        else:
            header = header.replace(token, "")

    footer = FOOTER.replace("{{BASE}}", base)
    body = body.replace("{{BASE}}", base)

    return head + "\n" + header + "\n" + body + "\n" + footer

def main():
    built = []
    for page in sorted(PAGES.glob("*.html")):
        raw = page.read_text(encoding="utf-8")
        m = re.search(r"<!--META\s*(\{.*?\})\s*META-->", raw, re.S)
        if not m:
            print("  [skip] sin META:", page.name); continue
        meta = json.loads(m.group(1))
        body = raw[m.end():].strip()
        html = render(meta, body)
        out_path = ROOT / meta["out"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        built.append(meta["out"])
        print("  [ok]", meta["out"])
    print(f"\n{len(built)} páginas generadas.")
    return built

if __name__ == "__main__":
    main()
