#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las 17 entradas de blog + el índice del blog desde contenido/03-blog/*/texto.md."""
import re, json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "contenido" / "03-blog"
OUT = ROOT / "_build" / "pages"

# Una imagen ÚNICA por post (no copyright), elegida por tema.
POSTS = [
 ("tratamientos-de-estetica-dental-mas-innovadores-para-lograr-una-sonrisa-perfecta",
  "tratamientos-de-estetica-dental-mas-innovadores.html", "casos/paciente-1.jpg", "15 sep 2025", "2025-09-15", "Estética dental"),
 ("implantes-dentales-y-salud-osea-lo-que-debes-saber",
  "implantes-dentales-y-salud-osea.html", "blog/laboratorio-muestras.jpg", "1 sep 2025", "2025-09-01", "Implantes"),
 ("sabias-que-la-ortodoncia-tambien-mejora-la-respiracion-y-el-sueno",
  "ortodoncia-mejora-respiracion-y-sueno.html", "blog/cerebro-neurona.jpg", "15 ago 2025", "2025-08-15", "Ortodoncia"),
 ("7-cosas-que-nadie-te-cuenta-sobre-llevar-ortodoncia",
  "7-cosas-sobre-llevar-ortodoncia.html", "blog/ortodoncia-separador.jpg", "1 ago 2025", "2025-08-01", "Ortodoncia"),
 ("beneficios-de-la-ortodoncia-en-adolescentes-mas-alla-de-la-estetica",
  "ortodoncia-en-adolescentes.html", "casos/paciente-2.jpg", "15 jul 2025", "2025-07-15", "Ortodoncia"),
 ("como-funciona-la-odontologia-preventiva",
  "como-funciona-la-odontologia-preventiva.html", "clinica/higiene-cepillos.jpg", "1 jul 2025", "2025-07-01", "Prevención"),
 ("como-la-ortodoncia-mejora-la-mordida-la-estetica-y-la-salud",
  "ortodoncia-mordida-estetica-y-salud.html", "clinica/ortodoncia-invisible.jpg", "15 jun 2025", "2025-06-15", "Ortodoncia"),
 ("implantes-dentales-todo-lo-que-necesitas-saber-antes-de-decidirte",
  "implantes-todo-lo-que-necesitas-saber.html", "blog/consulta-reunion.jpg", "1 jun 2025", "2025-06-01", "Implantes"),
 ("implantes-dentales-vs-protesis-cual-es-la-mejor-opcion",
  "implantes-vs-protesis.html", "blog/diagnostico-pantallas.jpg", "15 may 2025", "2025-05-15", "Implantes"),
 ("la-revolucion-de-los-implantes-dentales-en-la-estetica-dental",
  "revolucion-implantes-estetica.html", "hero/sonrisa-hero.jpg", "1 may 2025", "2025-05-01", "Implantes"),
 ("mitos-y-realidades-sobre-los-implantes-dentales-que-debes-conocer",
  "mitos-y-realidades-implantes.html", "blog/medicacion.jpg", "15 abr 2025", "2025-04-15", "Implantes"),
 ("ortodoncia-invisible-todo-lo-que-debes-saber-antes-de-empezar",
  "ortodoncia-invisible-antes-de-empezar.html", "casos/paciente-3.jpg", "1 abr 2025", "2025-04-01", "Ortodoncia"),
 ("oxido-nitroso",
  "fobia-dental-sedacion.html", "blog/cerebro-modelo.jpg", "15 mar 2025", "2025-03-15", "Sedación"),
 ("que-resultados-puedes-esperar-con-los-implantes-dentales",
  "resultados-implantes-dentales.html", "clinica/cirugia-implante.jpg", "1 mar 2025", "2025-03-01", "Implantes"),
 ("quien-es-candidato-para-implantes-dentales",
  "quien-es-candidato-implantes.html", "blog/consulta-online.jpg", "15 feb 2025", "2025-02-15", "Implantes"),
 ("todo-lo-que-debes-saber-sobre-la-cirugia-de-implantes-dentales",
  "cirugia-de-implantes-dentales.html", "blog/quirofano-vacio.jpg", "1 feb 2025", "2025-02-01", "Cirugía"),
 ("vale-la-pena-la-ortodoncia-invisible-te-lo-contamos-todo",
  "vale-la-pena-ortodoncia-invisible.html", "casos/paciente-4.jpg", "15 ene 2025", "2025-01-15", "Ortodoncia"),
]

def esc(t): return html.escape(t, quote=True)

BOILER = ["Solicitar Cita Online","DESCUBRE TODOS NUESTROS TRATAMIENTOS","QUÉ DICEN NUESTROS PACIENTES",
          "NUESTRO BLOG","Consejos y Recomendaciones","Contacta con Nosotros"]

def parse_post(slug):
    text = (SRC/slug/"texto.md").read_text(encoding="utf-8")
    # corta el boilerplate final
    for b in ["#### DESCUBRE TODOS NUESTROS TRATAMIENTOS","## Cuidamos de tu salud","#### Nuestros pacientes opinan","#### NUESTRO BLOG"]:
        i = text.find(b)
        if i!=-1: text = text[:i]
    lines = text.splitlines()
    title = None
    blocks = []  # (h2/h3/p/li)
    started=False
    for ln in lines:
        s=ln.strip()
        if not s: continue
        if s.startswith("URL:") or s.startswith("**Meta") or s=="---": continue
        if any(b in s for b in BOILER): continue
        if s in ("- Clínica Dental Oiasso®","- 0 Comments","Solicitar Cita Online"): continue
        hm=re.match(r"^(#{1,4})\s+(.*)$", s)
        if hm:
            lvl,txt=len(hm.group(1)),hm.group(2).strip()
            txt=re.sub(r"\s*-\s*Clínica Dental Oiasso®.*$","",txt)
            if lvl==1 and title is None:
                title=txt; started=True; continue
            if not started: continue
            blocks.append(("h2" if lvl<=2 else "h3", txt))
            continue
        if not started: continue
        bm=re.match(r"^[-–●•]\s*(.*)$", s)
        if bm:
            blocks.append(("li", bm.group(1).strip())); continue
        blocks.append(("p", s))
    return title or slug, blocks

def render_blocks(blocks):
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

def first_para(blocks):
    for k,t in blocks:
        if k=="p" and len(t)>40: return t
    for k,t in blocks:
        if k=="p": return t
    return ""

INDEX_CARDS=[]

def build_post(slug, outname, img, date_h, date_iso, cat):
    title, blocks = parse_post(slug)
    body = render_blocks(blocks)
    excerpt = first_para(blocks)
    desc = excerpt[:155].replace('"',"'")
    INDEX_CARDS.append((outname, img, date_h, date_iso, cat, title, excerpt[:120]))

    schema = {"@context":"https://schema.org","@type":"BlogPosting",
              "headline":esc(title),"datePublished":date_iso,"dateModified":date_iso,
              "image":f"https://clinicadentaloiasso.com/assets/img/{img}",
              "author":{"@type":"Organization","name":"Clínica Dental Oiasso"},
              "publisher":{"@type":"Organization","name":"Clínica Dental Oiasso",
                           "logo":{"@type":"ImageObject","url":"https://clinicadentaloiasso.com/assets/img/brand/logo-oiasso.png"}},
              "mainEntityOfPage":f"https://clinicadentaloiasso.com/blog/{outname}"}
    schema_html='<script type="application/ld+json">\n'+json.dumps(schema,ensure_ascii=False)+'\n</script>'

    meta={"out":f"blog/{outname}","title":f"{title} | Blog Oiasso",
          "desc":desc or "Consejos dentales de la Clínica Dental Oiasso en Irún.",
          "keywords":f"{cat.lower()} Irún, blog dental, Clínica Dental Oiasso, consejos dentales",
          "ogtype":"article","ogimg":img,"nav":"A_BLOG","schema":schema_html}

    page=f'''<main id="main">
  <article>
  <section class="page-hero">
    <div class="page-hero__bg" aria-hidden="true"><img src="{{{{BASE}}}}assets/img/{img}" alt=""></div>
    <div class="container container--narrow page-hero__inner">
      <nav class="breadcrumb" aria-label="Migas de pan"><a href="{{{{BASE}}}}index.html">Inicio</a> <span>/</span> <a href="{{{{BASE}}}}blog/index.html">Blog</a> <span>/</span> <span aria-current="page">{esc(cat)}</span></nav>
      <span class="pill pill--magenta">{esc(cat)} · {esc(date_h)}</span>
      <h1 class="page-hero__title" style="max-width:24ch">{esc(title)}</h1>
    </div>
  </section>
  <section class="section">
    <div class="container container--narrow">
      <div class="split__media" style="aspect-ratio:16/9;margin-bottom:var(--space-l)"><img src="{{{{BASE}}}}assets/img/{img}" alt="{esc(title)} — Clínica Dental Oiasso, Irún" loading="lazy"></div>
      <div class="prose" style="margin-inline:auto">
        {body}
      </div>
      <div class="cta-band" style="margin-top:var(--space-xl)">
        <h2>¿Tienes dudas sobre tu caso?</h2>
        <p style="margin-top:var(--space-s)">Pide tu primera visita en la Clínica Dental Oiasso de Irún y te asesoramos sin compromiso.</p>
        <div class="btn-row" style="justify-content:center;margin-top:var(--space-m)"><a class="btn btn--white btn--lg magnetic" href="{{{{BASE}}}}contacto.html"><span>Pedir cita</span><svg class="btn__icon" width="22" height="22"><use href="#i-arrow"/></svg></a></div>
      </div>
    </div>
  </section>
  </article>
</main>'''
    block="<!--META\n"+json.dumps(meta,ensure_ascii=False,indent=1)+"\nMETA-->\n\n"+page+"\n"
    (OUT/f"post-{outname}").write_text(block,encoding="utf-8")

def build_index():
    cards=[]
    for outname,img,date_h,date_iso,cat,title,excerpt in INDEX_CARDS:
        cards.append(f'''<article class="post-card" data-reveal>
  <a class="post-card__media" href="{{{{BASE}}}}blog/{outname}"><img src="{{{{BASE}}}}assets/img/{img}" alt="{esc(title)}" loading="lazy"></a>
  <div class="post-card__body"><span class="post-card__date">{esc(cat)} · {esc(date_h)}</span><h2 class="post-card__title"><a href="{{{{BASE}}}}blog/{outname}">{esc(title)}</a></h2><p class="post-card__excerpt">{esc(excerpt)}…</p><a class="link-arrow" href="{{{{BASE}}}}blog/{outname}">Leer más <svg width="18" height="18"><use href="#i-arrow"/></svg></a></div>
</article>''')
    meta={"out":"blog/index.html","title":"Blog dental | Clínica Dental Oiasso en Irún",
          "desc":"Consejos y recomendaciones dentales de la Clínica Dental Oiasso en Irún: implantes, ortodoncia, estética dental, prevención y más.",
          "keywords":"blog dental Irún, consejos dentales, implantes, ortodoncia, Clínica Dental Oiasso","ogtype":"website","ogimg":"casos/paciente-1.jpg","nav":"A_BLOG"}
    page=f'''<main id="main">
  <section class="page-hero">
    <div class="page-hero__bg" aria-hidden="true"><img src="{{{{BASE}}}}assets/img/casos/paciente-1.jpg" alt=""></div>
    <div class="container page-hero__inner">
      <nav class="breadcrumb" aria-label="Migas de pan"><a href="{{{{BASE}}}}index.html">Inicio</a> <span>/</span> <span aria-current="page">Blog</span></nav>
      <span class="pill"><svg width="18" height="18"><use href="#i-leaf"/></svg> Nuestro blog</span>
      <h1 class="page-hero__title">Consejos y recomendaciones dentales</h1>
      <p class="lead page-hero__lead">Aprende a cuidar tu sonrisa con los artículos de nuestro equipo: implantes, ortodoncia, estética dental y prevención.</p>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="post-grid">
        {"".join(cards)}
      </div>
    </div>
  </section>
</main>'''
    block="<!--META\n"+json.dumps(meta,ensure_ascii=False,indent=1)+"\nMETA-->\n\n"+page+"\n"
    (OUT/"30-blog-index.html").write_text(block,encoding="utf-8")

if __name__=="__main__":
    for p in POSTS:
        build_post(*p)
    build_index()
    print(f"{len(POSTS)} posts + índice generados.")
