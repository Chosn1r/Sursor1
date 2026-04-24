from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [
    ROOT / "deliverables" / "k6_catalog_style_ja.png",
    ROOT / "deliverables" / "k6_catalog_style_ja.jpg",
    ROOT / "data" / "k6_catalog_style_ja.png",
    ROOT / "data" / "k6_catalog_style_ja.jpg",
]

WIDTH, HEIGHT = 1500, 3200
BG = (250, 248, 244)
WHITE = (255, 255, 255)
TEXT = (42, 46, 54)
MUTED = (112, 114, 118)
ACCENT = (209, 93, 42)
ACCENT_SOFT = (240, 169, 130)
LINE = (207, 207, 202)
TAG_BG = (246, 238, 230)
PALE = (247, 244, 240)
ROW_ALT = (251, 250, 247)
MARK = (26, 39, 63)
OPTION = (215, 143, 57)


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
BODY_FONT = load_font(18)
SMALL_FONT = load_font(16)
TINY_FONT = load_font(14)
BIG_NUM_FONT = load_font(22, bold=True)
MARK_FONT = load_font(18, bold=True)


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
    for row in range(-2, 18):
        for col in range(-1, 5):
            x = 100 + col * 360
            y = 240 + row * 220
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
    hint_font = load_font(28, bold=True)
    hint_w, hint_h = text_size(draw, hint, hint_font)
    draw.text(((x0 + x1 - hint_w) / 2, (y0 + y1 - hint_h) / 2 - 10), hint, fill=(192, 192, 188), font=hint_font)
    sub = "左上の事例画像のみ空欄で保持"
    sub_w, _ = text_size(draw, sub, BODY_FONT)
    draw.text(((x0 + x1 - sub_w) / 2, (y0 + y1 - hint_h) / 2 + 34), sub, fill=(200, 200, 196), font=BODY_FONT)


def draw_tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str):
    tw, th = text_size(draw, text, SMALL_FONT)
    draw.rounded_rectangle((x, y, x + tw + 30, y + th + 16), radius=18, fill=TAG_BG, outline=(238, 225, 212))
    draw.text((x + 15, y + 8), text, fill=ACCENT, font=SMALL_FONT)


def draw_floorplan(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, outline=(150, 150, 146), width=2, fill=(254, 254, 252))
    ix0, iy0, ix1, iy1 = x0 + 14, y0 + 14, x1 - 14, y1 - 14
    draw.rectangle((ix0, iy0, ix1, iy1), outline=(180, 180, 176), width=2)
    draw.rectangle((ix0 + 8, iy0 + 8, ix1 - 92, iy1 - 12), outline=(160, 160, 156), width=2)
    draw.rectangle((ix1 - 84, iy0 + 8, ix1 - 8, iy0 + 56), outline=(160, 160, 156), width=2)
    draw.rectangle((ix1 - 84, iy0 + 64, ix1 - 8, iy1 - 8), outline=(160, 160, 156), width=2)
    draw.rounded_rectangle((ix0 + 34, iy0 + 14, ix0 + 102, iy0 + 54), radius=8, outline=(190, 190, 186), width=2)
    draw.rounded_rectangle((ix0 + 118, iy0 + 16, ix0 + 154, iy0 + 44), radius=6, outline=(190, 190, 186), width=2)
    draw.rounded_rectangle((ix0 + 164, iy0 + 16, ix0 + 200, iy0 + 44), radius=6, outline=(190, 190, 186), width=2)
    draw.rounded_rectangle((ix0 + 208, iy0 + 66, ix0 + 296, iy0 + 108), radius=18, outline=(190, 190, 186), width=2)
    for i in range(10):
        xx = ix0 + i * 24
        draw.line((xx, iy0 + 60, xx + 22, iy1 - 8), fill=(224, 224, 220), width=1)


def draw_pod_lineart(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.ellipse((x0 + 60, y1 - 18, x1 - 70, y1 + 10), fill=(226, 226, 223))
    draw.rounded_rectangle((x0 + 12, y0 + 30, x1 - 18, y1 - 24), radius=74, fill=(250, 250, 248), outline=(152, 156, 160), width=4)
    draw.rounded_rectangle((x0 + 58, y0 + 50, x1 - 68, y1 - 48), radius=58, fill=(245, 247, 248), outline=(208, 212, 214), width=2)
    draw.rounded_rectangle((x0 + 28, y0 + 40, x0 + 112, y1 - 24), radius=40, fill=(50, 56, 66))
    draw.rounded_rectangle((x1 - 160, y0 + 56, x1 - 84, y1 - 54), radius=16, fill=(236, 237, 235), outline=(188, 190, 193), width=2)
    draw.rounded_rectangle((x0 + 152, y0 + 60, x1 - 188, y1 - 58), radius=20, fill=(229, 236, 241), outline=(188, 198, 205), width=2)
    draw.line((x0 + 14, y1 - 24, x1 - 20, y1 - 24), fill=(125, 127, 130), width=4)
    draw.text((x0 + 60, y0 + 90), "K6", fill=(245, 245, 242), font=load_font(34, bold=True))
    draw.text((x0 + 114, y0 + 96), "series", fill=(206, 210, 214), font=BODY_FONT)


def draw_model_summary(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.text((x0, y0), "モデル構成 / 図2 全項目表示版", fill=TEXT, font=SECTION_FONT)
    draw.line((x0, y0 + 44, x0 + 260, y0 + 44), fill=ACCENT, width=3)

    model_cards = [
        ("K6 SE", "$5,900", "展示導入向け"),
        ("K6 PRO", "$7,900", "宿泊標準仕様"),
        ("K6 MAX", "CUSTOM", "上位カスタム"),
    ]
    card_w = 180
    cx = x0
    for name, price, desc in model_cards:
        draw.rounded_rectangle((cx, y0 + 64, cx + card_w, y0 + 154), radius=18, fill=PALE, outline=(236, 230, 222))
        draw.text((cx + 16, y0 + 78), name, fill=ACCENT, font=SUBSECTION_FONT)
        draw.text((cx + 16, y0 + 108), price, fill=TEXT, font=BIG_NUM_FONT)
        draw.text((cx + 16, y0 + 134), desc, fill=MUTED, font=TINY_FONT)
        cx += card_w + 14

    draw_tag(draw, x0, y0 + 176, "Ivory White")
    draw_tag(draw, x0 + 170, y0 + 176, "Space Gray")

    draw_pod_lineart(draw, (x0 + 14, y0 + 236, x0 + 360, y0 + 410))
    draw_floorplan(draw, (x0 + 388, y0 + 242, x1, y0 + 398))
    draw.text((x0 + 390, y0 + 408), "*フロアプランは参考図", fill=MUTED, font=TINY_FONT)

    notes = [
        "図2で見えている仕様・装備・オプション項目を、",
        "左上の事例画像以外はすべてレイアウト内に再配置。",
        "比較表は K6 SE / K6 PRO を中心に表示し、",
        "K6 MAX は上位カスタム枠としてヘッダーに保持。",
    ]
    yy = y0 + 446
    for note in notes:
        draw.ellipse((x0 + 2, yy + 7, x0 + 10, yy + 15), fill=ACCENT_SOFT)
        draw.text((x0 + 18, yy), note, fill=TEXT, font=BODY_FONT)
        yy += 28


def status_color(value: str):
    if value == "●":
        return MARK
    if value == "○":
        return OPTION
    if value == "◎":
        return ACCENT
    if value in {"-", "－"}:
        return MUTED
    return TEXT


def draw_status(draw: ImageDraw.ImageDraw, x_center: int, y_top: int, value: str):
    if value in {"●", "○", "◎"}:
        r = 5 if value != "◎" else 6
        draw.ellipse((x_center - r, y_top + 10, x_center + r, y_top + 10 + 2 * r), fill=status_color(value))
    elif value in {"-", "－"}:
        draw.text((x_center - 4, y_top + 4), "–", fill=MUTED, font=MARK_FONT)
    else:
        w, _ = text_size(draw, value, SMALL_FONT)
        draw.text((x_center - w / 2, y_top + 4), value, fill=status_color(value), font=SMALL_FONT)


def draw_matrix_table(draw: ImageDraw.ImageDraw, box, title: str, rows, columns, footer_lines):
    x0, y0, x1, y1 = box
    draw.text((x0, y0), title, fill=TEXT, font=SECTION_FONT)
    draw.line((x0, y0 + 44, x0 + 210, y0 + 44), fill=ACCENT, width=3)

    top = y0 + 68
    header_h = 44
    table_w = x1 - x0
    label_w = int(table_w * 0.56)
    col_w = (table_w - label_w) // len(columns)
    draw.rounded_rectangle((x0, top, x1, top + header_h), radius=16, fill=PALE, outline=(238, 238, 234))
    for idx, column in enumerate(columns):
        cx = x0 + label_w + idx * col_w
        draw.text((cx + (col_w - text_size(draw, column, SUBSECTION_FONT)[0]) / 2, top + 10), column, fill=ACCENT, font=SUBSECTION_FONT)

    yy = top + header_h + 10
    row_index = 0
    for row in rows:
        if row["kind"] == "section":
            draw.rounded_rectangle((x0, yy, x1, yy + 30), radius=12, fill=(255, 249, 243), outline=(244, 231, 219))
            draw.text((x0 + 14, yy + 6), row["label"], fill=ACCENT, font=SMALL_FONT)
            yy += 38
            continue

        label_lines = wrap_chars(draw, row["label"], SMALL_FONT, label_w - 24)
        value_lines = [wrap_chars(draw, value, SMALL_FONT, col_w - 14) if len(value) > 2 else [value] for value in row["values"]]
        max_lines = max(len(label_lines), max(len(lines) for lines in value_lines))
        row_h = max(28, 10 + max_lines * 18)
        bg = WHITE if row_index % 2 == 0 else ROW_ALT
        draw.rounded_rectangle((x0, yy, x1, yy + row_h), radius=12, fill=bg, outline=(239, 239, 235))

        ly = yy + 7
        for line in label_lines:
            draw.text((x0 + 14, ly), line, fill=TEXT, font=SMALL_FONT)
            ly += 18

        for idx, value in enumerate(row["values"]):
            cx = x0 + label_w + idx * col_w
            if value in {"●", "○", "◎", "-", "－"}:
                draw_status(draw, int(cx + col_w / 2), yy, value)
            else:
                v_lines = value_lines[idx]
                vy = yy + 7
                for v_line in v_lines:
                    tw, _ = text_size(draw, v_line, SMALL_FONT)
                    draw.text((cx + (col_w - tw) / 2, vy), v_line, fill=status_color(value), font=SMALL_FONT)
                    vy += 18

        yy += row_h + 6
        row_index += 1

    footer_y = y1 - 54
    for line in footer_lines:
        draw.text((x0, footer_y), line, fill=MUTED, font=TINY_FONT)
        footer_y += 18


def build_basic_rows():
    return [
        {"kind": "section", "label": "基本情報"},
        {"kind": "row", "label": "参考価格", "values": ["$5,900", "$7,900"]},
        {"kind": "row", "label": "長さ・幅・高さ (mm)", "values": ["9500×3300×3200", "9500×3300×3200"]},
        {"kind": "row", "label": "占有面積 (参考)", "values": ["31.4㎡", "31.4㎡"]},
        {"kind": "row", "label": "利用人数", "values": ["2人", "2〜4人"]},
        {"kind": "row", "label": "最大出力", "values": ["床暖房なし", "床暖房なし"]},
        {"kind": "row", "label": "参考重量", "values": ["<2.5t", "<4.5t"]},
        {"kind": "section", "label": "外装・構造"},
        {"kind": "row", "label": "建物の外殻", "values": ["●", "●"]},
        {"kind": "row", "label": "フロア断熱", "values": ["●", "●"]},
        {"kind": "row", "label": "複層防音ガラス（客室窓）", "values": ["●", "●"]},
        {"kind": "row", "label": "防熱防音ガラス（前窓）", "values": ["●", "●"]},
        {"kind": "row", "label": "ステンレス製エントリードア", "values": ["●", "●"]},
        {"kind": "row", "label": "玄関ステップ", "values": ["●", "●"]},
        {"kind": "row", "label": "屋根サンルーフ / 天窓", "values": ["○", "●"]},
        {"kind": "row", "label": "屋外照明", "values": ["●", "●"]},
        {"kind": "section", "label": "室内標準"},
        {"kind": "row", "label": "断熱遮光カーテン", "values": ["●", "●"]},
        {"kind": "row", "label": "室内照明システム", "values": ["●", "●"]},
        {"kind": "row", "label": "ソファベッド", "values": ["○", "●"]},
        {"kind": "row", "label": "ベッドマットレス", "values": ["●", "●"]},
        {"kind": "row", "label": "収納キャビネット", "values": ["●", "●"]},
        {"kind": "row", "label": "TV / プロジェクター準備", "values": ["○", "●"]},
        {"kind": "row", "label": "ミニバー", "values": ["○", "●"]},
        {"kind": "row", "label": "バスルーム換気ファン", "values": ["-", "●"]},
        {"kind": "row", "label": "洗面台", "values": ["-", "●"]},
        {"kind": "row", "label": "トイレ", "values": ["-", "●"]},
        {"kind": "row", "label": "シャワー", "values": ["-", "●"]},
        {"kind": "section", "label": "設備・制御"},
        {"kind": "row", "label": "3Dスマートシステム", "values": ["○", "●"]},
        {"kind": "row", "label": "全室集中コントロール", "values": ["○", "●"]},
        {"kind": "row", "label": "音声制御", "values": ["○", "●"]},
        {"kind": "row", "label": "スマートドアロック", "values": ["●", "●"]},
        {"kind": "row", "label": "空調システム", "values": ["○", "●"]},
        {"kind": "row", "label": "床暖房", "values": ["○", "○"]},
        {"kind": "row", "label": "給排水インターフェース", "values": ["○", "●"]},
        {"kind": "row", "label": "カスタム家具", "values": ["○", "○"]},
    ]


def build_option_rows():
    return [
        {"kind": "section", "label": "アクセサリー＆パーツ"},
        {"kind": "row", "label": "専用設置プラットフォーム", "values": ["○", "○"]},
        {"kind": "row", "label": "断熱パネル", "values": ["○", "○"]},
        {"kind": "row", "label": "プライベート庭エリア", "values": ["○", "○"]},
        {"kind": "row", "label": "アジャストベース", "values": ["○", "○"]},
        {"kind": "row", "label": "外部ステップデッキ", "values": ["○", "○"]},
        {"kind": "row", "label": "サイドガードフェンス", "values": ["○", "○"]},
        {"kind": "section", "label": "内装改装アップグレード"},
        {"kind": "row", "label": "ガラスパーティションドア", "values": ["-", "○"]},
        {"kind": "row", "label": "アルミダブルガラスドア", "values": ["○", "○"]},
        {"kind": "row", "label": "フルサイズワードローブ", "values": ["-", "○"]},
        {"kind": "row", "label": "ドレッサー / ミラー", "values": ["○", "○"]},
        {"kind": "row", "label": "TV キャビネット", "values": ["○", "○"]},
        {"kind": "row", "label": "コーヒーテーブル", "values": ["○", "○"]},
        {"kind": "row", "label": "コーヒーサイドテーブル", "values": ["○", "○"]},
        {"kind": "row", "label": "コートフック", "values": ["○", "○"]},
        {"kind": "row", "label": "コートハンガー", "values": ["○", "○"]},
        {"kind": "row", "label": "折りたたみソファーベッド", "values": ["-", "○"]},
        {"kind": "row", "label": "カスタム家具", "values": ["○", "○"]},
        {"kind": "section", "label": "スマートシステム"},
        {"kind": "row", "label": "スマート照明システム", "values": ["○", "●"]},
        {"kind": "row", "label": "スマート電源システム", "values": ["○", "●"]},
        {"kind": "row", "label": "3Dスマートパネル", "values": ["○", "●"]},
        {"kind": "row", "label": "全室集中コントロール", "values": ["○", "●"]},
        {"kind": "row", "label": "音声制御モジュール", "values": ["○", "●"]},
        {"kind": "row", "label": "スマートドアロック", "values": ["●", "●"]},
        {"kind": "row", "label": "スマートセンサー", "values": ["○", "●"]},
        {"kind": "section", "label": "水回り・キッチン"},
        {"kind": "row", "label": "一体型洗面カウンター", "values": ["-", "●"]},
        {"kind": "row", "label": "バスルーム換気", "values": ["-", "●"]},
        {"kind": "row", "label": "温水器", "values": ["○", "●"]},
        {"kind": "row", "label": "独立シャワー", "values": ["-", "●"]},
        {"kind": "row", "label": "トイレ", "values": ["-", "●"]},
        {"kind": "row", "label": "ミニバー / 小型冷蔵", "values": ["○", "●"]},
        {"kind": "row", "label": "冷蔵庫対応", "values": ["○", "●"]},
        {"kind": "section", "label": "快適装備"},
        {"kind": "row", "label": "エアコン", "values": ["●", "●"]},
        {"kind": "row", "label": "床暖房", "values": ["○", "○"]},
        {"kind": "row", "label": "断熱アップグレード", "values": ["○", "●"]},
        {"kind": "row", "label": "防音アップグレード", "values": ["○", "●"]},
        {"kind": "row", "label": "電動天窓", "values": ["○", "●"]},
        {"kind": "row", "label": "電動ブラインド", "values": ["○", "●"]},
        {"kind": "row", "label": "カスタムLED天井", "values": ["○", "●"]},
        {"kind": "section", "label": "エンタメ・その他"},
        {"kind": "row", "label": "プロジェクター準備", "values": ["○", "●"]},
        {"kind": "row", "label": "音響インターフェース", "values": ["○", "●"]},
        {"kind": "row", "label": "Wi-Fiルーター", "values": ["○", "○"]},
        {"kind": "row", "label": "Mug / 小物棚", "values": ["○", "○"]},
        {"kind": "row", "label": "セキュリティカメラ", "values": ["○", "○"]},
        {"kind": "row", "label": "換気 / 新風連携", "values": ["○", "●"]},
        {"kind": "row", "label": "カスタム床仕上げ", "values": ["○", "○"]},
    ]


def main():
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)

    base = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
    draw_watermark(base)
    draw = ImageDraw.Draw(base)

    draw.text((84, 54), "ZCAMP K6 パラメータ設定", fill=TEXT, font=TITLE_FONT)
    draw.text((86, 118), "ZCAMP Modular Housing / Standard Product Catalog 2026", fill=MUTED, font=SMALL_FONT)
    draw.line((84, 154, 334, 154), fill=ACCENT, width=4)
    draw.text((1360, 72), "03", fill=(184, 184, 180), font=load_font(28, bold=True))

    tl_box = (48, 184, 670, 612)
    tr_box = (720, 184, 1428, 820)
    left_box = (70, 656, 690, 3050)
    right_box = (720, 860, 1428, 3050)

    for box in (tl_box, tr_box, left_box, right_box):
        draw_card(base, box)
    draw = ImageDraw.Draw(base)

    draw_placeholder(draw, (tl_box[0] + 18, tl_box[1] + 18, tl_box[2] - 18, tl_box[3] - 18), "CASE IMAGE 01")
    draw_model_summary(draw, (tr_box[0] + 24, tr_box[1] + 24, tr_box[2] - 24, tr_box[3] - 24))
    draw_matrix_table(
        draw,
        (left_box[0] + 24, left_box[1] + 24, left_box[2] - 24, left_box[3] - 24),
        "基本仕様・標準構成",
        build_basic_rows(),
        ["K6 SE", "K6 PRO"],
        ["※ ●=標準　○=オプション　–=非搭載", "※ 図2で視認できる比較項目をテンプレート内へ全表示。"],
    )
    draw_matrix_table(
        draw,
        (right_box[0] + 24, right_box[1] + 24, right_box[2] - 24, right_box[3] - 24),
        "装備・オプション一覧",
        build_option_rows(),
        ["K6 SE", "K6 PRO"],
        ["※ 左上の実例画像以外は、図2の情報ブロックをすべて本文側へ再配置。", "※ K6 MAX は上位カスタムモデルとしてヘッダーで案内。"],
    )

    footer_y = HEIGHT - 86
    draw.line((84, footer_y, 1418, footer_y), fill=LINE, width=2)
    draw.text((86, footer_y + 16), "ZCAMP Modular Housing | Standard Product Catalog 2026", fill=MUTED, font=TINY_FONT)
    draw.text((900, footer_y + 16), "図2 全パラメータ表示版 / 左上サンプル画像のみ空欄", fill=MUTED, font=TINY_FONT)

    rgb = base.convert("RGB")
    for path in OUTPUTS:
        if path.suffix.lower() == ".png":
            rgb.save(path, quality=95)
        else:
            rgb.save(path, quality=95)
        print(f"saved {path}")


if __name__ == "__main__":
    main()
