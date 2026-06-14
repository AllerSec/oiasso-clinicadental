#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Añade width/height/decoding a <img> sin dimensiones, usando tamaños reales medidos.
   Mejora CLS sin romper el layout (los contenedores ya usan aspect-ratio)."""
import pathlib, re, json, struct

ROOT = pathlib.Path(__file__).resolve().parent.parent

def png_size(d):
    if d[:8]==b'\x89PNG\r\n\x1a\n': return struct.unpack('>II', d[16:24])
def jpg_size(d):
    i=2
    while i<len(d):
        if d[i]!=0xFF: i+=1; continue
        m=d[i+1]
        if 0xC0<=m<=0xCF and m not in (0xC4,0xC8,0xCC):
            h,w=struct.unpack('>HH', d[i+5:i+9]); return (w,h)
        i+=2+struct.unpack('>H', d[i+2:i+4])[0]

dims={}
for p in (ROOT/"assets/img").rglob("*"):
    if p.suffix.lower() not in (".png",".jpg",".jpeg"): continue
    d=p.read_bytes()
    s=png_size(d) if p.suffix.lower()==".png" else jpg_size(d)
    if s: dims["assets/img/"+p.relative_to(ROOT/"assets/img").as_posix()]=s

IMG_RE = re.compile(r'<img\b([^>]*?)>', re.I)

def fix_img(m):
    attrs=m.group(1)
    if re.search(r'\bwidth=', attrs):  # ya tiene dimensiones
        # asegurar decoding
        if 'decoding=' not in attrs:
            attrs+=' decoding="async"'
            return f'<img{attrs}>'
        return m.group(0)
    src_m=re.search(r'src="([^"]+)"', attrs)
    if not src_m: return m.group(0)
    src=src_m.group(1)
    key=re.sub(r'^(\.\./)+','',src)  # quitar prefijos relativos
    if key in dims:
        w,h=dims[key]
        extra=f' width="{w}" height="{h}"'
    else:
        extra=''
    if 'decoding=' not in attrs:
        extra+=' decoding="async"'
    return f'<img{attrs}{extra}>'

def run():
    n=0; changed=0
    htmls=[p for p in ROOT.rglob("*.html") if "_build" not in p.parts and "contenido" not in p.parts]
    for p in htmls:
        t=p.read_text(encoding="utf-8")
        nt=IMG_RE.sub(fix_img, t)
        if nt!=t:
            p.write_text(nt, encoding="utf-8"); changed+=1
        n+=1
    print(f"postprocess: {changed}/{n} HTML actualizados (img dims/decoding)")

if __name__=="__main__":
    run()
