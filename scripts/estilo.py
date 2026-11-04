"""Colores y medidas de las tarjetas. Cambiar aquí cambia todas las tarjetas a la vez.

Las tarjetas son siempre oscuras (negro "Kirito") con un solo acento morado,
así se ven igual en GitHub claro y oscuro y no hay que mantener dos versiones.
"""

# Colores con nombre de uso, no de color, para poder cambiar la paleta sin buscar hex sueltos.
COLOR = {
    "fondo": "#121116",        # casi negro: el negro puro cansa y pierde la sensación de profundidad
    "superficie": "#1A1920",   # un poco más claro que el fondo para dar altura a los bloques
    "borde": "#2E2C38",
    "texto": "#E8E6EC",
    "texto_suave": "#A3A0AE",
    "acento": "#B794E0",       # morado claro: sobre negro tiene más contraste que el morado oscuro
    "acento_fondo": "#241D30", # fondo teñido de morado para chips y la píldora de estado
}

# Pares que deben cumplir WCAG AA (4.5:1). El generador los revisa antes de dibujar.
PARES_CONTRASTE = [
    ("texto", "fondo"), ("texto", "superficie"),
    ("texto_suave", "fondo"), ("texto_suave", "superficie"),
    ("acento", "fondo"), ("acento", "superficie"), ("acento", "acento_fondo"),
]

SANS = "Inter, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', Consolas, 'DejaVu Sans Mono', monospace"

# Escala fija de tamaños (px): no se inventan intermedios.
TAM = {"etiqueta": 11, "chico": 13, "cuerpo": 15, "subtitulo": 20, "titulo": 34}

ANCHO = 840     # ancho de todas las tarjetas, coincide con el ancho útil del README en GitHub
MARGEN = 32     # relleno interior, múltiplo de 4
RADIO = {"tarjeta": 12, "chip": 6, "pildora": 999}

# Ancho aproximado de un carácter monoespaciado respecto del tamaño de letra.
# Los chips van en mono justamente para poder medirlos sin cargar la fuente.
ANCHO_MONO = 0.62
