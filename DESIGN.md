# Design

## Theme
Clínica dental cálida y luminosa. Escena: una sala de espera bañada de luz natural a media mañana — blanco limpio, verde menta vivo y un latido magenta que humaniza. Light theme siempre (la salud se asocia a luz y limpieza; el dark mode leería como frío/quirúrgico). El motivo recurrente es la **curva de la sonrisa** del logo: aparece como arcos, máscaras clip-path y trazos SVG animados.

Estrategia de color: **Committed** — el verde de marca carga heros, footer y bloques de sección; el magenta es el acento de acción (CTAs, subrayados, números). Blanco/hueso como respiro.

## Color
Identidad ya comprometida en el logo (verde + magenta). Se preserva. Tokens en OKLCH.

- `--brand-green`: `#1a9b5c` ≈ `oklch(0.62 0.15 155)` — verde principal (logo "clínica dental", fondos de sección, footer).
- `--brand-green-deep`: `oklch(0.48 0.13 156)` — verde oscuro para texto sobre claro y hovers (contraste AA).
- `--brand-green-ink`: `oklch(0.30 0.07 157)` — verde casi-tinta para titulares sobre fondo claro.
- `--brand-magenta`: `#e6007e` ≈ `oklch(0.60 0.25 354)` — acento de acción, CTAs, números, subrayados.
- `--brand-magenta-deep`: `oklch(0.50 0.22 354)` — hover de CTA, texto magenta sobre claro (AA).
- `--ink`: `oklch(0.24 0.02 160)` — cuerpo de texto (verde-tinta muy oscuro, no negro puro).
- `--bg`: `oklch(0.99 0.004 150)` — blanco con micro-tinte verde (off-white, chroma hacia la marca, no calidez por defecto).
- `--surface`: `oklch(0.97 0.008 155)` — menta-niebla para tarjetas/secciones alternas.
- `--surface-mint`: `oklch(0.95 0.03 158)` — menta suave para bloques destacados.
- `--muted`: `oklch(0.45 0.02 160)` — texto secundario (cumple 4.5:1 sobre bg).
- `--line`: `oklch(0.90 0.01 155)` — bordes/divisores.
- Gradiente de marca (decorativo, NUNCA en texto): verde→magenta solo en trazos/auras puntuales.

## Typography
Self-hosted (woff2 en `/assets/fonts`). Eje de contraste display humanista + body neutral.

- **Display / titulares**: `Bricolage Grotesque` (variable, 400–800). Carácter cálido y contemporáneo, no genérico. `letter-spacing: -0.03em` en display, `text-wrap: balance`.
- **Cuerpo / UI**: `Hanken Grotesk` (400/500/600/700). Altísima legibilidad a tamaño pequeño para público de edad amplia. `text-wrap: pretty` en prosa, line-height 1.65, medida 65–72ch.
- Escala modular fluida con `clamp()`, ratio ≥1.25. Hero h1 max ~5.5rem (techo 6rem). Floor letter-spacing display −0.04em.
- Números de pasos/estadísticas en Bricolage 700 magenta.

## Motion
GSAP (core + ScrollTrigger + SplitText cuando aporte). Ease-out exponencial (`expo`/`quart`), sin bounce. `autoAlpha` en reveals. Timelines, no delays encadenados. Cleanup con `gsap.context()`/`ScrollTrigger.kill()`.
- **Page loader**: solo primera visita (sessionStorage flag). Trazo SVG de la curva-sonrisa dibujándose.
- **Hero**: animación playful de fondo (curvas de sonrisa SVG en parallax + partículas suaves / canvas), reveal coreografiado del titular con SplitText.
- **Scroll**: reveals por sección adaptados al contenido (stagger en grids, draw-SVG en iconos de tratamiento, contadores en estadísticas, pin en "Tu primera visita").
- **Microinteracciones**: botones que se transforman (la curva sonríe), tooltips, hover magnético en CTAs, cursor-react en hero.
- `@media (prefers-reduced-motion: reduce)`: todo a crossfade/instantáneo, sin parallax ni loader animado.

## Components
- **Nav** sticky con logo, menú (Inicio / Tratamientos / Sedación consciente / Casos / Blog / Contacto), selector de idioma, CTA "Pedir cita". Menú móvil accesible (dialog/overlay).
- **Treatment card**: imagen + icono SVG animado (draw-on-scroll) + título + extracto + "Ver tratamiento". Grid `auto-fit minmax` SIN filas huérfanas (recuento de items siempre par/completo; rellenar o reequilibrar).
- **Before/After slider**: comparador arrastrable para casos reales (antes/después).
- **Step timeline** ("Tu primera visita" 01–04): secuencia numerada real (aquí los números SÍ son información, es un flujo ordenado).
- **Testimonial carousel**: GSAP/embla, testimonios reales con nombre.
- **FAQ accordion** con FAQ schema.
- **Stat band**: 30 años · 6 gabinetes · 100% edades — contadores animados.
- **Footer** verde: horario, dirección, contacto, mapa, enlaces legales. Copyright → **unaxaller.com** (enlace).
- **404** personalizada (diente "perdido", redirección a inicio).

## Layout
- Contenedores simétricos, max-width ~1200–1280px, gutters fluidos `clamp()`.
- Grids equilibrados, prohibidas las filas huérfanas (orphaned last row) en cualquier sección. En móvil: "Ver más" en lugar de saturar.
- 6 imágenes mínimo por página; heros con imagen/vídeo de fondo.
- Páginas separadas reales por idioma (`/`, `/en/`, `/eu/`, `/fr/` — euskara nunca por defecto). Empezar solo ES; resto tras validación.
- Estructura en raíz del repo para GitHub Pages.
