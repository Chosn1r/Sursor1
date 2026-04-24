from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = Path('/home/ubuntu/.cursor/projects/workspace/uploads/ab.pdf')
WORK_DIR = ROOT / 'data' / 'pdf_inspect'
RENDER_PATH = WORK_DIR / 'ab_page1.png'
OUTPUTS = [
    ROOT / 'deliverables' / 'k6_catalog_style_ja.png',
    ROOT / 'deliverables' / 'k6_catalog_style_ja.jpg',
    ROOT / 'data' / 'k6_catalog_style_ja.png',
    ROOT / 'data' / 'k6_catalog_style_ja.jpg',
]

CANVAS_W, CANVAS_H = 1500, 2121
BG = (248, 247, 243)
WHITE = (255, 255, 255)
TEXT = (98, 100, 104)
LINE = (214, 214, 210)


def load_font(size: int, bold: bool = False):
    candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


LABEL_FONT = load_font(24, bold=True)
NOTE_FONT = load_font(18)
SMALL_FONT = load_font(16)


def text_size(draw: ImageDraw.ImageDraw, text: str, font):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    return x1 - x0, y1 - y0


def render_pdf_page() -> Image.Image:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
    pix.save(RENDER_PATH)
    return Image.open(RENDER_PATH).convert('RGB')


def draw_shadow_card(base: Image.Image, box, radius=28):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    ld.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=radius, fill=(0, 0, 0, 34))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(layer)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius, fill=WHITE, outline=(232, 232, 228), width=2)


def draw_placeholder(draw: ImageDraw.ImageDraw, box, title: str):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=22, fill=(252, 251, 248), outline=LINE, width=2)
    for x in range(x0 + 18, x1 - 12, 24):
        draw.line((x, y0 + 16, min(x + 10, x1 - 16), y0 + 16), fill=(194, 194, 190), width=2)
        draw.line((x, y1 - 16, min(x + 10, x1 - 16), y1 - 16), fill=(194, 194, 190), width=2)
    for y in range(y0 + 30, y1 - 18, 24):
        draw.line((x0 + 16, y, x0 + 16, min(y + 10, y1 - 16)), fill=(194, 194, 190), width=2)
        draw.line((x1 - 16, y, x1 - 16, min(y + 10, y1 - 16)), fill=(194, 194, 190), width=2)

    tw, th = text_size(draw, title, SMALL_FONT)
    draw.rounded_rectangle((x0 + 22, y0 + 20, x0 + 46 + tw, y0 + 34 + th), radius=10, fill=WHITE, outline=(230, 230, 226))
    draw.text((x0 + 34, y0 + 27), title, fill=TEXT, font=SMALL_FONT)

    hint = '実例画像スペース'
    hw, hh = text_size(draw, hint, LABEL_FONT)
    draw.text(((x0 + x1 - hw) / 2, (y0 + y1 - hh) / 2 - 12), hint, fill=(185, 185, 181), font=LABEL_FONT)
    sub = 'データはPDF原本をそのまま使用'
    sw, _ = text_size(draw, sub, NOTE_FONT)
    draw.text(((x0 + x1 - sw) / 2, (y0 + y1 - hh) / 2 + 28), sub, fill=(194, 194, 190), font=NOTE_FONT)


def build_image() -> Image.Image:
    pdf_img = render_pdf_page()
    page = pdf_img.resize((CANVAS_W - 76, CANVAS_H - 96), Image.Resampling.LANCZOS)

    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), BG + (255,))
    card_box = (26, 24, CANVAS_W - 26, CANVAS_H - 24)
    draw_shadow_card(canvas, card_box)
    canvas.paste(page, (38, 38))

    # Overlay a blank placeholder only on the top-left sample image area.
    scale_x = page.width / pdf_img.width
    scale_y = page.height / pdf_img.height
    src_box = (28, 70, 470, 328)
    px0 = int(38 + src_box[0] * scale_x)
    py0 = int(38 + src_box[1] * scale_y)
    px1 = int(38 + src_box[2] * scale_x)
    py1 = int(38 + src_box[3] * scale_y)
    draw = ImageDraw.Draw(canvas)
    draw_placeholder(draw, (px0, py0, px1, py1), 'CASE IMAGE 01')

    # Add a small note clarifying this version follows the supplied PDF exactly.
    note = '※ パラメータ部分は提供PDFの原本をそのまま使用し、左上の実例画像のみ空欄化。'
    nw, nh = text_size(draw, note, SMALL_FONT)
    note_box = (CANVAS_W - nw - 84, CANVAS_H - 62, CANVAS_W - 44, CANVAS_H - 30)
    draw.rounded_rectangle(note_box, radius=12, fill=(255, 255, 255, 235), outline=(232, 232, 228))
    draw.text((note_box[0] + 18, note_box[1] + 7), note, fill=TEXT, font=SMALL_FONT)

    return canvas.convert('RGB')


def main():
    image = build_image()
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, quality=95)
        print(f'saved {path}')


if __name__ == '__main__':
    main()
