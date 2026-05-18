"""Generate og-image.png (1200x630) using Pillow only — no Cairo.

Run from this directory:
    python _render-og.py
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1200, 630
INK = (10, 11, 13)
BONE = (232, 230, 225)
BONE_DIM = (232, 230, 225, 165)
MINT = (124, 245, 176)
GRID = (255, 255, 255, 10)
LINE = (255, 255, 255, 20)


def cubic(p0, p1, p2, p3, n=24):
    """Approximate a cubic bezier with n line segments."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3 * p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def load_font(candidates, size):
    """Try several font filenames; fall back to default if none load."""
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


# Windows system font paths
SANS = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf", "Arial.ttf"]
SANS_REG = ["C:/Windows/Fonts/segoeui.ttf", "Arial.ttf"]
SANS_IT = ["C:/Windows/Fonts/segoeuii.ttf", "C:/Windows/Fonts/seguili.ttf", "Arial.ttf"]
MONO = ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]

img = Image.new("RGB", (W, H), INK)
draw = ImageDraw.Draw(img, "RGBA")

# ── subtle grid ──
for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=GRID, width=1)
for y in range(0, H, 40):
    draw.line([(0, y), (W, y)], fill=GRID, width=1)

# ── mint corner glow ──
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for r in range(540, 0, -20):
    a = int(28 * (r / 540))
    gdraw.ellipse([W - r, H - r * 0.55, W + r, H + r * 0.55], fill=(124, 245, 176, a))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")

# ── hairline rules ──
draw.line([(0, 80), (W, 80)], fill=LINE, width=1)
draw.line([(0, 556), (W, 556)], fill=LINE, width=1)

# ── logo (Aperture Shield) — drawn at scale 0.85 (~40 px tall) ──
def draw_shield(cx, cy, scale):
    """Draw the shield logo centered around (cx, cy) at given scale.
    Original viewBox is 96x96; coordinates are scaled and shifted.
    """
    def p(x, y):
        return (cx + (x - 48) * scale, cy + (y - 48) * scale)

    # shield outline path: M48 6 L84 18 V44 C84 64 70 78 48 88 C26 78 12 64 12 44 V18 Z
    pts = [p(48, 6), p(84, 18), p(84, 44)]
    pts += cubic(p(84, 44), p(84, 64), p(70, 78), p(48, 88))
    pts += cubic(p(48, 88), p(26, 78), p(12, 64), p(12, 44))
    pts += [p(12, 18)]
    draw.polygon(pts, fill=BONE)

    # the open N — strokes drawn as thick lines with round caps
    sw = max(2, int(6 * scale))
    n_pts = [p(32, 62), p(32, 32), p(64, 62), p(64, 32)]
    for i in range(3):
        draw.line([n_pts[i], n_pts[i + 1]], fill=INK, width=sw)
    # round caps on the endpoints
    for x, y in n_pts:
        draw.ellipse([x - sw / 2, y - sw / 2, x + sw / 2, y + sw / 2], fill=INK)

    # sentinel pin (mint)
    px, py = p(72, 22)
    r = max(3, 6 * scale)
    draw.ellipse([px - r, py - r, px + r, py + r], fill=MINT)


# top-left: 40 px shield + wordmark
draw_shield(72 + 24, 48, scale=0.42)

font_brand = load_font(SANS, 26)
draw.text((128, 33), "NoviSentinel", font=font_brand, fill=BONE)

# BETA chip — next to the wordmark
font_chip = load_font(MONO, 11)
brand_w = draw.textlength("NoviSentinel", font=font_brand)
chip_x = 128 + brand_w + 10
chip_y = 42
chip_w = draw.textlength("BETA", font=font_chip) + 14
draw.rounded_rectangle(
    [chip_x, chip_y - 1, chip_x + chip_w, chip_y + 18],
    radius=10, outline=MINT, width=1, fill=(124, 245, 176, 32),
)
draw.text((chip_x + 7, chip_y + 2), "BETA", font=font_chip, fill=MINT)

# top-right meta
font_meta = load_font(MONO, 13)
right = "OPEN SOURCE · APACHE 2.0"
rw = draw.textlength(right, font=font_meta)
draw.text((W - 72 - rw, 36), right, font=font_meta, fill=(232, 230, 225, 140))

# ── huge headline ──
font_hl = load_font(SANS, 100)
font_hl_it = load_font(SANS_IT, 100)

draw.text((72, 170), "Stop leaking", font=font_hl, fill=BONE)
# second line: italic mint "secrets" + bone " to your AI."
y2 = 290
draw.text((72, y2), "secrets", font=font_hl_it, fill=MINT)
sw = draw.textlength("secrets", font=font_hl_it)
draw.text((72 + sw, y2), " to your AI.", font=font_hl, fill=BONE)

# ── subhead ──
font_sub = load_font(SANS_REG, 22)
draw.text((72, 442), "The open-source privacy proxy for AI coding agents.", font=font_sub, fill=(232, 230, 225, 175))
draw.text((72, 478), "Redacts secrets and PII before they ever reach the LLM.", font=font_sub, fill=(232, 230, 225, 175))

# ── bottom row ──
font_foot = load_font(MONO, 13)
# left: live dot + version meta
draw.ellipse([72, 590, 80, 598], fill=MINT)
draw.text((92, 587), "v1.0.0-beta · runs locally · no telemetry", font=font_foot, fill=(232, 230, 225, 140))
# right: novisentinel.com in mint
dom = "novisentinel.com"
dw = draw.textlength(dom, font=font_foot)
draw.text((W - 72 - dw, 587), dom, font=font_foot, fill=MINT)

out = os.path.join(os.path.dirname(__file__), "og-image.png")
img.convert("RGB").save(out, "PNG", optimize=True)
print(f"wrote {out} ({os.path.getsize(out) // 1024} KB)")
