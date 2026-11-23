#!/usr/bin/env python3
"""Draw one image summing up the world news of Monday, 23 November 2026.

Writes /output/entry.png (1024x1024, PNG, under 1 MiB). No network, no
randomness, no clock: every run produces byte-identical output.

Layout: a newspaper front page. A navy masthead names the day, then six
stories in a 2x3 grid, each with a drawn pictogram, a kicker, a headline
and a one-paragraph summary. A navy footer closes the page.

Run: python3 main.py
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path("/output/entry.png")

PAPER = (247, 243, 234)      # warm off-white
INK = (22, 28, 38)          # near-black for headlines
BODY = (64, 70, 80)         # grey for summaries
NAVY = (20, 38, 63)         # masthead / footer
GOLD = (232, 184, 75)       # date line
RULE = (200, 192, 174)      # hairline dividers
WHITE = (255, 255, 255)

HEADER_H = 148
FOOTER_H = 64
GRID_TOP = HEADER_H
GRID_BOTTOM = H - FOOTER_H
COLS, ROWS = 2, 3
CELL_W = W // COLS
CELL_H = (GRID_BOTTOM - GRID_TOP) // ROWS

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"


def load_font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


# The six stories of Monday, 23 November 2026, as reported that day.
# (kicker, headline, summary, tile colour, icon)
STORIES = [
    (
        "CLIMATE",
        "COP31 ENDS WITH NO DEAL",
        "Antalya climate talks collapse: the EU and about 130 nations "
        "reject a text with no fossil-fuel phase-out.",
        (14, 124, 107),
        "globe",
    ),
    (
        "WAR IN UKRAINE",
        "10 DEAD IN KYIV REGION",
        "A Russian strike on Dymer kills at least 10; rescuers pull a "
        "boy alive from the rubble as Kyiv region mourns.",
        (74, 74, 85),
        "building",
    ),
    (
        "MARKETS",
        "MARKETS SLIDE ON AI FEARS",
        "Nikkei falls 5.06% and the S&P 500 drops 3.7% as fears that "
        "AI shares are overpriced spread across Asia.",
        (192, 57, 43),
        "chart",
    ),
    (
        "U.S. POLITICS",
        "DEMOCRATS WIN BIG IN THE HOUSE",
        "Democrats take 258 House seats - the largest US House "
        "majority since 1992.",
        (31, 78, 121),
        "capitol",
    ),
    (
        "DISASTER",
        "24 DEAD IN FACTORY FIRE",
        "A candy factory fire in Serang kills 24; dozens of workers "
        "are still missing.",
        (211, 84, 0),
        "factory",
    ),
    (
        "CRIME",
        "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
        "FBI most-wanted drug lord 'El Chapo Isidro' is seized in a "
        "deadly Sinaloa firefight.",
        (44, 62, 80),
        "cuffs",
    ),
]


def wrap(text, font, draw, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def rounded_tile(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_globe(draw, ox, oy):
    """A world globe with a red no-deal cross badge."""
    cx, cy, r = ox + 74, oy + 74, 50
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=5)
    # meridian
    draw.ellipse([cx - 25, cy - r, cx + 25, cy + r], outline=WHITE, width=3)
    # parallels
    for dy in (-22, 0, 22):
        hw = int((r * r - dy * dy) ** 0.5)
        draw.line([cx - hw, cy + dy, cx + hw, cy + dy], fill=WHITE, width=3)
    # red cross badge, bottom right
    bx, by = ox + 116, oy + 116
    draw.ellipse([bx - 17, by - 17, bx + 17, by + 17], fill=(192, 57, 43))
    draw.line([bx - 8, by - 8, bx + 8, by + 8], fill=WHITE, width=4)
    draw.line([bx - 8, by + 8, bx + 8, by - 8], fill=WHITE, width=4)


def draw_building(draw, ox, oy):
    """An apartment block under smoke, with a flame at its base."""
    # smoke puffs
    for sx, sy, sr in ((ox + 48, oy + 26, 13), (ox + 74, oy + 16, 15),
                       (ox + 100, oy + 28, 12)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(154, 160, 166))
    # block
    draw.rectangle([ox + 30, oy + 46, ox + 118, oy + 126], fill=(38, 38, 48))
    # windows: some lit, some dark
    lit = {(0, 0), (2, 0), (1, 1), (0, 2), (2, 2), (1, 3)}
    for row in range(4):
        for col in range(3):
            x0 = ox + 40 + col * 28
            y0 = oy + 56 + row * 18
            colour = (255, 211, 77) if (col, row) in lit else (90, 96, 110)
            draw.rectangle([x0, y0, x0 + 14, y0 + 10], fill=colour)
    # flame at the base, right side
    fx, fy = ox + 100, oy + 126
    draw.polygon([(fx - 16, fy), (fx - 14, fy - 16), (fx - 6, fy - 26),
                  (fx + 2, fy - 14), (fx + 12, fy - 22), (fx + 16, fy - 8),
                  (fx + 14, fy)],
                 fill=(240, 120, 30))
    draw.polygon([(fx - 8, fy), (fx - 6, fy - 12), (fx + 2, fy - 18),
                  (fx + 8, fy - 8), (fx + 8, fy)],
                 fill=(255, 211, 77))


def draw_chart(draw, ox, oy):
    """A share-price line falling off a cliff, with an arrowhead."""
    # faint grid
    for gy in (oy + 40, oy + 74, oy + 108):
        draw.line([ox + 22, gy, ox + 126, gy], fill=(255, 255, 255), width=2)
    pts = [(ox + 24, oy + 34), (ox + 48, oy + 48), (ox + 66, oy + 44),
           (ox + 84, oy + 66), (ox + 100, oy + 92), (ox + 122, oy + 116)]
    draw.line(pts, fill=WHITE, width=6, joint="curve")
    # arrowhead at the end
    ex, ey = pts[-1]
    draw.polygon([(ex + 2, ey + 2), (ex - 16, ey - 2), (ex - 2, ey - 16)],
                 fill=WHITE)
    # red down badge
    badge_font = load_font("DejaVuSans-Bold.ttf", 18)
    badge_text = "-5%"
    btw = draw.textlength(badge_text, font=badge_font)
    draw.ellipse([ox + 98, oy + 12, ox + 142, oy + 56], fill=WHITE)
    draw.text((ox + 98 + (44 - btw) / 2, oy + 25), badge_text,
              font=badge_font, fill=(192, 57, 43))


def draw_capitol(draw, ox, oy):
    """A domed capitol building."""
    # base steps
    draw.rectangle([ox + 22, oy + 112, ox + 126, oy + 122], fill=WHITE)
    draw.rectangle([ox + 28, oy + 102, ox + 120, oy + 112], fill=WHITE)
    # columns
    for cx in (ox + 38, ox + 58, ox + 78, ox + 98):
        draw.rectangle([cx, oy + 74, cx + 8, oy + 102], fill=WHITE)
    # entablature
    draw.rectangle([ox + 30, oy + 66, ox + 118, oy + 74], fill=WHITE)
    # dome
    draw.pieslice([ox + 44, oy + 22, ox + 104, oy + 82], 180, 360, fill=WHITE)
    draw.rectangle([ox + 44, oy + 56, ox + 104, oy + 66], fill=WHITE)
    # flag
    draw.line([ox + 74, oy + 8, ox + 74, oy + 24], fill=WHITE, width=3)
    draw.polygon([(ox + 74, oy + 8), (ox + 92, oy + 12), (ox + 74, oy + 16)],
                 fill=(232, 184, 75))


def draw_factory(draw, ox, oy):
    """A factory with a sawtooth roof, smoke and flame."""
    # smoke
    for sx, sy, sr in ((ox + 42, oy + 24, 12), (ox + 62, oy + 14, 14)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(154, 160, 166))
    # chimney
    draw.rectangle([ox + 100, oy + 30, ox + 116, oy + 118], fill=(60, 60, 70))
    # sawtooth roof + body
    draw.polygon([(ox + 22, oy + 118), (ox + 22, oy + 78), (ox + 44, oy + 58),
                  (ox + 44, oy + 78), (ox + 66, oy + 58), (ox + 66, oy + 78),
                  (ox + 88, oy + 58), (ox + 88, oy + 78), (ox + 100, oy + 78),
                  (ox + 100, oy + 118)],
                 fill=(60, 60, 70))
    # windows
    for wx in (ox + 30, ox + 52, ox + 72):
        draw.rectangle([wx, oy + 92, wx + 12, oy + 104], fill=(255, 211, 77))
    # flame at the door
    fx, fy = ox + 62, oy + 118
    draw.polygon([(fx - 13, fy), (fx - 11, fy - 14), (fx - 4, fy - 22),
                  (fx + 3, fy - 12), (fx + 10, fy - 18), (fx + 13, fy - 6),
                  (fx + 11, fy)],
                 fill=(255, 211, 77))


def draw_cuffs(draw, ox, oy):
    """A pair of handcuffs."""
    # chain
    draw.line([ox + 58, oy + 60, ox + 90, oy + 88], fill=WHITE, width=4)
    draw.line([ox + 90, oy + 60, ox + 58, oy + 88], fill=WHITE, width=4)
    # two rings
    draw.ellipse([ox + 24, oy + 30, ox + 66, oy + 72], outline=WHITE, width=7)
    draw.ellipse([ox + 82, oy + 76, ox + 124, oy + 118], outline=WHITE,
                 width=7)
    # keyholes
    draw.ellipse([ox + 40, oy + 46, ox + 50, oy + 56], fill=WHITE)
    draw.ellipse([ox + 98, oy + 92, ox + 108, oy + 102], fill=WHITE)


ICONS = {
    "globe": draw_globe,
    "building": draw_building,
    "chart": draw_chart,
    "capitol": draw_capitol,
    "factory": draw_factory,
    "cuffs": draw_cuffs,
}


def draw_header(draw):
    draw.rectangle([0, 0, W, HEADER_H], fill=NAVY)
    masthead = load_font("DejaVuSans-Bold.ttf", 62)
    date_font = load_font("DejaVuSans-Bold.ttf", 30)
    title = "THE WORLD IN ONE DAY"
    tw = draw.textlength(title, font=masthead)
    draw.text(((W - tw) / 2, 26), title, font=masthead, fill=WHITE)
    date = "MONDAY, 23 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_font)
    draw.text(((W - dw) / 2, 100), date, font=date_font, fill=GOLD)
    draw.line([0, HEADER_H - 1, W, HEADER_H - 1], fill=GOLD, width=3)


def draw_footer(draw):
    draw.rectangle([0, H - FOOTER_H, W, H], fill=NAVY)
    font = load_font("DejaVuSans.ttf", 21)
    text = "SIX STORIES FROM ONE DAY  ·  MONDAY, 23 NOVEMBER 2026"
    tw = draw.textlength(text, font=font)
    draw.text(((W - tw) / 2, H - FOOTER_H + 20), text, font=font, fill=WHITE)


def draw_cell(draw, index, story):
    kicker, headline, summary, colour, icon = story
    row, col = divmod(index, COLS)
    x0 = col * CELL_W
    y0 = GRID_TOP + row * CELL_H

    # icon tile
    tx, ty = x0 + 20, y0 + 58
    rounded_tile(draw, [tx, ty, tx + 148, ty + 148], 18, colour)
    ICONS[icon](draw, tx, ty)

    # text block
    text_x = x0 + 188
    text_w = x0 + CELL_W - 20 - text_x
    kicker_font = load_font("DejaVuSans-Bold.ttf", 19)
    head_font = load_font("DejaVuSans-Bold.ttf", 31)
    body_font = load_font("DejaVuSans.ttf", 21)

    draw.text((text_x, y0 + 28), " ".join(kicker), font=kicker_font,
              fill=colour)
    head_lines = wrap(headline, head_font, draw, text_w)
    hy = y0 + 56
    for line in head_lines:
        draw.text((text_x, hy), line, font=head_font, fill=INK)
        hy += 38
    body_lines = wrap(summary, body_font, draw, text_w)
    by = hy + 8
    for line in body_lines:
        draw.text((text_x, by), line, font=body_font, fill=BODY)
        by += 27


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    draw_header(draw)
    for i, story in enumerate(STORIES):
        draw_cell(draw, i, story)

    # hairline dividers between cells
    draw.line([CELL_W, GRID_TOP, CELL_W, GRID_BOTTOM], fill=RULE, width=2)
    for r in range(1, ROWS):
        y = GRID_TOP + r * CELL_H
        draw.line([0, y, W, y], fill=RULE, width=2)

    draw_footer(draw)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(OUT), format="PNG", compress_level=6)
    os.chmod(OUT, 0o644)


if __name__ == "__main__":
    main()
