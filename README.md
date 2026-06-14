# Clínica Dental Oiasso — Sitio web

Sitio estático (HTML + CSS + JS vanilla con GSAP) para la Clínica Dental Oiasso de Irún (Gipuzkoa).
Pensado para **GitHub Pages**: todo el contenido publicable vive en la raíz del repositorio.

## Estructura

```
/                       Páginas raíz: index, clinica, equipo, primera-visita,
                        financiacion, preguntas-frecuentes, urgencias, contacto, 404
/tratamientos/          11 tratamientos + índice
/blog/                  17 artículos + índice
/casos/                 Casos reales (antes/después)
/legal/                 Aviso legal, privacidad, cookies
/assets/
  /css/                 tokens · base · components · sections · motion
  /js/main.js           Loader, nav, sliders, GSAP, microinteracciones
  /fonts/               Bricolage Grotesque + Hanken Grotesk (woff2, self-hosted)
  /img/                 brand · hero · clinica · casos
robots.txt · sitemap.xml · llms.txt · llms-full.txt · CNAME · .nojekyll

/_build/                Sistema de plantillas (NO se publica)
  partials/             head · header · footer · sprite compartidos
  pages/                Cuerpos de página con front-matter <!--META … META-->
  *.py                  Generadores de contenido + build
/contenido/             Texto e imágenes originales extraídos (fuente, para i18n)
```

## Reconstruir el sitio

```bash
python _build/make.py
```

Ejecuta los generadores (servicios, blog, legal), ensambla todas las páginas con los
partials compartidos, añade dimensiones a las imágenes (CLS) y regenera `sitemap.xml`.

## Marca

- Verde `#1a9b5c` + magenta `#e6007e` sobre blanco (colores del logo).
- Tipografía: Bricolage Grotesque (display) + Hanken Grotesk (cuerpo).
- Leitmotiv: la curva de la sonrisa del logo.

## Decisiones

- **Loader** solo en la primera visita de la sesión (`sessionStorage`).
- **Animaciones** con GSAP + ScrollTrigger; respetan `prefers-reduced-motion`
  (el contenido es visible por defecto, la animación solo realza).
- **Idiomas**: por ahora español. La arquitectura de `_build` permite generar
  `/en/`, `/fr/`, `/eu/` como páginas reales traducidas (euskara nunca por defecto).
- **SEO**: meta + Open Graph + Twitter Cards, Schema.org (Dentist, FAQPage, BlogPosting),
  geo tags, canonical, sitemap, robots con reglas para bots de IA, llms.txt.

Diseñado por [unaxaller.com](https://unaxaller.com).
