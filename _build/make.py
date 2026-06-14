#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orquestador: genera contenido, ensambla páginas, postprocesa y crea el sitemap."""
import subprocess, sys, pathlib, datetime
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable

def run(name):
    print(f"\n=== {name} ===")
    subprocess.run([PY, str(HERE/name)], check=True)

for g in ("gen_services.py","gen_blog.py","gen_legal.py","build.py","postprocess.py"):
    run(g)

# sitemap
today=datetime.date.today().isoformat()
pages=[]
globs=[ROOT.glob("*.html")]
for sub in ("tratamientos","blog","casos","legal"):
    globs.append((ROOT/sub).glob("*.html"))
seen=set()
for g in globs:
    for p in sorted(g):
        rel=p.relative_to(ROOT).as_posix()
        if rel=="404.html" or rel in seen: continue
        seen.add(rel)
        url="https://clinicadentaloiasso.com/"+("" if rel=="index.html" else rel)
        if rel=="index.html": pr,cf="1.0","weekly"
        elif rel.startswith("tratamientos/") or rel in ("contacto.html","clinica.html","casos/index.html"): pr,cf="0.9","monthly"
        elif rel.startswith("blog/"): pr,cf="0.7","monthly"
        elif rel.startswith("legal/"): pr,cf="0.3","yearly"
        else: pr,cf="0.8","monthly"
        pages.append((url,pr,cf))
out=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url,pr,cf in pages:
    out.append(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>")
out.append("</urlset>")
(ROOT/"sitemap.xml").write_text("\n".join(out)+"\n",encoding="utf-8")
print(f"\n=== sitemap.xml: {len(pages)} URLs ===")
print("\nBuild completo.")
