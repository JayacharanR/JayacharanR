"""Build the repository-hosted stack grid and contact badges."""
from io import BytesIO
from math import ceil
from pathlib import Path
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

TOOLS = Path(__file__).resolve().parent
ICONS = TOOLS / 'stack-icons'
ASSETS = TOOLS.parent / 'assets'
STACK = (
    'python', 'rust', 'typescript', 'pytorch', 'onnx', 'opencv', 'nextdotjs',
    'nodedotjs', 'tailwindcss', 'langfuse', 'docker', 'kubernetes', 'aws', 'azure', 'postgresql',
    'redis', 'sqlite', 'neo4j', 'linux', 'git', 'githubactions', 'ffmpeg',
)
BADGES = (
    ('LangChain', 'langchain', '#1d393a', '#f0f7f4'),
    ('LangGraph', 'langgraph', '#203a39', '#f0f7f4'),
    ('Hugging Face', 'huggingface', '#ffd21e', '#242014'),
    ('Qdrant', None, '#9f2455', '#fff6fa'),
    ('Ollama', 'ollama', '#232b33', '#ffffff'),
    ('CARLA', None, '#355d76', '#ffffff'),
)
SCALE = 2
TILE = 54
GAP = 8


def rasterize(slug, size, ink=None):
    svg = ICONS / f'{slug}.svg'
    source = svg.read_text()
    if ink is not None:
        source = source.replace('fill="#242938"', 'fill="none"')
        source = re.sub(r'(<path fill=")[^"]+', rf'\g<1>{ink}', source)
    result = subprocess.run(
        ['rsvg-convert', '--width', str(size), '--height', str(size)],
        input=source.encode(),
        check=True,
        capture_output=True,
    )
    with Image.open(BytesIO(result.stdout)) as image:
        return image.convert('RGBA')


def badges(image, row, y, font):
    widths = []
    for label, icon, _, _ in row:
        widths.append(round(font.getlength(label)) + (42 if icon else 22))
    gap = 8
    x = (image.width - sum(widths) - gap * (len(row) - 1)) // 2
    draw = ImageDraw.Draw(image)
    for (label, icon, background, ink), width in zip(row, widths):
        draw.rectangle((x, y, x + width - 1, y + 43), fill=background)
        label_x = x + 11
        if icon:
            mark = rasterize(icon, 32, ink).crop((5, 5, 27, 27))
            image.alpha_composite(mark, (x + 6, y + 11))
            label_x = x + 32
        draw.text((label_x, y + 22), label, font=font, fill=ink, anchor='lm')
        x += width + gap


def grid(columns, name, tiles):
    rows = ceil(len(tiles) / columns)
    badge_rows = (BADGES,) if columns == 11 else (BADGES[:3], BADGES[3:])
    width = (columns * TILE + (columns - 1) * GAP) * SCALE
    tiles_height = (rows * TILE + (rows - 1) * GAP) * SCALE
    image = Image.new('RGBA', (width, tiles_height + 24 + len(badge_rows) * 50))
    for index, tile in enumerate(tiles):
        row, column = divmod(index, columns)
        row_count = min(columns, len(tiles) - row * columns)
        inset = (columns - row_count) * (TILE + GAP) * SCALE // 2
        image.alpha_composite(tile, (inset + column * (TILE + GAP) * SCALE, row * (TILE + GAP) * SCALE))
    font = ImageFont.load_default(size=22)
    for index, row in enumerate(badge_rows):
        badges(image, row, tiles_height + 22 + index * 50, font)
    image.save(ASSETS / name, optimize=True)


def badge(name, label, width, color, icon='', tracking=2):
    center = (width + (16 if icon else 0)) / 2
    icon_markup = f'  {icon}\n' if icon else ''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="30" viewBox="0 0 {width} 30">
  <title>{label}</title>
  <path fill="{color}" d="M0 0h{width}v30H0z"/>
{icon_markup}  <text x="{center}" y="19" text-anchor="middle" fill="#fff" font-family="Arial, sans-serif" font-size="11" font-weight="700" letter-spacing="{tracking}">{label}</text>
</svg>
'''
    (ASSETS / f'{name}.svg').write_text(svg)


if __name__ == '__main__':
    tiles = [rasterize(slug, TILE * SCALE) for slug in STACK]
    grid(11, 'tech-stack.png', tiles)
    grid(6, 'tech-stack-mobile.png', tiles)
    badge('contact-linkedin', 'LINKEDIN', 100, '#0a66c2')
    badge('contact-email', 'EMAIL', 96, '#bd3d2a',
          '<path d="M11 11h13v9H11z M11 11l6.5 5 6.5-5" fill="none" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/>')
    badge('contact-repositories', 'REPOSITORIES', 142, '#374a3c')
    badge('cert-aws-architect', 'AWS SOLUTIONS ARCHITECT ASSOCIATE', 248, '#845016', tracking=.35)
    badge('cert-azure-ai', 'AZURE AI ENGINEER ASSOCIATE', 204, '#185480', tracking=.35)
    badge('cert-azure-data', 'AZURE DATA FUNDAMENTALS', 185, '#185480', tracking=.35)
