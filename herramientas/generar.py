"""Genera los recursos del perfil de Radagora Labs en GitHub (repositorio .github de la organización).
Todo el texto se convierte en trazos con Space Grotesk (OFL), porque GitHub no carga fuentes dentro de un SVG.
Animaciones solo con CSS dentro del SVG (GitHub no ejecuta JavaScript) y respetan prefers-reduced-motion."""
import math, pathlib, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FUENTES = pathlib.Path(sys.argv[1])
SALIDA = pathlib.Path(sys.argv[2]); SALIDA.mkdir(parents=True, exist_ok=True)
AMB, AZUL, ROJO, VIOLETA = "#E8A33D", "#4A86E8", "#E5484D", "#C084FC"
TEMAS = {"oscuro": dict(fondo="#111214", tinta="#F3F1EC", suave="#A7A39A", linea="#2A2B2F", panel="#17181B"),
         "claro": dict(fondo="#F6F4EF", tinta="#16171A", suave="#5F5B53", linea="#DEDAD1", panel="#FFFFFF")}
_fuentes = {}

def _fuente(peso):
    if peso not in _fuentes:
        f = TTFont(FUENTES / f"SpaceGrotesk-{peso}.ttf")
        _fuentes[peso] = (f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm, f.get("kern"))
    return _fuentes[peso]

def ancho(t, tam, peso=500, espacio=0):
    gs, cmap, hmtx, upm, _ = _fuente(peso)
    return sum(hmtx[cmap.get(ord(c), "space")][0] for c in t) * tam / upm + espacio * max(len(t) - 1, 0)

def texto(t, x, y, tam, peso=500, color="#000", ancla="start", espacio=0, extra=""):
    """Texto -> <path>. y es la línea base."""
    gs, cmap, hmtx, upm, _ = _fuente(peso)
    w = ancho(t, tam, peso, espacio)
    x0 = x - (w if ancla == "end" else w / 2 if ancla == "middle" else 0)
    esc = tam / upm
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cx = 0.0
    for c in t:
        g = cmap.get(ord(c), "space")
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x0 + cx, y)))
        cx += hmtx[g][0] * esc + espacio
    return f'<path d="{pen.getCommands()}" fill="{color}"{extra}/>'

def pt(cx, cy, r, d):
    return cx + r * math.cos(math.radians(d)), cy + r * math.sin(math.radians(d))

def lupa(cx, cy, s, tinta, clase_barrido=""):
    """Lupa con barrido y las tres señales (la 'o' del logotipo). s = escala respecto del original."""
    x1, y1 = pt(cx, cy, 11 * s, -90); x2, y2 = pt(cx, cy, 11 * s, -15)
    puntos = "".join(f'<circle cx="{pt(cx, cy, 7.5*s, d)[0]:.2f}" cy="{pt(cx, cy, 7.5*s, d)[1]:.2f}" r="{2.5*s:.2f}" fill="{c}"/>'
                     for d, c in [(210, AZUL), (330, ROJO), (90, VIOLETA)])
    return (f'<circle cx="{cx}" cy="{cy}" r="{18.5*s:.2f}" fill="none" stroke="{tinta}" stroke-width="{8.5*s:.2f}"/>'
            f'<g class="{clase_barrido}" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy} L{x1:.2f} {y1:.2f} A{11*s:.2f} {11*s:.2f} 0 0 1 {x2:.2f} {y2:.2f} Z" fill="{AMB}" fill-opacity="0.5"/></g>'
            f'{puntos}<circle cx="{cx}" cy="{cy}" r="{1.9*s:.2f}" fill="{AMB}"/>'
            f'<line x1="{cx+14*s:.2f}" y1="{cy+14*s:.2f}" x2="{cx+29*s:.2f}" y2="{cy+29*s:.2f}" stroke="{AMB}" stroke-width="{8*s:.2f}" stroke-linecap="round"/>')

def logotipo(x_o, base, s, tinta, barrido=""):
    """radag◉ra: la lupa ocupa la 'o'. x_o = centro de la lupa; base = línea base del texto."""
    tam = 84 * s
    cy = base - 20 * s
    return (texto("radag", x_o - 27 * s, base, tam, 600, tinta, "end", -2 * s)
            + texto("ra", x_o + 27 * s, base, tam, 600, tinta, "start", -2 * s)
            + lupa(x_o, cy, s, tinta, barrido))

def logotipo_izq(x, base, s, tinta, barrido=""):
    """Logotipo alineado a la izquierda en x (para que coincida con el texto de abajo)."""
    return logotipo(x + ancho("radag", 84 * s, 600, -2 * s) + 27 * s, base, s, tinta, barrido)

def simbolo(cx, cy, r, tinta, encendida=None, barrido=""):
    """Símbolo de la marca: anillo, barrido, tres señales y mango."""
    s = r / 30
    x1, y1 = pt(cx, cy, 24 * s, -90); x2, y2 = pt(cx, cy, 24 * s, -20)
    b = [f'<circle cx="{cx}" cy="{cy}" r="{30*s:.2f}" fill="none" stroke="{tinta}" stroke-width="{8*s:.2f}"/>',
         f'<g class="{barrido}" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy} L{x1:.2f} {y1:.2f} A{24*s:.2f} {24*s:.2f} 0 0 1 {x2:.2f} {y2:.2f} Z" fill="{AMB}" fill-opacity="0.4"/></g>']
    for d, c, k in [(210, AZUL, "nav"), (330, ROJO, "ves"), (90, VIOLETA, "noc")]:
        x, y = pt(cx, cy, 14 * s, d)
        op = "" if encendida in (None, k) else ' fill-opacity="0.22"'
        b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{5.2*s:.2f}" fill="{c}"{op}/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{3.5*s:.2f}" fill="{AMB}"/>'
             f'<line x1="{cx+22*s:.2f}" y1="{cy+22*s:.2f}" x2="{cx+45*s:.2f}" y2="{cy+45*s:.2f}" stroke="{AMB}" stroke-width="{10*s:.2f}" stroke-linecap="round"/>')
    return "".join(b)

CSS = """<style>
@keyframes giro{to{transform:rotate(360deg)}}
.giro{animation:giro 6s linear infinite}
.giro-rapido{animation:giro 4s linear infinite}
@keyframes eco{0%,8%{opacity:1;transform:scale(1)}40%{opacity:.25;transform:scale(1)}100%{opacity:.25}}
.eco{transform-box:fill-box;transform-origin:center;animation:eco 6s ease-out infinite}
@keyframes onda{0%{transform:scale(.4);opacity:.7}100%{transform:scale(2.6);opacity:0}}
.onda{transform-box:fill-box;transform-origin:center;animation:onda 6s ease-out infinite}
@keyframes entrar{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.entrar{animation:entrar .9s ease-out both}
@keyframes brillo{0%{transform:translateX(-30%)}100%{transform:translateX(130%)}}
.brillo{animation:brillo 3.8s ease-in-out infinite}
@keyframes latido{0%,100%{opacity:1}50%{opacity:.3}}
.latido{animation:latido 2s ease-in-out infinite}
@keyframes cursor{0%,49%{opacity:1}50%,100%{opacity:0}}
.cursor{animation:cursor 1.1s steps(1) infinite}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
</style>"""

def svg(w, h, cuerpo, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{titulo}">'
            f'<title>{titulo}</title>{CSS}{cuerpo}</svg>')

def banner(t):
    T = TEMAS[t]; W, H = 1200, 420
    rcx, rcy = 960, 210
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{T["fondo"]}"/>',
         f'<defs><pattern id="p" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{T["suave"]}" fill-opacity="0.18"/></pattern>'
         f'<linearGradient id="haz" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMB}" stop-opacity="0"/><stop offset="1" stop-color="{AMB}" stop-opacity="0.38"/></linearGradient>'
         f'<radialGradient id="vineta" cx="0.8" cy="0.5" r="0.7"><stop offset="0" stop-color="{AMB}" stop-opacity="0.08"/><stop offset="1" stop-color="{AMB}" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="marco"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>',
         f'<g clip-path="url(#marco)"><rect width="{W}" height="{H}" fill="url(#p)"/><rect width="{W}" height="{H}" fill="url(#vineta)"/>']
    for r in (60, 120, 180, 240, 300):
        b.append(f'<circle cx="{rcx}" cy="{rcy}" r="{r}" fill="none" stroke="{AMB}" stroke-opacity="{0.35 if r < 200 else 0.2}" stroke-width="1"/>')
    b.append(f'<line x1="{rcx-300}" y1="{rcy}" x2="{rcx+300}" y2="{rcy}" stroke="{AMB}" stroke-opacity="0.15"/>'
             f'<line x1="{rcx}" y1="{rcy-300}" x2="{rcx}" y2="{rcy+300}" stroke="{AMB}" stroke-opacity="0.15"/>')
    x1, y1 = pt(rcx, rcy, 300, -55)
    b.append(f'<g class="giro" style="transform-origin:{rcx}px {rcy}px"><path d="M{rcx} {rcy} L{x1:.1f} {y1:.1f} A300 300 0 0 1 {rcx+300} {rcy} Z" fill="url(#haz)"/>'
             f'<line x1="{rcx}" y1="{rcy}" x2="{rcx+300}" y2="{rcy}" stroke="{AMB}" stroke-opacity="0.8" stroke-width="1.5"/></g>')
    # ecos: cada señal se ilumina cuando pasa el barrido (6 s por vuelta; ángulo 0 = derecha, sentido horario)
    for ang, r, col in [(35, 150, AZUL), (150, 205, ROJO), (260, 110, VIOLETA), (310, 235, AMB)]:
        x, y = pt(rcx, rcy, r, ang)
        demora = f"{ang/360*6:.2f}s"
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{col}" stroke-width="1.5" class="onda" style="animation-delay:{demora}"/>'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{col}" class="eco" style="animation-delay:{demora}"/>')
    b.append('</g>')
    b.append(f'<g class="entrar">{logotipo_izq(68, 170, 1.18, T["tinta"], "giro-rapido")}</g>')
    b.append(f'<g class="entrar" style="animation-delay:.25s">{texto("LABS", 74, 214, 22, 600, AMB, espacio=9)}</g>')
    b.append(f'<g class="entrar" style="animation-delay:.45s">'
             + texto("Herramientas para investigar incidentes,", 72, 282, 30, 500, T["tinta"])
             + texto("hechas por quienes los atienden.", 72, 322, 30, 500, T["tinta"])
             + f'<rect x="{72 + ancho("hechas por quienes los atienden.", 30, 500) + 6:.0f}" y="298" width="3" height="30" fill="{AMB}" class="cursor"/></g>')
    fichas = ["Local primero", "Sin telemetría", "Gratis para la comunidad"]
    x = 72
    piezas = []
    for f_ in fichas:
        w = ancho(f_, 15, 500) + 30
        piezas.append(f'<rect x="{x}" y="350" width="{w:.0f}" height="32" rx="16" fill="none" stroke="{T["linea"] if t == "claro" else "#3A3B40"}"/>'
                      + texto(f_, x + 15, 371, 15, 500, T["suave"]))
        x += w + 10
    b.append(f'<g class="entrar" style="animation-delay:.65s">{"".join(piezas)}</g>')
    return svg(W, H, "".join(b), "Radagora Labs: herramientas para investigar incidentes")

HERRAMIENTAS = [
    ("nav", "Navestigio", AZUL, ["Forense de navegadores: historial,", "descargas y sesiones en una sola", "línea de tiempo."], "Disponible · gratis"),
    ("ves", "Vestigador", ROJO, ["Análisis de indicadores: varias", "fuentes de inteligencia en una", "sola consulta."], "Próximamente"),
    ("noc", "Noctyra", VIOLETA, ["Respuesta a incidentes guiada:", "de la alerta al plan de acción,", "en tu propio equipo."], "En desarrollo"),
]

def tarjeta(t, clave, nombre, color, lineas, estado):
    T = TEMAS[t]; W, H = 400, 250
    b = [f'<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
         f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity="0"/><stop offset=".5" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>',
         f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{T["panel"]}"/>'
         f'<rect width="{W}" height="4" fill="{color}" fill-opacity="0.35"/><rect class="brillo" x="-160" width="160" height="4" fill="url(#g)"/></g>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{T["linea"] if t == "claro" else "#2E2F34"}"/>',
         f'<circle cx="58" cy="62" r="32" fill="{color}" fill-opacity="0.08"/>',
         simbolo(56, 60, 21, T["tinta"], clave, "giro-rapido"),
         texto(nombre, 104, 72, 32, 600, T["tinta"], espacio=-0.5)]
    for i, l in enumerate(lineas):
        b.append(texto(l, 32, 130 + i * 25, 17, 400, T["suave"]))
    w = ancho(estado, 14, 500) + 42
    b.append(f'<rect x="32" y="{H-50}" width="{w:.0f}" height="28" rx="14" fill="{color}" fill-opacity="0.12"/>'
             f'<circle cx="49" cy="{H-36}" r="4.5" fill="{color}" class="latido"/>'
             + texto(estado, 61, H - 31, 14, 500, color))
    return svg(W, H, "".join(b), f"{nombre}: {' '.join(lineas)} {estado}")

def divisor(t):
    T = TEMAS[t]; W, H = 1200, 30
    b = (f'<defs><linearGradient id="d" x1="0" x2="1"><stop offset="0" stop-color="{AMB}" stop-opacity="0"/><stop offset=".5" stop-color="{AMB}"/><stop offset="1" stop-color="{AMB}" stop-opacity="0"/></linearGradient></defs>'
         f'<line x1="0" y1="15" x2="{W}" y2="15" stroke="{T["linea"] if t == "claro" else "#2E2F34"}" stroke-width="1.5"/>'
         f'<rect class="brillo" x="-300" y="14" width="300" height="2.5" fill="url(#d)"/>'
         + "".join(f'<circle cx="{x}" cy="15" r="4" fill="{c}"/>' for x, c in [(584, AZUL), (600, ROJO), (616, VIOLETA)]))
    return svg(W, H, b, "")

def avatar():
    W = 500
    b = (f'<rect width="{W}" height="{W}" fill="#111214"/>'
         + "".join(f'<circle cx="222" cy="222" r="{r}" fill="none" stroke="{AMB}" stroke-opacity="0.18"/>' for r in (150, 200))
         + simbolo(222, 222, 110, "#F3F1EC"))
    return svg(W, W, b, "Radagora Labs")

def social():
    W, H = 1280, 640
    T = TEMAS["oscuro"]
    b = (f'<rect width="{W}" height="{H}" fill="{T["fondo"]}"/>'
         + "".join(f'<circle cx="1040" cy="320" r="{r}" fill="none" stroke="{AMB}" stroke-opacity="0.2"/>' for r in (80, 160, 240, 320))
         + "".join(f'<circle cx="{pt(1040,320,r,a)[0]:.0f}" cy="{pt(1040,320,r,a)[1]:.0f}" r="8" fill="{c}"/>' for a, r, c in [(35,170,AZUL),(200,210,ROJO),(260,120,VIOLETA)])
         + logotipo_izq(92, 300, 1.45, T["tinta"])
         + texto("LABS", 96, 352, 26, 600, AMB, espacio=10)
         + texto("Herramientas para investigar incidentes", 96, 450, 38, 500, T["tinta"])
         + texto("Navestigio · Vestigador · Noctyra", 96, 500, 28, 400, T["suave"]))
    return svg(W, H, b, "Radagora Labs")

for t in TEMAS:
    (SALIDA / f"banner-{t}.svg").write_text(banner(t), encoding="utf-8")
    (SALIDA / f"divisor-{t}.svg").write_text(divisor(t), encoding="utf-8")
    for clave, nombre, color, lineas, estado in HERRAMIENTAS:
        (SALIDA / f"{nombre.lower()}-{t}.svg").write_text(tarjeta(t, clave, nombre, color, lineas, estado), encoding="utf-8")
(SALIDA / "_avatar.svg").write_text(avatar(), encoding="utf-8")
(SALIDA / "_social.svg").write_text(social(), encoding="utf-8")
print("\n".join(sorted(p.name + f"  {p.stat().st_size//1024} KB" for p in SALIDA.iterdir())))
