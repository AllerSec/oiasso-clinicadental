#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera los cuerpos de página de los 11 tratamientos a partir de contenido/02-servicios/*/texto.md
   Respeta el texto original; lo reorganiza en una landing de servicio."""
import re, json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "contenido" / "02-servicios"
OUT = ROOT / "_build" / "pages"

# slug -> config
SERVICES = {
    "implantes-dentales":     dict(title="Implantes Dentales", icon="i-implante",     img="clinica/cirugia-implante.jpg",    kicker="Una opción de aspecto natural", order=1),
    "ortodoncia-invisible":   dict(title="Ortodoncia Invisible", icon="i-invisible",  img="clinica/ortodoncia-invisible.jpg", kicker="Presume de sonrisa", order=2),
    "estetica-dental":        dict(title="Estética Dental", icon="i-estetica",        img="casos/paciente-1.jpg",            kicker="Carillas dentales en Irún", order=3),
    "brackets":               dict(title="Brackets", icon="i-brackets",               img="casos/paciente-3.jpg",            kicker="Ortodoncia en Irún", order=4),
    "cirugia-oral":           dict(title="Cirugía Oral", icon="i-cirugia",            img="clinica/cirugia-quirofano.jpg",   kicker="Clínica Dental Oiasso en Irún", order=5),
    "endodoncia":             dict(title="Endodoncia", icon="i-endodoncia",           img="clinica/radiografias.jpg",        kicker="Clínica Dental Oiasso en Irún", order=6),
    "periodoncia":            dict(title="Periodoncia", icon="i-periodoncia",         img="clinica/limpieza-dental.jpg",     kicker="Salud de tus encías", order=7),
    "odontologia-conservadora":dict(title="Odontología Conservadora", icon="i-conservadora", img="clinica/higiene-cepillos.jpg", kicker="Prevención y cuidado", order=8),
    "blanqueamiento-dental":  dict(title="Blanqueamiento Dental", icon="i-blanqueamiento", img="casos/paciente-4.jpg",        kicker="Sonrisa más luminosa", order=9),
    "odontopediatria":        dict(title="Odontopediatría", icon="i-pediatria",       img="casos/paciente-2.jpg",            kicker="Los más peques", order=10),
    "sedacion-consciente":    dict(title="Sedación Consciente", icon="i-sedacion",    img="clinica/doctora.jpg",             kicker="Adiós al miedo al dentista", order=11),
}

GALLERY = ["clinica/gabinete-moderno.jpg","clinica/gabinete-naranja.jpg","clinica/radiografias.jpg",
           "clinica/limpieza-dental.jpg","clinica/higiene-cepillos.jpg","clinica/doctora.jpg"]

def esc(t): return html.escape(t, quote=True)

def parse_md(path):
    """Devuelve dict con title, kicker_intro (primer bloque), body paragraphs (h2/h3/p/li), faqs."""
    lines = path.read_text(encoding="utf-8").splitlines()
    # quitar cabecera (title, URL, metadesc) hasta el primer '---' o primer '##'
    intro_paras, faqs = [], []
    body = []  # list of ('h3'/'p'/'liheader'/'li', text)
    in_faq = False
    cur_q = None
    cur_a = []
    # Recortar todo lo posterior a "DESCUBRE TODOS NUESTROS TRATAMIENTOS" (boilerplate repetido)
    text = "\n".join(lines)
    cut = text.find("#### DESCUBRE TODOS NUESTROS TRATAMIENTOS")
    if cut == -1: cut = text.find("DESCUBRE TODOS NUESTROS TRATAMIENTOS")
    if cut != -1: text = text[:cut]
    lines = text.splitlines()

    started = False
    skip_next_blank = False
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        # saltar las primeras líneas meta
        if s.startswith("URL:") or s.startswith("**Meta") or s == "---":
            continue
        if s.startswith("# ") and not started:
            # título principal de la página (lo ignoramos, usamos config)
            started = True
            continue
        # detectar zona FAQ
        if "Preguntas Frecuentes" in s or s.startswith("## ") and "Faq" in s:
            in_faq = True
            continue
        # CTAs repetidos: saltar
        if s in ("Solicitar Cita Online",) or s.startswith("### Llámanos") or s.startswith("Llámanos Y Solicita"):
            continue
        # headings
        hm = re.match(r"^(#{2,4})\s+(.*)$", s)
        if hm:
            level, txt = len(hm.group(1)), hm.group(2).strip()
            if in_faq:
                if level >= 3:  # nueva pregunta
                    if cur_q:
                        faqs.append((cur_q, cur_a)); cur_a=[]
                    cur_q = txt
                continue
            else:
                # h2 grandes que son el nombre del servicio -> los tratamos como subtítulo del body
                if txt.upper() == txt and level==2:
                    continue
                body.append(("h3", txt))
            continue
        # bullets
        bm = re.match(r"^[-–●•]\s*(.*)$", s)
        if bm:
            item = bm.group(1).strip()
            if in_faq and cur_q is not None:
                cur_a.append(("li", item))
            else:
                body.append(("li", item))
            continue
        # parrafo normal
        if in_faq and cur_q is not None:
            cur_a.append(("p", s))
        elif not started or len(intro_paras) < 2 and not body:
            intro_paras.append(s)
        else:
            body.append(("p", s))
    if cur_q:
        faqs.append((cur_q, cur_a))
    return intro_paras, body, faqs

def render_body_block(items):
    out = []
    in_ul = False
    for kind, txt in items:
        if kind == "li":
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{esc(txt)}</li>")
        else:
            if in_ul:
                out.append("</ul>"); in_ul = False
            if kind == "h3":
                out.append(f"<h3>{esc(txt)}</h3>")
            else:
                out.append(f"<p>{esc(txt)}</p>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)

def faq_schema(slug, title, faqs):
    if not faqs: return ""
    items = []
    for q, a in faqs:
        ans = " ".join(esc(t) if k=="p" else esc(t) for k,t in a) or esc(title)
        items.append({"@type":"Question","name":esc(q),
                      "acceptedAnswer":{"@type":"Answer","text":ans}})
    data = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":items}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False) + '\n</script>'

def aside_list(active):
    rows=[]
    for slug,c in sorted(SERVICES.items(), key=lambda kv: kv[1]["order"]):
        cur = ' aria-current="page"' if slug==active else ''
        rows.append(f'<a href="{{{{BASE}}}}tratamientos/{slug}.html"{cur}>{esc(c["title"])} <svg width="16" height="16"><use href="#i-arrow"/></svg></a>')
    rows.append('<a href="{{BASE}}tratamientos/sedacion-consciente.html">Sedación consciente <svg width="16" height="16"><use href="#i-arrow"/></svg></a>')
    return "\n".join(rows)

def build_service(slug, cfg):
    intro, body, faqs = parse_md(SRC/slug/"texto.md")
    intro_html = "\n".join(f"<p>{esc(p)}</p>" for p in intro[:3])
    body_html = render_body_block(body)
    faqs_html = ""
    if faqs:
        faq_items=[]
        for q,a in faqs:
            ans = render_body_block(a)
            faq_items.append(f'''<details class="faq__item"><summary class="faq__q">{esc(q)} <svg class="faq__icon"><use href="#i-plus"/></svg></summary><div class="faq__a">{ans}</div></details>''')
        faqs_html = f'''
  <section class="section bg-surface">
    <div class="container container--narrow">
      <div class="section-head section-head--center"><span class="eyebrow">Preguntas frecuentes</span><h2>{esc(cfg["title"])} en Irún</h2></div>
      <div class="faq">
        {"".join(faq_items)}
      </div>
    </div>
  </section>'''

    gal = "\n".join(f'<figure><img src="{{{{BASE}}}}assets/img/{g}" alt="{esc(cfg["title"])} en la Clínica Dental Oiasso de Irún — imagen {i+1}" loading="lazy"></figure>' for i,g in enumerate(GALLERY))

    schema = faq_schema(slug, cfg["title"], faqs)

    meta = {
        "out": f"tratamientos/{slug}.html",
        "title": f"{cfg['title']} en Irún | Clínica Dental Oiasso",
        "desc": (intro[0][:150] if intro else f"{cfg['title']} en la Clínica Dental Oiasso de Irún.").replace('"',"'"),
        "keywords": f"{cfg['title'].lower()} Irún, {cfg['title'].lower()} Gipuzkoa, dentista Irún, Clínica Dental Oiasso",
        "ogtype":"article", "ogimg": cfg["img"], "nav":("A_SED" if slug=="sedacion-consciente" else "A_TRAT"),
        "schema": schema,
    }

    body_page = f'''<main id="main">
  <section class="page-hero">
    <div class="page-hero__bg" aria-hidden="true"><img src="{{{{BASE}}}}assets/img/{cfg['img']}" alt=""></div>
    <div class="container page-hero__inner">
      <nav class="breadcrumb" aria-label="Migas de pan"><a href="{{{{BASE}}}}index.html">Inicio</a> <span>/</span> <a href="{{{{BASE}}}}tratamientos/index.html">Tratamientos</a> <span>/</span> <span aria-current="page">{esc(cfg['title'])}</span></nav>
      <span class="pill"><svg width="18" height="18"><use href="#{cfg['icon']}"/></svg> {esc(cfg['kicker'])}</span>
      <h1 class="page-hero__title">{esc(cfg['title'])}</h1>
      <div class="btn-row" style="margin-top:var(--space-m)">
        <a class="btn magnetic" href="{{{{BASE}}}}contacto.html"><span>Solicitar cita</span><svg class="btn__icon" width="22" height="22"><use href="#i-arrow"/></svg></a>
        <a class="btn btn--ghost" href="tel:+34943633933"><svg width="20" height="20"><use href="#i-phone"/></svg><span>943 633 933</span></a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container svc-layout">
      <article class="prose">
        {intro_html}
        <div class="split__media" style="aspect-ratio:16/9;margin-block:var(--space-m)"><img src="{{{{BASE}}}}assets/img/{cfg['img']}" alt="{esc(cfg['title'])} en Irún — Clínica Dental Oiasso" loading="lazy"></div>
        {body_html}
      </article>
      <aside class="svc-aside">
        <div class="aside-card aside-card--green">
          <h3>¿Hablamos de tu caso?</h3>
          <p>Pide tu primera visita y recibe un plan de tratamiento personalizado por escrito, sin compromiso.</p>
          <div class="btn-row" style="margin-top:var(--space-s)"><a class="btn btn--white" href="{{{{BASE}}}}contacto.html"><span>Pedir cita</span></a></div>
        </div>
        <div class="aside-card">
          <h3 style="font-size:var(--step-1);margin-bottom:var(--space-s)">Más tratamientos</h3>
          <nav class="aside-list" aria-label="Tratamientos">
            {aside_list(slug)}
          </nav>
        </div>
      </aside>
    </div>
  </section>
{faqs_html}
  <section class="section--tight">
    <div class="container">
      <div class="section-head section-head--center"><span class="eyebrow">Nuestra clínica</span><h2>El entorno donde te cuidamos</h2></div>
      <div class="img-grid">
        {gal}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container"><div class="cta-band">
      <div class="cta-band__deco" aria-hidden="true"><svg width="100%" height="100%" viewBox="0 0 1200 300" preserveAspectRatio="none" fill="none"><path d="M0 200c300-120 900-120 1200 0" stroke="#fff" stroke-width="3"/></svg></div>
      <h2>¿Damos el primer paso?</h2>
      <p style="margin-top:var(--space-s)">Estamos en el centro de Irún. Llámanos o escríbenos por WhatsApp y te asesoramos sin compromiso.</p>
      <div class="btn-row" style="justify-content:center;margin-top:var(--space-m)">
        <a class="btn btn--white btn--lg magnetic" href="{{{{BASE}}}}contacto.html"><span>Pedir cita</span><svg class="btn__icon" width="22" height="22"><use href="#i-arrow"/></svg></a>
        <a class="btn btn--lg magnetic" style="--btn-bg:var(--brand-magenta)" href="https://wa.me/34646290701"><svg width="22" height="22"><use href="#i-wa"/></svg><span>WhatsApp</span></a>
      </div>
    </div></div>
  </section>
</main>'''

    block = "<!--META\n" + json.dumps(meta, ensure_ascii=False, indent=1) + "\nMETA-->\n\n" + body_page + "\n"
    (OUT / f"svc-{cfg['order']:02d}-{slug}.html").write_text(block, encoding="utf-8")
    return slug, len(faqs)

if __name__ == "__main__":
    for slug, cfg in SERVICES.items():
        s, nf = build_service(slug, cfg)
        print(f"  {s}: {nf} FAQs")
    print("Servicios generados.")
