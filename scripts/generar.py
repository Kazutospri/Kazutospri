"""Genera las tarjetas SVG y el README del perfil a partir de data/perfil.json.

Uso: python3 scripts/generar.py
Solo usa la biblioteca estándar de Python, para que corra en cualquier equipo sin instalar nada.
"""

import json
import sys
from html import escape
from pathlib import Path

from estilo import (ANCHO, ANCHO_MONO, COLOR, MARGEN, MONO, PARES_CONTRASTE, RADIO, RETRATO,
                    RETRATO_ESCALA, SANS, TAM)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"

# Columna donde empiezan los valores en las filas "etiqueta · valor".
COL_VALOR = 168
# Ancho medio de un carácter de Inter respecto del tamaño; algo holgado para no cortar texto.
ANCHO_SANS = 0.56


# ---------- Contraste ----------

def _luminancia(hex_color):
    canales = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2]


def contraste(a, b):
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def revisar_contraste():
    """Se niega a generar si algún par de colores queda bajo AA: mejor fallar que publicar texto ilegible."""
    fallas = []
    for texto, fondo in PARES_CONTRASTE:
        valor = contraste(COLOR[texto], COLOR[fondo])
        if valor < 4.5:
            fallas.append(f"{texto} sobre {fondo}: {valor:.2f}:1")
    if fallas:
        sys.exit("Contraste insuficiente (mínimo 4.5:1):\n  " + "\n  ".join(fallas))


# ---------- Piezas de dibujo ----------

def ancho_mono(texto, tam):
    return len(texto) * tam * ANCHO_MONO


def partir(texto, tam, ancho):
    """Corta un texto en líneas que quepan en `ancho`, estimando el ancho por carácter."""
    max_chars = max(1, int(ancho / (tam * ANCHO_SANS)))
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if len(prueba) <= max_chars:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def texto(x, y, contenido, tam, color="texto", peso=400, familia=SANS, espaciado=0):
    extra = f' letter-spacing="{espaciado}"' if espaciado else ""
    return (f'<text x="{x}" y="{y}" font-family="{familia}" font-size="{tam}" '
            f'font-weight="{peso}" fill="{COLOR[color]}"{extra}>{escape(contenido)}</text>')


def etiqueta(x, y, contenido, color="texto_suave"):
    # Mayúsculas siempre con espaciado (0.08em) para que no se lean apretadas.
    return texto(x, y, contenido.upper(), TAM["etiqueta"], color, 600, MONO, round(TAM["etiqueta"] * 0.08, 2))


def chip(x, y, contenido):
    """Devuelve el SVG del chip y su ancho, para poder poner el siguiente a continuación."""
    tam, alto, relleno = TAM["chico"], 26, 10
    ancho = ancho_mono(contenido, tam) + 2 * relleno
    svg = (f'<rect x="{x}" y="{y}" width="{ancho:.0f}" height="{alto}" rx="{RADIO["chip"]}" '
           f'fill="{COLOR["superficie"]}" stroke="{COLOR["borde"]}"/>'
           + texto(x + relleno, y + 17.5, contenido, tam, "texto", 500, MONO))
    return svg, ancho


def fila_chips(x, y, items, ancho_max):
    """Pone chips en fila y salta de línea si no caben. Devuelve SVG y alto ocupado."""
    partes, cx, cy = [], x, y
    for item in items:
        _, ancho = chip(0, 0, item)
        if cx + ancho > x + ancho_max and cx > x:
            cx, cy = x, cy + 34
        svg, ancho = chip(cx, cy, item)
        partes.append(svg)
        cx += ancho + 8
    return "".join(partes), cy - y + 26


def pildora(x, y, contenido):
    tam, alto, relleno = TAM["etiqueta"], 22, 10
    ancho = ancho_mono(contenido.upper(), tam) + len(contenido) * tam * 0.08 + 2 * relleno
    return (f'<rect x="{x}" y="{y}" width="{ancho:.0f}" height="{alto}" rx="{alto / 2}" '
            f'fill="{COLOR["acento_fondo"]}"/>'
            + etiqueta(x + relleno, y + 15, contenido, "acento"))


def tarjeta(alto, cuerpo, titulo, descripcion):
    """Marco común: mismo fondo, borde y radio en todas, y título accesible para lectores de pantalla."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{alto}" '
            f'viewBox="0 0 {ANCHO} {alto}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(titulo)}</title><desc id="d">{escape(descripcion)}</desc>'
            f'<rect x="0.5" y="0.5" width="{ANCHO - 1}" height="{alto - 1}" rx="{RADIO["tarjeta"]}" '
            f'fill="{COLOR["fondo"]}" stroke="{COLOR["borde"]}"/>{cuerpo}</svg>\n')


# ---------- Tarjetas ----------

def espadas(cx, cy, escala=1.0):
    """Dos espadas cruzadas en línea fina: guiño a Kirito, decorativo y discreto."""
    partes = []
    for direccion, color, opacidad in ((1, "acento", 1), (-1, "texto_suave", 0.6)):
        d = direccion
        # Punta arriba; la hoja termina en la guarda (a 30 px del centro hacia abajo).
        punta = (cx + 50 * d, cy - 50)
        guarda = (cx - 30 * d, cy + 30)
        pomo = (cx - 46 * d, cy + 46)
        # La guarda va perpendicular a la hoja; la empuñadura es más gruesa que la hoja.
        partes.append(
            f'<g stroke="{COLOR[color]}" stroke-opacity="{opacidad}" stroke-linecap="round" fill="none">'
            f'<line x1="{guarda[0]}" y1="{guarda[1]}" x2="{punta[0]}" y2="{punta[1]}" stroke-width="2"/>'
            f'<line x1="{guarda[0] - 11}" y1="{guarda[1] - 11 * d}" x2="{guarda[0] + 11}" '
            f'y2="{guarda[1] + 11 * d}" stroke-width="2"/>'
            f'<line x1="{guarda[0]}" y1="{guarda[1]}" x2="{pomo[0]}" y2="{pomo[1]}" stroke-width="4"/>'
            f'<circle cx="{pomo[0]}" cy="{pomo[1]}" r="2.5" fill="{COLOR[color]}" fill-opacity="{opacidad}"/></g>')
    zoom = f'translate({cx} {cy}) scale({escala}) translate({-cx} {-cy})'
    return f'<g aria-hidden="true" transform="{zoom}">{"".join(partes)}</g>'


def leer_pam(ruta):
    """Lee un PAM RGB_ALPHA (formato simple de imagen) sin librerías externas."""
    datos = ruta.read_bytes()
    cabecera, pixeles = datos.split(b"ENDHDR\n", 1)
    campos = dict(linea.split(" ", 1) for linea in cabecera.decode().splitlines()[1:] if " " in linea)
    ancho, alto = int(campos["WIDTH"]), int(campos["HEIGHT"])
    if campos.get("TUPLTYPE") != "RGB_ALPHA":
        sys.exit(f"{ruta} debe ser RGB_ALPHA; vuelve a correr scripts/preparar_retrato.sh")
    filas = []
    for y in range(alto):
        fila = []
        for x in range(ancho):
            r, g, b, a = pixeles[(y * ancho + x) * 4:(y * ancho + x) * 4 + 4]
            fila.append(None if a < 128 else 0.2126 * r + 0.7152 * g + 0.0722 * b)
        filas.append(fila)
    return filas


def retrato(ruta, x0, y0):
    """Dibuja el retrato en duotono: cada luminosidad se lleva a uno de los tonos de RETRATO."""
    filas = leer_pam(ruta)
    visibles = sorted(v for fila in filas for v in fila if v is not None)
    # Se estira entre los percentiles 3 y 90: la polera blanca se satura al tono más claro
    # y así la cara aprovecha toda la escala (si no, los rasgos se pierden en dos tonos).
    bajo, alto = visibles[len(visibles) * 3 // 100], visibles[len(visibles) * 90 // 100]
    niveles = len(RETRATO)
    s = RETRATO_ESCALA
    partes = []
    for y, fila in enumerate(filas):
        x = 0
        while x < len(fila):
            if fila[x] is None:
                x += 1
                continue
            t = min(1.0, max(0.0, (fila[x] - bajo) / max(1.0, alto - bajo)))
            nivel = min(niveles - 1, int(t * niveles))
            # Junta píxeles seguidos del mismo tono en un solo rectángulo: el SVG pesa mucho menos.
            fin = x + 1
            while fin < len(fila) and fila[fin] is not None and min(niveles - 1, int(min(1.0, max(0.0, (fila[fin] - bajo) / max(1.0, alto - bajo))) * niveles)) == nivel:
                fin += 1
            partes.append(f'<rect x="{x0 + x * s}" y="{y0 + y * s}" width="{(fin - x) * s}" height="{s}" fill="{RETRATO[nivel]}"/>')
            x = fin
    ancho = len(filas[0]) * s
    return f'<g aria-hidden="true" shape-rendering="crispEdges">{"".join(partes)}</g>', ancho


def tarjeta_encabezado(p):
    ruta_retrato = RAIZ / "data" / "retrato.pam"
    if ruta_retrato.exists():
        # Con retrato: foto a la izquierda, texto alineado con la columna de valores de las otras tarjetas.
        alto, y_retrato = 192, 24
        svg_retrato, ancho_retrato = retrato(ruta_retrato, MARGEN, y_retrato)
        x_texto, y_base, cuerpo = MARGEN + ancho_retrato + 28, 64, [svg_retrato]
        espadas_svg = espadas(ANCHO - MARGEN - 44, alto / 2, 0.7)
        ancho_texto = ANCHO - x_texto - MARGEN - 100
    else:
        # Sin retrato: el encabezado de siempre, para que el script no falle si no hay foto.
        alto, x_texto, y_base, cuerpo = 176, MARGEN, 52, []
        espadas_svg = espadas(ANCHO - MARGEN - 64, alto / 2)
        ancho_texto = ANCHO - 2 * MARGEN - 140
    cuerpo += [etiqueta(x_texto, y_base, f'{p["rol"]} · {p["lugar"]}', "acento"),
               texto(x_texto, y_base + 46, p["nombre"], TAM["titulo"], "texto", 700, espaciado=-0.6)]
    for i, linea in enumerate(partir(p["lema"], TAM["cuerpo"], ancho_texto)):
        cuerpo.append(texto(x_texto, y_base + 80 + i * 22, linea, TAM["cuerpo"], "texto_suave"))
    cuerpo.append(espadas_svg)
    return tarjeta(alto, "".join(cuerpo), p["nombre"], f'{p["rol"]} en {p["lugar"]}. {p["lema"]}')


def tarjeta_experiencia(e):
    ancho_valor = ANCHO - COL_VALOR - MARGEN
    cuerpo = [etiqueta(MARGEN, 48, e["organizacion"], "acento"),
              texto(MARGEN, 82, e["proyecto"], TAM["subtitulo"], "texto", 700),
              texto(MARGEN, 110, e["resumen"], TAM["cuerpo"], "texto_suave")]
    y = 134
    cuerpo.append(f'<line x1="{MARGEN}" y1="{y}" x2="{ANCHO - MARGEN}" y2="{y}" stroke="{COLOR["borde"]}"/>')
    y += 32
    for nombre, valor in e["detalles"]:
        lineas = partir(valor, TAM["cuerpo"], ancho_valor)
        cuerpo.append(etiqueta(MARGEN, y, nombre))
        for i, linea in enumerate(lineas):
            cuerpo.append(texto(COL_VALOR, y + i * 22, linea, TAM["cuerpo"]))
        y += 22 * len(lineas) + 14
    y += 6
    cuerpo.append(texto(MARGEN, y, e["nota"], TAM["chico"], "texto_suave"))
    alto = y + MARGEN - 4
    desc = f'{e["proyecto"]}, {e["organizacion"]}. ' + " ".join(f"{n}: {v}." for n, v in e["detalles"])
    return tarjeta(alto, "".join(cuerpo), e["proyecto"], desc)


def tarjeta_en_desarrollo(d):
    cuerpo = [texto(MARGEN, 56, d["proyecto"], TAM["subtitulo"], "texto", 700)]
    ancho_titulo = len(d["proyecto"]) * TAM["subtitulo"] * 0.68
    cuerpo.append(pildora(MARGEN + ancho_titulo + 16, 39, d["estado"]))
    y = 88
    for linea in partir(d["resumen"], TAM["cuerpo"], ANCHO - 2 * MARGEN):
        cuerpo.append(texto(MARGEN, y, linea, TAM["cuerpo"], "texto_suave"))
        y += 22
    chips, alto_chips = fila_chips(MARGEN, y, d["stack"], ANCHO - 2 * MARGEN)
    cuerpo.append(chips)
    alto = y + alto_chips + MARGEN
    desc = f'{d["proyecto"]} ({d["estado"]}). {d["resumen"]} Stack: {", ".join(d["stack"])}.'
    return tarjeta(alto, "".join(cuerpo), d["proyecto"], desc)


def tarjeta_stack(stack):
    cuerpo, y = [], MARGEN
    for area, items in stack:
        chips, alto_chips = fila_chips(COL_VALOR, y, items, ANCHO - COL_VALOR - MARGEN)
        cuerpo.append(etiqueta(MARGEN, y + 17, area))
        cuerpo.append(chips)
        y += alto_chips + 14
    alto = y - 14 + MARGEN
    desc = " ".join(f'{area}: {", ".join(items)}.' for area, items in stack)
    return tarjeta(alto, "".join(cuerpo), "Stack", desc)


# ---------- README ----------

def img(archivo, alt):
    return f'<img src="assets/{archivo}" width="100%" alt="{escape(alt)}">'


def readme(p, archivos):
    """Los títulos van en texto real (navegables y buscables); las tarjetas son el apoyo visual."""
    partes = [img("encabezado.svg", f'{p["nombre"]}, {p["rol"].lower()} en {p["lugar"]}. {p["lema"]}'), ""]
    partes += ["## Experiencia", ""]
    for archivo, e in archivos["experiencia"]:
        partes += [img(archivo, f'{e["proyecto"]}, {e["organizacion"]}. {e["resumen"]}'), ""]
    if archivos["en_desarrollo"]:
        partes += ["## En desarrollo", ""]
        for archivo, d in archivos["en_desarrollo"]:
            partes += [img(archivo, f'{d["proyecto"]} ({d["estado"].lower()}): {d["resumen"]}'), ""]
    partes += ["## Stack", "", img("stack.svg", "Stack: " + " ".join(
        f'{area}: {", ".join(items)}.' for area, items in p["stack"])), ""]
    partes += ["<sub>Las tarjetas se generan con <a href=\"scripts/generar.py\">scripts/generar.py</a> "
               "desde <a href=\"data/perfil.json\">data/perfil.json</a>.</sub>", ""]
    return "\n".join(partes)


def main():
    revisar_contraste()
    p = json.loads((RAIZ / "data" / "perfil.json").read_text(encoding="utf-8"))
    ASSETS.mkdir(exist_ok=True)
    # Se borran las tarjetas viejas para que no queden huérfanas si se quita un proyecto.
    for viejo in ASSETS.glob("*.svg"):
        viejo.unlink()

    salida = {"encabezado.svg": tarjeta_encabezado(p), "stack.svg": tarjeta_stack(p["stack"])}
    archivos = {"experiencia": [], "en_desarrollo": []}
    for clave, dibujar in (("experiencia", tarjeta_experiencia), ("en_desarrollo", tarjeta_en_desarrollo)):
        for i, item in enumerate(p.get(clave, []), start=1):
            nombre = f'{clave.replace("_", "-")}-{i}.svg'
            salida[nombre] = dibujar(item)
            archivos[clave].append((nombre, item))

    for nombre, svg in salida.items():
        (ASSETS / nombre).write_text(svg, encoding="utf-8")
    (RAIZ / "README.md").write_text(readme(p, archivos), encoding="utf-8")
    print(f"Listo: {len(salida)} tarjetas en assets/ y README.md")


if __name__ == "__main__":
    main()
