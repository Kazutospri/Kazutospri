#!/usr/bin/env bash
# Convierte una foto en data/retrato.pam: 36x48 píxeles, sin fondo.
# Se corre una sola vez por foto; generar.py lee el .pam y lo dibuja con la paleta del perfil.
# La foto original queda fuera de git (.gitignore): en el repo solo vive la versión de 36x48.
#
# Uso: scripts/preparar_retrato.sh data/foto.png [recorte]
#   recorte: rectángulo de la cara en la foto original, formato ANCHOxALTO+X+Y, proporción 3:4.
set -euo pipefail

foto="${1:?Falta la foto, por ejemplo data/foto.png}"
recorte="${2:-510x680+105+200}"
# rembg vive en el entorno de Stable Diffusion WebUI, con sus modelos ya descargados: así no se instala nada.
py="${REMBG_PYTHON:-$HOME/Proyectos/stable-diffusion-webui/venv/bin/python}"
raiz="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

"$py" - "$foto" "$tmp/sin-fondo.png" <<'EOF'
import sys
from rembg import new_session, remove
from PIL import Image
remove(Image.open(sys.argv[1]).convert("RGB"), session=new_session("isnet-general-use")).save(sys.argv[2])
EOF

# Recorte de la cara, achicado a 36x48 y alfa binario: un píxel es visible o no, como en pixel art.
magick "$tmp/sin-fondo.png" -crop "$recorte" +repage -resize 36x48! -unsharp 0x0.6+0.8+0 \
  -channel A -threshold 50% +channel "PAM:$raiz/data/retrato.pam"
echo "Listo: data/retrato.pam"
