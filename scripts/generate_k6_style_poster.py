from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliverables"
OUT_PATH = OUT_DIR / "k6_style_poster.png"
OUT_JPG_PATH = OUT_DIR / "k6_style_poster.jpg"

WIDTH, HEIGHT = 1600, 900
BG = (248, 247, 243)
RED = (203, 23, 24)
YELLOW = (246, 228, 43)
GREEN = (17, 83, 76)
DARK = (32, 36, 41)
GRAY = (110, 110, 110)
LIGHT_GRAY = (236, 236, 232)
ORANGE = (232, 169, 62)
BLUE = (76, 145, 210)


def load_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


TITLE_FONT = load_font(68, bold=True)
SUBTITLE_FONT = load_font(34, bold=True)
SECTION_FONT = load_font(28, bold=True)
BODY_FONT = load_font(24)
SMALL_FONT = load_font(19)
TINY_FONT = load_font(15)
CARD_TITLE_FONT = load_font(26, bold=True)


def text_size(draw: ImageDraw.ImageDraw, text: str, font):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def draw_vertical_gradient(image: Image.Image, box, top_color, bottom_color):
    x0, y0, x1, y1 = box
    gradient = Image.new("RGBA", (x1 - x0, y1 - y0), 0)
    gd = ImageDraw.Draw(gradient)
    height = max(1, y1 - y0 - 1)
    for i in range(y1 - y0):
        ratio = i / height
        color = tuple(int(top_color[c] * (1 - ratio) + bottom_color[c] * ratio) for c in range(3)) + (255,)
        gd.line((0, i, x1 - x0, i), fill=color)
    image.paste(gradient, (x0, y0), gradient)


def shadowed_panel(base: Image.Image, xy, radius=24, shadow=16, fill=(255, 255, 255, 255)):
    x0, y0, x1, y1 = xy
    shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=radius, fill=(0, 0, 0, 50))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow))
    base.alpha_composite(shadow_layer)
    fg = ImageDraw.Draw(base)
    fg.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_highlight_spec(draw: ImageDraw.ImageDraw, x, y, label, value, value_color=YELLOW):
    draw.text((x, y), label, fill=DARK, font=BODY_FONT)
    label_w, _ = text_size(draw, label, BODY_FONT)
    value_w, value_h = text_size(draw, value, BODY_FONT)
    draw.rounded_rectangle(
        (x + label_w + 10, y + 2, x + label_w + 22 + value_w, y + value_h + 6),
        radius=6,
        fill=value_color,
    )
    draw.text((x + label_w + 16, y), value, fill=DARK, font=BODY_FONT)


def draw_bullets(draw: ImageDraw.ImageDraw, x, y, title, items, width, bullet_color=ORANGE):
    draw.text((x, y), title, fill=DARK, font=SECTION_FONT)
    y += 42
    for item in items:
        draw.ellipse((x, y + 9, x + 10, y + 19), fill=bullet_color)
        draw.text((x + 20, y), item, fill=DARK, font=SMALL_FONT)
        y += 32


def draw_floorplan(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, outline=(110, 110, 110), width=3, fill=(255, 255, 255))
    inset = 14
    ix0, iy0, ix1, iy1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    draw.rectangle((ix0, iy0, ix1, iy1), outline=(160, 160, 160), width=2)
    draw.rectangle((ix0 + 10, iy0 + 10, ix1 - 110, iy1 - 20), outline=(140, 140, 140), width=2)
    draw.rectangle((ix1 - 100, iy0 + 10, ix1 - 10, iy0 + 70), outline=(140, 140, 140), width=2)
    draw.rectangle((ix1 - 100, iy0 + 78, ix1 - 10, iy1 - 10), outline=(140, 140, 140), width=2)
    draw.rounded_rectangle((ix0 + 38, iy0 + 18, ix0 + 110, iy0 + 62), radius=8, outline=(180, 180, 180), width=2)
    draw.rounded_rectangle((ix0 + 124, iy0 + 18, ix0 + 164, iy0 + 48), radius=6, outline=(180, 180, 180), width=2)
    draw.rounded_rectangle((ix0 + 176, iy0 + 18, ix0 + 216, iy0 + 48), radius=6, outline=(180, 180, 180), width=2)
    draw.rounded_rectangle((ix0 + 216, iy0 + 76, ix0 + 306, iy0 + 122), radius=20, outline=(180, 180, 180), width=2)
    for i in range(10):
        xx = ix0 + 4 + i * 26
        draw.line((xx, iy0 + 72, xx + 28, iy1 - 10), fill=(222, 222, 222), width=1)
    draw.rectangle((ix1 - 92, iy0 + 18, ix1 - 18, iy0 + 56), fill=(225, 225, 225))
    draw.rectangle((ix1 - 92, iy0 + 88, ix1 - 18, iy1 - 18), fill=(235, 235, 235))
    draw.text((x0 + 14, y1 + 8), "*参考平面图 / FOR REFERENCE ONLY", fill=DARK, font=TINY_FONT)


def draw_pod(draw: ImageDraw.ImageDraw, box):
    x0, y0, x1, y1 = box
    shadow = (x0 + 20, y1 - 18, x1 - 30, y1 + 16)
    draw.ellipse(shadow, fill=(210, 210, 210))

    outer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    od = ImageDraw.Draw(outer)
    od.rounded_rectangle((0, 26, x1 - x0 - 24, y1 - y0 - 18), radius=72, fill=(245, 245, 243), outline=(150, 156, 160), width=4)
    od.rounded_rectangle((40, 44, x1 - x0 - 70, y1 - y0 - 52), radius=58, fill=(249, 249, 247), outline=(205, 205, 205), width=2)
    od.rounded_rectangle((48, 32, 124, y1 - y0 - 18), radius=45, fill=(40, 45, 53))
    od.rounded_rectangle((x1 - x0 - 164, 40, x1 - x0 - 84, y1 - y0 - 56), radius=12, fill=(230, 231, 229), outline=(180, 180, 180))
    od.rounded_rectangle((152, 48, x1 - x0 - 196, y1 - y0 - 54), radius=18, fill=(228, 235, 242), outline=(180, 190, 200))
    od.line((0, y1 - y0 - 16, x1 - x0 - 24, y1 - y0 - 16), fill=(135, 135, 135), width=4)
    outer = outer.filter(ImageFilter.GaussianBlur(0.2))
    draw.bitmap((x0, y0), outer)
    draw.text((x0 + 68, y0 + 82), "K6", fill=(245, 245, 245), font=load_font(34, bold=True))
    draw.text((x0 + 112, y0 + 88), "series", fill=(207, 213, 219), font=load_font(16))


def draw_photo_card(draw: ImageDraw.ImageDraw, x, y, w, h, title, lines, tint):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=(255, 255, 255), outline=(226, 226, 226))
    draw.rounded_rectangle((x, y, x + w, y + h - 60), radius=12, fill=tint)
    arch_box = (x + 36, y + 24, x + w - 36, y + h - 94)
    draw.rounded_rectangle(arch_box, radius=80, fill=(236, 216, 188))
    draw.rounded_rectangle((arch_box[0] + 28, arch_box[1] + 18, arch_box[2] - 28, arch_box[3] - 16), radius=56, fill=(193, 151, 101))
    draw.rectangle((arch_box[0] + 36, arch_box[1] + 36, arch_box[2] - 36, arch_box[3] - 24), fill=(228, 214, 197))
    draw.text((x + 18, y + h - 50), title, fill=DARK, font=CARD_TITLE_FONT)
    yy = y + h - 18
    for idx, line in enumerate(lines):
        draw.text((x + 126 * idx + 18 if idx else x + 18, y + h - 20), "", fill=DARK, font=TINY_FONT)
    ty = y + h - 28
    for line in lines:
        draw.text((x + 120, ty), line, fill=GRAY, font=TINY_FONT)
        ty += 16


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
    draw = ImageDraw.Draw(base)

    # Background accents
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BG)
    draw.rectangle((0, 736, 36, HEIGHT), fill=GREEN)
    draw_vertical_gradient(base, (644, 34, 666, 740), (243, 176, 70), (195, 69, 183))

    # Top-right brand mark
    draw.text((1378, 20), "ZCAMP", fill=(100, 140, 150), font=load_font(28, bold=True))

    # Left header
    draw.text((56, 72), "ZCAMP K6", fill=RED, font=TITLE_FONT)
    draw.text((60, 142), "SE / PRO / MAX", fill=DARK, font=SUBTITLE_FONT)

    spec_x = 60
    spec_y = 214
    draw_highlight_spec(draw, spec_x, spec_y, "系列型号:", "K6 SE / K6 PRO / K6 MAX")
    draw_highlight_spec(draw, spec_x, spec_y + 42, "参考售价:", "$5,900 起 / $7,900 起 / CUSTOM")
    draw_highlight_spec(draw, spec_x, spec_y + 84, "适住人数:", "2-4 人")
    draw_highlight_spec(draw, spec_x, spec_y + 126, "产品特征:", "一体舱体 / 智能门锁 / 天窗 / 卫浴 / 空调")
    draw_highlight_spec(draw, spec_x, spec_y + 168, "配色方案:", "Ivory White / Obsidian Gray")
    draw.text((60, 428), "外观标准化设计", fill=DARK, font=SMALL_FONT)
    features = [
        "流线型整体舱体，强调未来感与一体化量产外观",
        "前窗 / 侧窗 / 入口门形成图 1 类似的横向展示重心",
        "可搭配平台、踏步、外摆区域作为营地扩展界面",
        "适合做系列海报、单品介绍页与招商资料封面",
    ]
    yy = 460
    for item in features:
        draw.text((60, yy), "• " + item, fill=DARK, font=TINY_FONT)
        yy += 22

    draw_pod(draw, (38, 560, 598, 760))
    draw.rounded_rectangle((500, 546, 616, 584), radius=8, outline=(185, 185, 185), fill=(255, 255, 255))
    draw.text((518, 553), "AI 识图风格化", fill=DARK, font=TINY_FONT)

    # Floorplan
    draw_floorplan(draw, (688, 32, 1128, 172))

    # Top right green block
    draw.rounded_rectangle((1142, 36, 1570, 312), radius=0, fill=GREEN)
    draw.rectangle((1162, 56, 1545, 84), fill=(238, 238, 238))
    draw.text((1178, 59), "ROOM CONTROL UNIT", fill=DARK, font=SMALL_FONT)
    green_items = [
        "智能开关 / Smart switch",
        "舱门联动与智能锁",
        "空调与新风模式切换",
        "照明 / 场景预设",
    ]
    y = 108
    for item in green_items:
        draw.text((1182, y), item, fill=(248, 248, 245), font=TINY_FONT)
        y += 26

    draw.text((1180, 218), "内装推荐模块", fill=(248, 248, 245), font=SMALL_FONT)
    interior_items = [
        "全景天窗 / 电动遮阳",
        "一体式卫浴 / 洗手台",
        "迷你吧台 / 收纳柜",
        "影音位 / 投影接口",
        "折叠沙发床 / 储物地台",
        "窗帘灯带 / 氛围照明",
    ]
    y = 252
    for item in interior_items:
        draw.text((1182, y), item, fill=(248, 248, 245), font=TINY_FONT)
        y += 22

    # Option card
    shadowed_panel(base, (700, 214, 1126, 660), radius=8, shadow=10)
    draw = ImageDraw.Draw(base)
    draw.text((728, 240), "配置亮点", fill=DARK, font=SECTION_FONT)
    option_items_left = [
        "标准玻璃幕墙与横向景观窗",
        "可选天窗系统与电动遮阳",
        "集成空调 / 新风 / 照明",
        "一体式卫浴模块",
        "入口平台与踏步系统",
        "可定制外立面包覆材料",
    ]
    option_items_right = [
        "迷你吧台 / 小冰箱位",
        "投影 / 音响 / 电视接口",
        "沙发床与地台储物",
        "AI 语音与智能家居联动",
        "地暖 / 保温升级（可选）",
        "适合营地、民宿、样板舱展示",
    ]
    draw_bullets(draw, 728, 288, "标准配置", option_items_left, width=350)
    draw_bullets(draw, 928, 288, "可升级项", option_items_right, width=170)

    # Right side comparison list
    shadowed_panel(base, (1142, 338, 1570, 660), radius=8, shadow=10, fill=(252, 251, 247, 255))
    draw = ImageDraw.Draw(base)
    draw.text((1168, 362), "系列差异参考", fill=DARK, font=SECTION_FONT)
    compare_rows = [
        ("K6 SE", "入门展示版 / 轻量配置"),
        ("K6 PRO", "平衡型主推款 / 卫浴与氛围灯更完整"),
        ("K6 MAX", "高配定制款 / 影音、地暖、储物加强"),
        ("共通点", "2-4 人居住、模块化交付、适配营地场景"),
        ("配色", "Ivory White / Obsidian Gray"),
        ("备注", "图 2 信息重组后，按图 1 样式做成单页海报"),
    ]
    y = 408
    for name, value in compare_rows:
        draw.ellipse((1168, y + 8, 1178, y + 18), fill=ORANGE)
        draw.text((1188, y), name, fill=DARK, font=SMALL_FONT)
        draw.text((1280, y), value, fill=GRAY, font=TINY_FONT)
        y += 42

    # Bottom cards
    cards = [
        ("K6 SE", ["紧凑展示", "基础智能"], (220, 201, 173)),
        ("K6 PRO", ["卫浴升级", "氛围更完整"], (207, 184, 156)),
        ("K6 MAX", ["高配影音", "定制扩展"], (198, 176, 149)),
    ]
    cx = 720
    for title, lines, tint in cards:
        draw_photo_card(draw, cx, 684, 264, 180, title, lines, tint)
        cx += 282

    # Footer note
    footer = "NOTE: Based on the content structure of figure 2 and rebuilt in the layout language of figure 1."
    draw.text((682, 866), footer, fill=(240, 240, 240), font=TINY_FONT)
    draw.text((56, 846), "*本图为重制版示意图，适合继续替换为真实产品渲染与正式参数。", fill=GRAY, font=TINY_FONT)

    base = base.convert("RGB")
    base.save(OUT_PATH, quality=95)
    base.save(OUT_JPG_PATH, quality=95)
    print(f"saved {OUT_PATH}")
    print(f"saved {OUT_JPG_PATH}")


if __name__ == "__main__":
    main()
