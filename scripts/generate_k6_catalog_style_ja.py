from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliverables"
OUT_PNG = OUT_DIR / "k6_catalog_style_ja.png"
OUT_JPG = OUT_DIR / "k6_catalog_style_ja.jpg"

WIDTH, HEIGHT = 1500, 2121
BG = (250, 248, 244)
WHITE = (255, 255, 255)
TEXT = (42, 46, 54)
MUTED = (112, 114, 118)
LIGHT = (224, 224, 220)
ACCENT = (209, 93, 42)
ACCENT_SOFT = (240, 169, 130)
LINE = (207, 207, 202)
TAG_BG = (246, 238, 230)


def load_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


TITLE_FONT = load_font(54, bold=True)
SECTION_FONT = load_font(30, bold=True)
SUBSECTION_FONT = load_font(22, bold=True)
BODY_FONT = load_font(20)
SMALL_FONT = load_font(17)
TINY_FONT = load_font(14)
BIG_NUM_FONT = load_font(22, bold=True)


def text_size(draw: ImageDraw.ImageDraw, text: str, font):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    return x1 - x0, y1 - y0


def wrap_chars(draw: ImageDraw.ImageDraw, text: str, font, width: int):
    lines = []
    current = ""
    for ch in text:
        trial = current + ch
        trial_w, _ = text_size(draw, trial, font)
        if current and trial_w > width:
            lines.append(current)
            current = ch
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def draw_soft_shadow(base: Image.Image, box, radius=26, blur=16):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    ld.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=radius, fill=(0, 0, 0, 32))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_card(base: Image.Image, box, radius=24):
    draw_soft_shadow(base, box, radius=radius)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius, fill=WHITE, outline=(232, 232, 228), width=2)


def draw_watermark(base: Image.Image):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    text = "Zcamp Modular Housing  "
    wm_font = load_font(42, bold=True)
    for row in range(-2, 13):
        for col in range(-1, 5):
            x = 100 + col * 360
            y = 220 + row * 220
            draw.text((x, y), text, fill=(180, 180, 180, 18), font=wm_font)
    layer = layer.rotate(26, resample=Image.Resampling.BICUBIC, expand=False)
    base.alpha_composite(layer)


def draw_placeholder(draw: ImageDraw.ImageDraw, box, title: str):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=26, fill=(252, 251, 248), outline=(216, 216, 212), width=2)
    for x in range(x0 + 20, x1 - 10, 24):
        draw.line((x, y0 + 18, min(x + 12, x1 - 18), y0 + 18), fill=(198, 198, 194), width=2)
        draw.line((x, y1 - 18, min(x + 12, x1 - 18), y1 - 18), fill=(198, 198, 194), width=2)
    for y in range(y0 + 32, y1 - 20, 24):
        draw.line((x0 + 18, y, x0 + 18, min(y + 12, y1 - 18)), fill=(198, 198, 194), width=2)
        draw.line((x1 - 18, y, x1 - 18, min(y + 12, y1 - 18)), fill=(198, 198, 194), width=2)
    label_w, label_h = text_size(draw, title, SUBSECTION_FONT)
    draw.rounded_rectangle(
        (x0 + 26, y0 + 26, x0 + 50 + label_w, y0 + 38 + label_h),
        radius=12,
        fill=WHITE,
        outline=(230, 230, 226),
    )
    draw.text((x0 + 38, y0 + 31), title, fill=MUTED, font=SUBSECTION_FONT)
    hint = "実例画像スペース"
    hint_w, hint_h = text_size(draw, hint, load_font(28, bold=True))
    draw.text(((x0 + x1 - hint_w) / 2, (y0 + y1 - hint_h) / 2 - 10), hint, fill=(192, 192, 188), font=load_font(28, bold=True))
    sub = "ここに写真やCGを差し替え可能"
    sub_w, _ = text_size(draw, sub, BODY_FONT)
    draw.text(((x0 + x1 - sub_w) / 2, (y0 + y1 - hint_h) / 2 + 34), sub, fill=(200, 200, 196), font=BODY_FONT)


def draw_tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str):
    tw, th = text_size(draw, text, SMALL_FONT)
    draw.rounded_rectangle((x, y, x + tw + 30, y + th + 16), radius=18, fill=TAG_BG, outline=(238, 225, 212))
    draw.text((x + 15, y + 8), text, fill=ACCENT, font=SMALL_FONT)


def draw_pod_lineart(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    draw.ellipse((x0 + 80, y1 - 24, x1 - 90, y1 + 8), fill=(226, 226, 223))
    draw.rounded_rectangle((x0 + 20, y0 + 44, x1 - 20, y1 - 34), radius=80, fill=(250, 250, 248), outline=(152, 156, 160), width=4)
    draw.rounded_rectangle((x0 + 74, y0 + 66, x1 - 76, y1 - 62), radius=62, fill=(245, 247, 248), outline=(208, 212, 214), width=2)
    draw.rounded_rectangle((x0 + 40, y0 + 50, x0 + 138, y1 - 34), radius=42, fill=(50, 56, 66))
    draw.rounded_rectangle((x1 - 184, y0 + 70, x1 - 96, y1 - 66), radius=16, fill=(236, 237, 235), outline=(188, 190, 193), width=2)
    draw.rounded_rectangle((x0 + 178, y0 + 74, x1 - 220, y1 - 68), radius=22, fill=(229, 236, 241), outline=(188, 198, 205), width=2)
    draw.line((x0 + 22, y1 - 34, x1 - 24, y1 - 34), fill=(125, 127, 130), width=4)
    draw.text((x0 + 76, y0 + 118), "K6", fill=(245, 245, 242), font=load_font(40, bold=True))
    draw.text((x0 + 138, y0 + 126), "series", fill=(206, 210, 214), font=BODY_FONT)
    draw.arc((x0 + 34, y0 + 40, x1 - 30, y1 - 18), 195, 345, fill=(180, 180, 180), width=2)
    for i in range(5):
        px = x0 + 236 + i * 78
        draw.line((px, y0 + 90, px, y1 - 76), fill=(214, 220, 224), width=1)


def draw_overview(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.text((x0, y0), "Zcamp K6 series 概要", fill=TEXT, font=SECTION_FONT)
    draw.line((x0, y0 + 44, x0 + 220, y0 + 44), fill=ACCENT, width=3)
    draw_tag(draw, x0, y0 + 62, "Ivory White")
    draw_tag(draw, x0 + 170, y0 + 62, "Obsidian Gray")
    draw_pod_lineart(draw, (x0 + 24, y0 + 136, x1 - 24, y0 + 356))
    summary = [
        "モジュール一体成形の流線型ハウジング。",
        "2〜4名の宿泊を想定した標準化シリーズ。",
        "スマートロック、天窓、空調、衛浴の組み合わせを想定。",
        "キャンプ場・民宿・展示ユニットに展開しやすい構成。",
    ]
    yy = y0 + 382
    for line in summary:
        draw.ellipse((x0 + 2, yy + 9, x0 + 10, yy + 17), fill=ACCENT)
        for wrapped in wrap_chars(draw, line, BODY_FONT, x1 - x0 - 30):
            draw.text((x0 + 24, yy), wrapped, fill=TEXT, font=BODY_FONT)
            yy += 28
        yy += 10

    box_y = y1 - 112
    stat_boxes = [
        ("想定人数", "2〜4人"),
        ("価格帯", "$5,900〜"),
        ("納品形式", "モジュール"),
    ]
    bx = x0
    bw = (x1 - x0 - 24) // 3
    for title, value in stat_boxes:
        draw.rounded_rectangle((bx, box_y, bx + bw, box_y + 88), radius=18, fill=(251, 247, 242), outline=(236, 230, 222))
        draw.text((bx + 18, box_y + 16), title, fill=MUTED, font=SMALL_FONT)
        draw.text((bx + 18, box_y + 44), value, fill=ACCENT, font=BIG_NUM_FONT)
        bx += bw + 12


def draw_spec_table(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.text((x0, y0), "基本仕様", fill=TEXT, font=SECTION_FONT)
    draw.line((x0, y0 + 44, x0 + 110, y0 + 44), fill=ACCENT, width=3)

    top = y0 + 74
    label_w = 170
    col_w = (x1 - x0 - label_w - 16) // 3
    header_h = 48
    draw.rounded_rectangle((x0, top, x1, top + header_h), radius=16, fill=(247, 244, 240))
    headers = ["K6 SE", "K6 PRO", "K6 MAX"]
    for i, header in enumerate(headers):
        cx = x0 + label_w + 8 + i * col_w
        draw.text((cx + 22, top + 12), header, fill=ACCENT, font=SUBSECTION_FONT)

    rows = [
        ("外形寸法 (参考)", "コンパクト", "標準", "拡張"),
        ("想定人数", "2人", "2〜4人", "2〜4人"),
        ("ベッド構成", "ダブル", "ソファベッド", "ダブル+収納"),
        ("スマートロック", "標準", "標準", "標準"),
        ("空調システム", "オプション", "標準", "標準"),
        ("天窓", "オプション", "標準", "標準"),
        ("衛浴モジュール", "-", "標準", "標準"),
        ("ミニバー", "-", "オプション", "標準"),
        ("収納強化", "基本", "拡張", "プレミアム"),
        ("音響 / 投影", "-", "オプション", "標準"),
        ("断熱アップ", "オプション", "オプション", "標準"),
        ("外装色", "2色", "2色", "2色"),
        ("納品形態", "完成品", "完成品", "完成品"),
        ("主な用途", "展示", "宿泊", "高配仕様"),
    ]
    row_h = 58
    yy = top + header_h + 12
    for idx, row in enumerate(rows):
        bg = (255, 255, 255) if idx % 2 == 0 else (251, 250, 247)
        draw.rounded_rectangle((x0, yy, x1, yy + row_h), radius=14, fill=bg, outline=(239, 239, 235))
        draw.text((x0 + 18, yy + 18), row[0], fill=TEXT, font=BODY_FONT)
        for i in range(3):
            cx = x0 + label_w + 8 + i * col_w
            value = row[i + 1]
            color = ACCENT if value == "標準" else TEXT
            draw.text((cx + 22, yy + 18), value, fill=color, font=BODY_FONT)
        yy += row_h + 8

    note_y = y1 - 74
    notes = [
        "※ 上記は図2の情報を整理した比較用レイアウトです。",
        "※ 実寸・設備構成は正式仕様書に合わせて差し替え可能です。",
    ]
    for note in notes:
        draw.text((x0, note_y), note, fill=MUTED, font=SMALL_FONT)
        note_y += 24


def draw_option_panel(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.text((x0, y0), "装備・オプション一覧", fill=TEXT, font=SECTION_FONT)
    draw.line((x0, y0 + 44, x0 + 210, y0 + 44), fill=ACCENT, width=3)

    columns = [
        (
            "標準装備",
            [
                "一体型シェル構造",
                "標準ドア / 玄関踏み板",
                "景観窓 / サイド開口",
                "スマートロック",
                "照明コントロール",
                "カーテン / 遮光系",
                "ベーシック収納",
                "外装 2 色対応",
            ],
        ),
        (
            "人気オプション",
            [
                "天窓システム",
                "電動遮陽",
                "一体型衛浴",
                "ミニバー / 小型冷蔵",
                "投影 / 音響インターフェース",
                "ソファベッド",
                "床暖アップグレード",
                "高断熱パッケージ",
            ],
        ),
        (
            "適用シーン",
            [
                "グランピング",
                "リゾート客室",
                "モデルルーム",
                "展示会ブース",
                "長期滞在ユニット",
                "キャンプ場管理棟",
                "モバイル宿泊",
                "カスタム案件",
            ],
        ),
    ]

    col_gap = 24
    col_w = (x1 - x0 - 2 * col_gap) // 3
    start_y = y0 + 76
    for idx, (title, items) in enumerate(columns):
        cx = x0 + idx * (col_w + col_gap)
        draw.rounded_rectangle((cx, start_y, cx + col_w, y1 - 190), radius=20, fill=(252, 251, 248), outline=(236, 236, 232))
        draw.text((cx + 20, start_y + 18), title, fill=ACCENT, font=SUBSECTION_FONT)
        yy = start_y + 60
        for item in items:
            draw.ellipse((cx + 20, yy + 8, cx + 30, yy + 18), fill=ACCENT_SOFT)
            for wrapped in wrap_chars(draw, item, SMALL_FONT, col_w - 56):
                draw.text((cx + 42, yy), wrapped, fill=TEXT, font=SMALL_FONT)
                yy += 24
            yy += 10

    sub_y = y1 - 152
    draw.text((x0, sub_y), "シリーズ差分メモ", fill=TEXT, font=SUBSECTION_FONT)
    diff_rows = [
        ("K6 SE", "導入しやすい入門モデル。展示・短期利用向け。"),
        ("K6 PRO", "宿泊用途を中心に、衛浴や快適装備を拡充。"),
        ("K6 MAX", "高配仕様。収納・影音・断熱の総合強化版。"),
    ]
    yy = sub_y + 36
    for name, desc in diff_rows:
        draw.text((x0, yy), name, fill=ACCENT, font=BODY_FONT)
        for wrapped in wrap_chars(draw, desc, BODY_FONT, x1 - x0 - 120):
            draw.text((x0 + 84, yy), wrapped, fill=MUTED, font=BODY_FONT)
            yy += 26
        yy += 10


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
    draw = ImageDraw.Draw(base)
    draw_watermark(base)
    draw = ImageDraw.Draw(base)

    # Header
    draw.text((84, 54), "ZCAMP K6 パラメータ設定", fill=TEXT, font=TITLE_FONT)
    draw.text((86, 118), "ZCAMP Modular Housing / Standard Product Catalog 2026", fill=MUTED, font=SMALL_FONT)
    draw.line((84, 154, 334, 154), fill=ACCENT, width=4)
    draw.text((1360, 72), "03", fill=(184, 184, 180), font=load_font(28, bold=True))

    # Layout cards aligned with the PDF structure
    tl_box = (48, 184, 670, 612)
    left_box = (70, 656, 690, 1784)
    tr_box = (760, 124, 1428, 704)
    mr_box = (720, 760, 1428, 1688)
    br_box = (760, 1760, 1428, 1986)

    for box in (tl_box, left_box, tr_box, mr_box, br_box):
        draw_card(base, box)
    draw = ImageDraw.Draw(base)

    draw_placeholder(draw, (tl_box[0] + 18, tl_box[1] + 18, tl_box[2] - 18, tl_box[3] - 18), "CASE IMAGE 01")
    draw_spec_table(draw, (left_box[0] + 24, left_box[1] + 24, left_box[2] - 24, left_box[3] - 24))
    draw_overview(draw, (tr_box[0] + 24, tr_box[1] + 24, tr_box[2] - 24, tr_box[3] - 24))
    draw_option_panel(draw, (mr_box[0] + 24, mr_box[1] + 24, mr_box[2] - 24, mr_box[3] - 24))
    draw_placeholder(draw, (br_box[0] + 18, br_box[1] + 18, br_box[2] - 18, br_box[3] - 18), "CASE IMAGE 02")

    # Footer
    draw.line((84, 2036, 1418, 2036), fill=LINE, width=2)
    draw.text((86, 2052), "ZCAMP Modular Housing | Standard Product Catalog 2026", fill=MUTED, font=TINY_FONT)
    draw.text((1010, 2052), "図2の内容をPDF風レイアウトへ再構成 / JA version", fill=MUTED, font=TINY_FONT)

    base = base.convert("RGB")
    base.save(OUT_PNG, quality=95)
    base.save(OUT_JPG, quality=95)
    print(f"saved {OUT_PNG}")
    print(f"saved {OUT_JPG}")


if __name__ == "__main__":
    main()
