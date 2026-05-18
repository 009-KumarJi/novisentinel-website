"""Generate all icon variants from the brand mark.

Outputs (in this directory):
    favicon-16.png         (browsers w/o SVG favicon support)
    favicon-32.png         (taskbar tab icons)
    apple-touch-icon.png   (180×180, iOS home screen)
    icon-512.png           (PWA / large slots)
    og-square.png          (1080×1080, LinkedIn square crop)
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

INK = (10, 11, 13)
BONE = (232, 230, 225)
MINT = (124, 245, 176)
DEEP_MINT = (31, 138, 91)


def cubic(p0, p1, p2, p3, n=64):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        out.append((x, y))
    return out


def draw_shield(canvas, size, fill_shield, stroke_n, mint=MINT, padding=0.06):
    """Draw the Aperture Shield centered into a square `size`×`size` canvas.

    fill_shield  — shield body color (use BONE on dark bg, INK on light bg)
    stroke_n     — N letterform color (must contrast with fill_shield)
    mint         — sentinel dot color (use deep_mint on light bg)
    padding      — outer canvas padding fraction (0 = touches edge)
    """
    inner = size * (1 - 2 * padding)
    scale = inner / 96
    off = (size - inner) / 2 - 48 * scale + size / 2 - inner / 2

    def p(x, y):
        return (off + x * scale + (size - inner) / 2, (size - inner) / 2 + y * scale)

    d = ImageDraw.Draw(canvas, "RGBA")

    # shield outer path
    pts = [p(48, 6), p(84, 18), p(84, 44)]
    pts += cubic(p(84, 44), p(84, 64), p(70, 78), p(48, 88))
    pts += cubic(p(48, 88), p(26, 78), p(12, 64), p(12, 44))
    pts += [p(12, 18)]
    d.polygon(pts, fill=fill_shield)

    # the open N
    sw = max(2, int(6 * scale))
    nodes = [p(32, 62), p(32, 32), p(64, 62), p(64, 32)]
    for i in range(3):
        d.line([nodes[i], nodes[i + 1]], fill=stroke_n, width=sw)
    for x, y in nodes:
        d.ellipse([x - sw/2, y - sw/2, x + sw/2, y + sw/2], fill=stroke_n)

    # sentinel pin
    px, py = p(72, 22)
    r = max(2, 6 * scale)
    d.ellipse([px - r, py - r, px + r, py + r], fill=mint)


here = os.path.dirname(__file__)


def make_icon(size, name, bg=None, fill_shield=BONE, stroke_n=INK, mint=MINT, padding=0.10, rounded=False, radius_frac=0.22):
    img = Image.new("RGBA", (size, size), bg if bg else (0, 0, 0, 0))
    if rounded and bg:
        # mask the corners with a rounded rect (Apple-style)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=int(size * radius_frac), fill=255)
        bg_img = Image.new("RGBA", (size, size), bg)
        img = Image.composite(bg_img, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask)
    draw_shield(img, size, fill_shield, stroke_n, mint=mint, padding=padding)
    img.save(os.path.join(here, name), "PNG", optimize=True)
    return os.path.join(here, name)


# 16 / 32 px favicons — filled shield (max contrast at tiny sizes)
out16 = make_icon(16, "favicon-16.png", bg=None, padding=0.0)
out32 = make_icon(32, "favicon-32.png", bg=None, padding=0.0)

# Apple touch icon — 180 × 180, ink rounded background tile
out_apple = make_icon(
    180, "apple-touch-icon.png",
    bg=INK, fill_shield=BONE, stroke_n=INK, mint=MINT,
    padding=0.20, rounded=True, radius_frac=0.22,
)

# PWA / generic 512
out_512 = make_icon(
    512, "icon-512.png",
    bg=INK, fill_shield=BONE, stroke_n=INK, mint=MINT,
    padding=0.22, rounded=True, radius_frac=0.22,
)


# ── 1080 × 1080 social square ──
SANS = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"]
SANS_IT = ["C:/Windows/Fonts/segoeuii.ttf", "C:/Windows/Fonts/seguili.ttf"]
SANS_REG = ["C:/Windows/Fonts/segoeui.ttf"]
MONO = ["C:/Windows/Fonts/consola.ttf"]


def load_font(c, size):
    for name in c:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


S = 1080
sq = Image.new("RGB", (S, S), INK)
d = ImageDraw.Draw(sq, "RGBA")

# grid
for x in range(0, S, 40):
    d.line([(x, 0), (x, S)], fill=(255, 255, 255, 10), width=1)
for y in range(0, S, 40):
    d.line([(0, y), (S, y)], fill=(255, 255, 255, 10), width=1)

# corner mint glow (bottom-right)
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = ImageDraw.Draw(glow)
for r in range(540, 0, -16):
    a = int(28 * (r / 540))
    g.ellipse([S - r, S - r * 0.65, S + r, S + r * 0.65], fill=(124, 245, 176, a))
sq = Image.alpha_composite(sq.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(sq, "RGBA")

# top hairline
d.line([(0, 110), (S, 110)], fill=(255, 255, 255, 20), width=1)

# brand row
draw_shield(sq, S, BONE, INK, padding=0.0)  # NO-OP placeholder, we redraw smaller below
# Pillow doesn't have an "easy way" to place a small logo inside a larger canvas
# without redrawing — so paint over the failed full draw with a fresh background tile
sq2 = Image.new("RGB", (S, S), INK)
d2 = ImageDraw.Draw(sq2, "RGBA")
for x in range(0, S, 40):
    d2.line([(x, 0), (x, S)], fill=(255, 255, 255, 10), width=1)
for y in range(0, S, 40):
    d2.line([(0, y), (S, y)], fill=(255, 255, 255, 10), width=1)
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = ImageDraw.Draw(glow)
for r in range(540, 0, -16):
    a = int(28 * (r / 540))
    g.ellipse([S - r, S - r * 0.65, S + r, S + r * 0.65], fill=(124, 245, 176, a))
sq2 = Image.alpha_composite(sq2.convert("RGBA"), glow).convert("RGB")
d2 = ImageDraw.Draw(sq2, "RGBA")
d2.line([(0, 110), (S, 110)], fill=(255, 255, 255, 20), width=1)

# logo at top-left (~64 px tall)
logo_tile = Image.new("RGBA", (90, 90), (0, 0, 0, 0))
draw_shield(logo_tile, 90, BONE, INK, padding=0.05)
sq2.paste(logo_tile, (80, 40), logo_tile)

# wordmark
font_brand = load_font(SANS, 38)
d2.text((184, 56), "NoviSentinel", font=font_brand, fill=BONE)

# BETA chip
font_chip = load_font(MONO, 16)
brand_w = d2.textlength("NoviSentinel", font=font_brand)
chip_x = 184 + brand_w + 14
chip_y = 64
chip_w = d2.textlength("BETA", font=font_chip) + 22
d2.rounded_rectangle(
    [chip_x, chip_y - 2, chip_x + chip_w, chip_y + 28],
    radius=15, outline=MINT, width=1, fill=(124, 245, 176, 32),
)
d2.text((chip_x + 11, chip_y + 4), "BETA", font=font_chip, fill=MINT)

# top-right meta
font_meta = load_font(MONO, 18)
right = "OPEN SOURCE · APACHE 2.0"
rw = d2.textlength(right, font=font_meta)
d2.text((S - 80 - rw, 60), right, font=font_meta, fill=(232, 230, 225, 140))

# Headline (multi-line, stacked)
font_hl = load_font(SANS, 130)
font_hl_it = load_font(SANS_IT, 130)
d2.text((80, 280), "Stop", font=font_hl, fill=BONE)
d2.text((80, 425), "leaking", font=font_hl, fill=BONE)
d2.text((80, 570), "secrets", font=font_hl_it, fill=MINT)
d2.text((80, 715), "to your AI.", font=font_hl, fill=BONE)

# subhead
font_sub = load_font(SANS_REG, 28)
d2.text((80, 890), "Open-source privacy proxy for AI coding agents.", font=font_sub, fill=(232, 230, 225, 175))

# bottom hairline + footer row
d2.line([(0, 970), (S, 970)], fill=(255, 255, 255, 20), width=1)
font_foot = load_font(MONO, 18)
d2.ellipse([80, 1010, 92, 1022], fill=MINT)
d2.text((104, 1006), "v1.0.0-beta · runs locally · no telemetry", font=font_foot, fill=(232, 230, 225, 140))
dom = "novisentinel.com"
dw = d2.textlength(dom, font=font_foot)
d2.text((S - 80 - dw, 1006), dom, font=font_foot, fill=MINT)

sq2.save(os.path.join(here, "og-square.png"), "PNG", optimize=True)


print("wrote:")
for f in ["favicon-16.png", "favicon-32.png", "apple-touch-icon.png", "icon-512.png", "og-square.png"]:
    p = os.path.join(here, f)
    if os.path.exists(p):
        print(f"  {f}  ({os.path.getsize(p)//1024} KB)")
