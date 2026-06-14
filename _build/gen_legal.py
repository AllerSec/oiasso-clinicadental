#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las páginas legales desde contenido/05-legal/*/texto.md (texto íntegro)."""
import re, json, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "contenido" / "05-legal"
OUT = ROOT / "_build" / "pages"

LEGAL = {
 "aviso-legal":            ("Aviso Legal", "legal/aviso-legal.html", 40),
 "politica-de-privacidad": ("Política de Privacidad", "legal/politica-de-privacidad.html", 41),
 "politica-de-cookies":    ("Política de Cookies", "legal/politica-de-cookies.html", 42),
}
def esc(t): return html.escape(t, quote=True)

def parse(slug):
    text=(SRC/slug/"texto.md").read_text(encoding="utf-8")
    lines=text.splitlines()
    blocks=[]; started=False; seen_dupe=set()
    for ln in lines:
        s=ln.strip()
        if not s: continue
        if s.startswith("URL:") or s=="---": continue
        hm=re.match(r"^(#{1,4})\s+(.*)$", s)
        if hm:
            lvl,txt=len(hm.group(1)),hm.group(2).strip()
            txt=re.sub(r"\s*-\s*Clínica Dental Oiasso®.*$","",txt)
            if lvl==1 and not started:
                started=True; continue
            blocks.append(("h2" if lvl<=2 else "h3", txt)); continue
        if not started: continue
        bm=re.match(r"^[-–●•]\s*(.*)$", s)
        if bm:
            blocks.append(("li", bm.group(1).strip())); continue
        # evitar líneas duplicadas (el scraper repite el bloque de datos en línea + bullets)
        key=s[:60]
        blocks.append(("p", s))
    return blocks

def render(blocks):
    out=[]; in_ul=False
    for k,t in blocks:
        if k=="li":
            if not in_ul: out.append("<ul>"); in_ul=True
            out.append(f"<li>{esc(t)}</li>")
        else:
            if in_ul: out.append("</ul>"); in_ul=False
            out.append(f"<{k}>{esc(t)}</{k}>" if k!="p" else f"<p>{esc(t)}</p>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)

for slug,(title,out,order) in LEGAL.items():
    body=render(parse(slug))
    meta={"out":out,"title":f"{title} | Clínica Dental Oiasso",
          "desc":f"{title} de la Clínica Dental Oiasso en Irún (Gipuzkoa).",
          "keywords":f"{title.lower()}, Clínica Dental Oiasso, Irún","ogtype":"website",
          "ogimg":"clinica/gabinete-moderno.jpg","nav":""}
    page=f'''<main id="main">
  <section class="page-hero">
    <div class="container page-hero__inner">
      <nav class="breadcrumb" aria-label="Migas de pan"><a href="{{{{BASE}}}}index.html">Inicio</a> <span>/</span> <span aria-current="page">{esc(title)}</span></nav>
      <h1 class="page-hero__title">{esc(title)}</h1>
    </div>
  </section>
  <section class="section">
    <div class="container container--narrow">
      <div class="prose" style="margin-inline:auto">
        {body}
      </div>
    </div>
  </section>
</main>'''
    block="<!--META\n"+json.dumps(meta,ensure_ascii=False,indent=1)+"\nMETA-->\n\n"+page+"\n"
    (OUT/f"legal-{order}-{slug}.html").write_text(block,encoding="utf-8")
    print("  legal:",out)
print("Legales generadas.")
