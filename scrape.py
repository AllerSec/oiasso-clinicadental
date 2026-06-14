# -*- coding: utf-8 -*-
"""
Scraper para clinicadentaloiasso.com
Descarga textos e imagenes de todas las paginas del sitemap y las clasifica
en carpetas / subcarpetas.
"""
import os
import re
import time
import hashlib
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

BASE = "https://clinicadentaloiasso.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contenido")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Estructura: carpeta -> lista de (slug_subcarpeta, url)
SITE = {
    "01-paginas-principales": [
        ("home",          f"{BASE}/"),
        ("clinica",       f"{BASE}/clinica/"),
        ("contacto",      f"{BASE}/contacto/"),
        ("casos-reales",  f"{BASE}/casos-reales/"),
    ],
    "02-servicios": [
        ("odontologia-conservadora", f"{BASE}/odontologia-conservadora/"),
        ("sedacion-consciente",      f"{BASE}/sedacion-consciente/"),
        ("brackets",                 f"{BASE}/brackets/"),
        ("blanqueamiento-dental",    f"{BASE}/blanqueamiento-dental/"),
        ("implantes-dentales",       f"{BASE}/implantes-dentales/"),
        ("ortodoncia-invisible",     f"{BASE}/ortodoncia-invisible/"),
        ("estetica-dental",          f"{BASE}/estetica-dental/"),
        ("endodoncia",               f"{BASE}/endodoncia/"),
        ("periodoncia",              f"{BASE}/periodoncia/"),
        ("cirugia-oral",             f"{BASE}/cirugia-oral/"),
        ("odontopediatria",          f"{BASE}/odontopediatria/"),
    ],
    "03-blog": [
        ("blog-index", f"{BASE}/blog/"),
        ("oxido-nitroso", f"{BASE}/oxido-nitroso/"),
        ("quien-es-candidato-para-implantes-dentales", f"{BASE}/quien-es-candidato-para-implantes-dentales/"),
        ("como-funciona-la-odontologia-preventiva", f"{BASE}/como-funciona-la-odontologia-preventiva/"),
        ("implantes-dentales-todo-lo-que-necesitas-saber-antes-de-decidirte", f"{BASE}/implantes-dentales-todo-lo-que-necesitas-saber-antes-de-decidirte/"),
        ("implantes-dentales-vs-protesis-cual-es-la-mejor-opcion", f"{BASE}/implantes-dentales-vs-protesis-cual-es-la-mejor-opcion/"),
        ("mitos-y-realidades-sobre-los-implantes-dentales-que-debes-conocer", f"{BASE}/mitos-y-realidades-sobre-los-implantes-dentales-que-debes-conocer/"),
        ("todo-lo-que-debes-saber-sobre-la-cirugia-de-implantes-dentales", f"{BASE}/todo-lo-que-debes-saber-sobre-la-cirugia-de-implantes-dentales/"),
        ("que-resultados-puedes-esperar-con-los-implantes-dentales", f"{BASE}/que-resultados-puedes-esperar-con-los-implantes-dentales/"),
        ("la-revolucion-de-los-implantes-dentales-en-la-estetica-dental", f"{BASE}/la-revolucion-de-los-implantes-dentales-en-la-estetica-dental/"),
        ("implantes-dentales-y-salud-osea-lo-que-debes-saber", f"{BASE}/implantes-dentales-y-salud-osea-lo-que-debes-saber/"),
        ("ortodoncia-invisible-todo-lo-que-debes-saber-antes-de-empezar", f"{BASE}/ortodoncia-invisible-todo-lo-que-debes-saber-antes-de-empezar/"),
        ("como-la-ortodoncia-mejora-la-mordida-la-estetica-y-la-salud", f"{BASE}/como-la-ortodoncia-mejora-la-mordida-la-estetica-y-la-salud/"),
        ("beneficios-de-la-ortodoncia-en-adolescentes-mas-alla-de-la-estetica", f"{BASE}/beneficios-de-la-ortodoncia-en-adolescentes-mas-alla-de-la-estetica/"),
        ("vale-la-pena-la-ortodoncia-invisible-te-lo-contamos-todo", f"{BASE}/vale-la-pena-la-ortodoncia-invisible-te-lo-contamos-todo/"),
        ("7-cosas-que-nadie-te-cuenta-sobre-llevar-ortodoncia", f"{BASE}/7-cosas-que-nadie-te-cuenta-sobre-llevar-ortodoncia/"),
        ("sabias-que-la-ortodoncia-tambien-mejora-la-respiracion-y-el-sueno", f"{BASE}/sabias-que-la-ortodoncia-tambien-mejora-la-respiracion-y-el-sueno/"),
        ("tratamientos-de-estetica-dental-mas-innovadores-para-lograr-una-sonrisa-perfecta", f"{BASE}/tratamientos-de-estetica-dental-mas-innovadores-para-lograr-una-sonrisa-perfecta/"),
    ],
    "04-galeria": [
        ("gallery-index",       f"{BASE}/gallery/"),
        ("implantes-dentales",  f"{BASE}/gallery/implantes-dentales/"),
        ("ortodoncia-invisible",f"{BASE}/gallery/ortodoncia-invisible/"),
        ("endodoncia",          f"{BASE}/gallery/endodoncia/"),
        ("periodoncia",         f"{BASE}/gallery/periodoncia/"),
        ("brackets",            f"{BASE}/gallery/brackets/"),
        ("cirugia-oral",        f"{BASE}/gallery/cirugia-oral/"),
        ("salud-oral",          f"{BASE}/gallery/salud-oral/"),
        ("estetica-dental",     f"{BASE}/gallery/estetica-dental/"),
    ],
    "05-legal": [
        ("aviso-legal",          f"{BASE}/aviso-legal/"),
        ("politica-de-cookies",  f"{BASE}/politica-de-cookies/"),
        ("politica-de-privacidad", f"{BASE}/politica-de-privacidad/"),
    ],
}

session = requests.Session()
session.headers.update(HEADERS)

log = []


def slugify_filename(url):
    path = urlparse(url).path
    name = os.path.basename(unquote(path))
    if not name or "." not in name:
        name = hashlib.md5(url.encode()).hexdigest()[:10] + ".img"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:120]


def clean_text(soup):
    # quitar elementos no informativos
    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()
    main = (soup.find("main") or soup.find("article")
            or soup.find(id="content") or soup.find("body") or soup)
    lines = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "li", "p", "blockquote"]):
        txt = el.get_text(" ", strip=True)
        if not txt or len(txt) < 2:
            continue
        tag = el.name
        if tag == "h1":
            lines.append(f"# {txt}")
        elif tag == "h2":
            lines.append(f"## {txt}")
        elif tag == "h3":
            lines.append(f"### {txt}")
        elif tag == "h4":
            lines.append(f"#### {txt}")
        elif tag == "li":
            lines.append(f"- {txt}")
        elif tag == "blockquote":
            lines.append(f"> {txt}")
        else:
            lines.append(txt)
    # eliminar duplicados consecutivos
    out, prev = [], None
    for l in lines:
        if l != prev:
            out.append(l)
        prev = l
    return "\n\n".join(out)


def collect_images(soup, page_url):
    urls = set()
    for img in soup.find_all("img"):
        for attr in ("data-src", "data-lazy-src", "src"):
            v = img.get(attr)
            if v and not v.startswith("data:"):
                urls.add(urljoin(page_url, v))
                break
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            # coger la candidata de mayor tamano
            cands = [s.strip().split(" ")[0] for s in srcset.split(",") if s.strip()]
            if cands:
                urls.add(urljoin(page_url, cands[-1]))
    # imagenes de fondo en style inline
    for el in soup.find_all(style=True):
        m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", el["style"])
        if m and not m.group(1).startswith("data:"):
            urls.add(urljoin(page_url, m.group(1)))
    # descartar iconos/sprites comunes
    skip = ("favicon", "data:", ".svg")
    return [u for u in urls if not any(s in u.lower() for s in skip)]


def download_image(url, folder):
    try:
        r = session.get(url, timeout=30)
        if r.status_code != 200 or not r.content:
            return None
        fn = slugify_filename(url)
        path = os.path.join(folder, fn)
        # evitar colision de nombres
        if os.path.exists(path):
            base, ext = os.path.splitext(fn)
            path = os.path.join(folder, f"{base}_{hashlib.md5(url.encode()).hexdigest()[:6]}{ext}")
        with open(path, "wb") as f:
            f.write(r.content)
        return os.path.basename(path)
    except Exception as e:
        return None


def process(category, slug, url):
    folder = os.path.join(OUT, category, slug)
    os.makedirs(folder, exist_ok=True)
    try:
        r = session.get(url, timeout=40)
    except Exception as e:
        log.append(f"[ERROR] {url} -> {e}")
        return
    if r.status_code != 200:
        log.append(f"[{r.status_code}] {url}")
        return
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("title")
    title = title.get_text(strip=True) if title else slug
    meta = soup.find("meta", attrs={"name": "description"})
    meta = meta.get("content", "") if meta else ""

    text = clean_text(BeautifulSoup(r.text, "html.parser"))
    md = f"# {title}\n\nURL: {url}\n\n"
    if meta:
        md += f"**Meta descripcion:** {meta}\n\n---\n\n"
    md += text + "\n"
    with open(os.path.join(folder, "texto.md"), "w", encoding="utf-8") as f:
        f.write(md)

    imgs = collect_images(soup, url)
    n_ok = 0
    if imgs:
        img_folder = os.path.join(folder, "imagenes")
        os.makedirs(img_folder, exist_ok=True)
        for iu in imgs:
            if download_image(iu, img_folder):
                n_ok += 1
            time.sleep(0.05)
    log.append(f"[OK] {category}/{slug}: texto({len(text)} chars), {n_ok}/{len(imgs)} imgs")
    print(log[-1])


def main():
    os.makedirs(OUT, exist_ok=True)
    for category, pages in SITE.items():
        for slug, url in pages:
            process(category, slug, url)
            time.sleep(0.3)
    with open(os.path.join(OUT, "_LOG.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print("\n==== DONE ====")


if __name__ == "__main__":
    main()
