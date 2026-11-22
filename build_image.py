#!/usr/bin/env python3
"""Render the news-image-20261122 entry ("THE WORLD IN ONE DAY") with Pillow.

One square newspaper page, 1024x1024, cream paper, all text typeset with real
Noto fonts (sharp vector text, like printed type). This script is the BUILD
step: it produces entry.png. The bounty program (main.py, stdlib only) only
validates the PNG and copies it byte-for-byte to the output directory.

Stories: the 35 verified 22 November 2026 stories from our spec v2
(~/workspace/makefun/news-image-20261122-spec-v2.md). Layout follows the
top-leaderboard newspaper format (number strip, region bar, 3 heroes + 10
grid, dotted world map with numbered pins, ALSO ON index, DATE CHECK box).
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
CW = W - 2 * MARGIN  # 972 content width

# ---- palette ----
CREAM = (247, 242, 231)
INK = (26, 26, 40)
RED = (178, 44, 38)
NAVY = (18, 38, 63)
TEAL = (36, 110, 100)
GOLD = (176, 124, 32)
BODY = (52, 48, 40)
MUTED = (96, 90, 78)
LINE = (180, 172, 150)
DARKBAR = (26, 26, 40)
WHITE = (255, 255, 255)
BROWN = (122, 74, 33)
OLIVE = (90, 90, 42)
GRAY = (58, 58, 72)

FONT_DIR = "/usr/share/fonts/truetype/noto"
F_SANS = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
F_SANS_B = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
F_SERIF = os.path.join(FONT_DIR, "NotoSerif-Regular.ttf")
F_SERIF_B = os.path.join(FONT_DIR, "NotoSerif-Bold.ttf")
F_SERIF_I = os.path.join(FONT_DIR, "NotoSerif-Italic.ttf")

_font_cache = {}


def font(path, size):
    key = (path, int(size))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, int(size))
    return _font_cache[key]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, line_h=None, max_lines=None,
                 shrink_to=None):
    """Draw wrapped text; returns total height used. If max_lines is set and
    the text needs more lines, shrink the font (down to shrink_to) and retry."""
    size = fnt.size
    cur_font = fnt
    while True:
        lines = wrap_text(draw, text, cur_font, max_w)
        if max_lines is None or len(lines) <= max_lines:
            break
        if shrink_to is None or cur_font.size <= shrink_to:
            lines = lines[:max_lines]
            break
        cur_font = font(cur_font.path, cur_font.size - 1)
    lh = line_h if line_h is not None else int(cur_font.size * 1.18)
    yy = y
    for ln in lines:
        draw.text((x, yy), ln, font=cur_font, fill=fill)
        yy += lh
    return yy - y, len(lines), cur_font


def fit_size(draw, text, path, start, minimum, max_w):
    """Largest font size (start down to minimum) whose text fits max_w."""
    size = start
    while size > minimum:
        fnt = font(path, size)
        if text_w(draw, text, fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, minimum)


def center_text(draw, cx, y, text, fnt, fill):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w

# ---------------------------------------------------------------- data ----
STATS = [
    ("~200", "nations at the COP31 talks"),
    ("03:00", "GMT deadline for objections"),
    ("400+", "drones fired at Ukraine"),
    ("110", "missiles in the same night"),
    ("7+", "people killed in Kyiv"),
    ("2", "US bases targeted in Bahrain"),
]

REGIONS = [
    ("EUROPE 9", NAVY),
    ("MIDDLE EAST 8", TEAL),
    ("AMERICAS 6", GOLD),
    ("ASIA-PACIFIC 5", RED),
    ("AFRICA 1", BROWN),
    ("WORLD 6", GRAY),
]

# Heroes: (num, banner, banner_color, place_line, chip, headline, deck, art)
HEROES = [
    (1, "COP31: DEAL CLOSE", TEAL, "ANTALYA, TURKEY \u00b7 CLIMATE",
     "\u2713 CONFIRMED",
     "COP31 climate talks close in on a final deal",
     "A new package lands after a fight over fossil fuels; delegations have "
     "until 03:00 GMT to object before a final plenary. (Reuters, BBC)",
     "cop31"),
    (2, "UKRAINE: BARRAGE", NAVY, "KYIV, UKRAINE \u00b7 WAR",
     "\u2713 OFFICIALS' COUNT",
     "Russia fires 400 drones and 110 missiles",
     "One of the war's largest overnight attacks; at least seven people are "
     "killed in Kyiv. (Al Jazeera)",
     "ukraine"),
    (3, "BAHRAIN: STRUCK", (122, 44, 38), "MANAMA, BAHRAIN \u00b7 IRAN WAR",
     "\u2713 CONFIRMED",
     "Iran strikes US bases in Bahrain",
     "An industrial site burns, no injuries; tankers are hit in Hormuz. "
     "(Al Jazeera, CNA)",
     "bahrain"),
]

# Grid: (num, banner, banner_color, place, headline, deck, art)
GRID = [
    (4, "SHIP ABLAZE", NAVY, "GULF OF FINLAND",
     "Russian cargo ship burns after drone strike",
     "Finland says Ukraine was likely behind it. (BBC)", "ship"),
    (5, "2 DEAD, 60 HURT", RED, "KRYVYI RIH",
     "Strike hits Zelenskyy's home city",
     "Russian strike on the central Ukrainian city. (Al Jazeera)", "blast"),
    (6, "24 DEAD", TEAL, "BAYELSA, NIGERIA",
     "Boat carrying mourners capsizes",
     "Passengers were going to a funeral. (DW, Sky News)", "boat"),
    (7, "COALITION TALKS", GOLD, "JERUSALEM",
     "Eisenkot invites Likud to talks",
     "He seeks the broadest possible government. (Straits Times)", "talks"),
    (8, "3 KILLED", RED, "GAZA",
     "Strike hits food aid vehicle",
     "Three Palestinians die in an air attack. (Al Jazeera, Reuters)", "aid"),
    (9, "11 DEAD", NAVY, "SINALOA, MEXICO",
     "'El Chapo Isidro' caught; violence follows",
     "FBI top-ten fugitive held after a shoot-out. (Sky News, BBC)", "badge"),
    (10, "POWER CUTS", GRAY, "TEHRAN, IRAN",
     "Iran to ration electricity",
     "War damage hits the energy network. (Straits Times)", "power"),
    (11, "SEC PROBE", TEAL, "WASHINGTON",
     "Nvidia faces US accounting probe",
     "The SEC inquiry is at an early stage. (Straits Times)", "chip"),
    (12, "BOLSONARO: ICU", GOLD, "BRASILIA, BRAZIL",
     "Bolsonaro in intensive care",
     "Ex-president stable, breathing on his own. (Al Jazeera, Reuters)", "ekg"),
    (13, "AUKUS ROW", NAVY, "CANBERRA",
     "Marles rejects US report on AUKUS subs",
     "He says the budget office is wrong. (ABC, Reuters)", "sub"),
]

# Briefs 14-35: (num, lead, rest) — lead bold, rest regular.
BRIEFS = [
    (14, "US:", " FBI looks into apparent hack of its crime database. (BBC)"),
    (15, "US:", " Teen gamer and his mother help FBI rescue a girl. (BBC)"),
    (16, "US:", " Midterm loss corners Vance as 2028 field widens. (ST)"),
    (17, "Saudi Arabia:", " Air defences down a missile. (Investing.com)"),
    (18, "Lebanon:", " Aoun demands Israeli withdrawal. (Al Jazeera)"),
    (19, "Iran:", " President warns of a 'silent economic war'. (Al Jazeera)"),
    (20, "Hormuz:", " Lewis Pugh swims strait as tanker is struck. (BBC)"),
    (21, "Moldova:", " Reports a Russian airspace breach. (Kyiv Ind.)"),
    (22, "Belgium:", " Air traffic to halt in 23 Nov national strike. (ST)"),
    (23, "Germany:", " IG Metall widens car and shipyard strikes. (Reuters)"),
    (24, "Portugal:", " Thousands march in Lisbon on living costs. (Reuters)"),
    (25, "Denmark:", " Expels Russian attache over rapper plot. (Guardian)"),
    (26, "Bangladesh:", " 30 Awami League homes set on fire. (TOI)"),
    (27, "Australia:", " Fred Nile, ex-NSW MP, dies aged 92. (ABC)"),
    (28, "Australia:", " Bystanders pull driver from burning car. (ABC)"),
    (29, "Melbourne:", " 70 years since the 1956 Olympics opened. (ABC)"),
    (30, "Trade:", " EU and Indonesia sign deal after 10 years. (DW)"),
    (31, "Rugby:", " England beat New Zealand 37-12. (Reuters)"),
    (32, "Rugby:", " France beat Argentina to reach the final. (Reuters)"),
    (33, "Football:", " Arsenal 2-2 Newcastle. (Reuters)"),
    (34, "Football:", " Liverpool host Manchester United today. (Al Jazeera)"),
    (35, "Tennis:", " Zverev v Alcaraz in today's ATP Finals final. (TOI)"),
]

DATE_CHECK = (
    "Wires read up to 05:50 UTC, Sunday 22 November 2026; every story here was "
    "reported or still developing on 22 November in at least one time zone. "
    "Left out as other days' news: the Peru earthquake (20 Nov local), Russian "
    "missiles landing in Poland (19 Nov), the Kerch Bridge strikes (earlier this "
    "week), the Shenzhen summit (19 Nov), the GTA VI launch (19 Nov), the "
    "Anthropic IPO debut (19 Nov), Wall Street's correction (20 Nov)."
)

FOOTER_SOURCES = (
    "Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, CNA, "
    "ABC Australia, Times of India, The Guardian, Kyiv Independent. Every story "
    "names its outlet. Pictures and map: original, drawn in code."
)
FOOTER_ATTEST = (
    "Every story here happened, or was first reported, on Sunday 22 November "
    "2026. Officials' counts are attributed."
)

# ---- dotted world map: 100 x 34 grid, land spans per row (x0, x1) ----
def _map_row(spans):
    row = ["."] * 100
    for a, b in spans:
        for x in range(max(0, a), min(99, b) + 1):
            row[x] = "#"
    return "".join(row)


MAP_SPANS = [
    [(36, 40), (52, 54)],                          # 0
    [(14, 18), (34, 42), (52, 53), (78, 82)],     # 1
    [(3, 8), (12, 26), (33, 42), (52, 56), (60, 95)],   # 2
    [(3, 10), (10, 28), (33, 41), (50, 57), (58, 97)],  # 3
    [(4, 10), (10, 28), (34, 40), (50, 57), (58, 98)],  # 4
    [(5, 10), (10, 28), (44, 45), (50, 57), (58, 98)],  # 5
    [(10, 28), (48, 49), (50, 57), (58, 98)],           # 6
    [(10, 27), (48, 50), (47, 60), (60, 97)],           # 7
    [(11, 27), (15, 30), (46, 60), (60, 95)],           # 8
    [(12, 30), (46, 58), (60, 64), (64, 88), (88, 95)], # 9
    [(13, 30), (46, 57), (59, 66), (66, 88), (88, 90)], # 10
    [(13, 30), (45, 56), (58, 66), (68, 74), (72, 85), (88, 90)],  # 11
    [(14, 29), (16, 24), (45, 64), (60, 66), (67, 74), (73, 85)],  # 12
    [(14, 28), (16, 25), (45, 64), (60, 66), (67, 73), (74, 84), (76, 80)],  # 13
    [(17, 25), (24, 28), (44, 64), (60, 65), (67, 72), (75, 81), (78, 84)],  # 14
    [(18, 24), (25, 28), (44, 63), (68, 71), (76, 81), (78, 88)],  # 15
    [(25, 28), (28, 36), (45, 62), (77, 81), (78, 90)],  # 16
    [(27, 37), (45, 61), (79, 90)],               # 17
    [(27, 38), (46, 60), (80, 88)],               # 18
    [(28, 39), (47, 59), (81, 87)],               # 19
    [(28, 39), (47, 58), (82, 90)],               # 20
    [(29, 38), (48, 57), (81, 92)],               # 21
    [(29, 37), (49, 56), (81, 93)],               # 22
    [(30, 36), (50, 55), (82, 93)],               # 23
    [(30, 36), (50, 55), (83, 92)],               # 24
    [(31, 35), (51, 54), (83, 91)],               # 25
    [(31, 35), (84, 90), (96, 97)],               # 26
    [(31, 34), (84, 89), (96, 98)],               # 27
    [(32, 34), (85, 88)],                         # 28
    [(32, 33), (85, 87)],                         # 29
    [(32, 33)],                                    # 30
    [(32, 33)],                                    # 31
    [(32, 32)],                                    # 32
    [],                                            # 33
]
WORLD_MAP = [_map_row(s) for s in MAP_SPANS]

# Pin positions on the 100x34 map grid: (story_num, gx, gy)
PINS = [
    (1, 60, 12), (2, 58, 8), (3, 64, 14), (4, 57, 6), (5, 59, 9),
    (6, 52, 19), (7, 61, 12), (8, 59, 14), (9, 20, 15), (10, 64, 12),
    (11, 29, 11), (12, 37, 24), (13, 91, 29),
]

# ---------------------------------------------------------- illustrations ----
def _star(draw, cx, cy, r_out, r_in, n=5, fill=None):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def draw_hero_art(draw, x0, y0, w, h, kind):
    """Flat illustration inside the hero image box (banner already drawn)."""
    if kind == "cop31":
        # Teal conference room.
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(38, 112, 100))
        draw.rectangle([x0, y0, x0 + w, y0 + 8], fill=(30, 92, 82))
        # Globe, left.
        gx, gy, gr = x0 + 34, y0 + h - 26, 22
        draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 120, 180))
        draw.ellipse([gx - 12, gy - 16, gx + 2, gy - 2], fill=(90, 170, 90))
        draw.ellipse([gx - 2, gy + 4, gx + 14, gy + 16], fill=(90, 170, 90))
        draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=(200, 220, 235), width=2)
        # Wall clock, right.
        cx, cy, cr = x0 + w - 34, y0 + 26, 17
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE,
                     outline=(26, 26, 40), width=2)
        draw.line([cx, cy, cx + 9, cy - 8], fill=INK, width=2)
        draw.line([cx, cy, cx - 1, cy - 11], fill=INK, width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
        # Long table + 8 delegates.
        ty = y0 + h - 22
        draw.rectangle([x0 + 8, ty, x0 + w - 8, ty + 12], fill=(122, 74, 33))
        draw.rectangle([x0 + 8, ty, x0 + w - 8, ty + 3], fill=(150, 98, 48))
        heads = [(150, 90, 60), (220, 180, 90), (80, 120, 200), (200, 80, 80),
                 (60, 160, 120), (190, 140, 60), (100, 100, 160), (240, 200, 140)]
        for i in range(8):
            hx = x0 + 22 + i * 34
            r, g, b = heads[i]
            draw.ellipse([hx - 6, ty - 16, hx + 6, ty - 4], fill=(r, g, b))
            draw.pieslice([hx - 9, ty - 6, hx + 9, ty + 10], 180, 360,
                          fill=(r, g, b))
    elif kind == "ukraine":
        # Navy night sky.
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY)
        for sx, sy in [(18, 8), (52, 14), (96, 6), (150, 18), (210, 8),
                       (250, 16), (290, 10), (120, 24), (180, 6), (70, 26)]:
            draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                         fill=(255, 240, 180))
        # Crescent moon.
        mx, my = x0 + w - 40, y0 + 16
        draw.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(255, 230, 140))
        draw.ellipse([mx - 5, my - 11, mx + 11, my + 7], fill=NAVY)
        # Orange dotted drone trails.
        for (x1, y1, x2, y2) in [(10, 46, 120, 20), (90, 52, 190, 26),
                                 (170, 48, 260, 22), (40, 58, 150, 34)]:
            steps = 9
            for i in range(steps + 1):
                t = i / steps
                px = x0 + x1 + (x2 - x1) * t
                py = y0 + y1 + (y2 - y1) * t
                r = 3 if i == steps else 2
                draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 140, 40))
        # Building silhouettes with lit windows.
        base = y0 + h
        for bx, bw, bh in [(0, 44, 30), (48, 36, 22), (88, 52, 34), (144, 40, 26),
                           (188, 46, 32), (238, 38, 24), (280, 36, 30)]:
            draw.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(10, 10, 20))
            for wy in range(base - bh + 5, base - 4, 9):
                for wx in range(x0 + bx + 5, x0 + bx + bw - 4, 10):
                    if (wx + wy) % 3 == 0:
                        draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
        # Two orange starburst explosions.
        _star(draw, x0 + 105, y0 + 30, 13, 5, fill=(255, 150, 40))
        _star(draw, x0 + 105, y0 + 30, 7, 3, fill=(255, 220, 90))
        _star(draw, x0 + 235, y0 + 38, 10, 4, fill=(255, 150, 40))
        _star(draw, x0 + 235, y0 + 38, 5, 2, fill=(255, 220, 90))
    else:  # bahrain — night over the sea
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(14, 26, 48))
        sea_y = y0 + int(h * 0.62)
        draw.rectangle([x0, sea_y, x0 + w, y0 + h], fill=(20, 48, 72))
        for sx, sy in [(30, 10), (90, 6), (160, 12), (230, 8), (280, 14)]:
            draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                         fill=(255, 240, 180))
        # Industrial base, left: dark buildings + tower + fire.
        draw.rectangle([x0 + 8, sea_y - 26, x0 + 70, sea_y], fill=(12, 12, 22))
        draw.rectangle([x0 + 76, sea_y - 38, x0 + 88, sea_y], fill=(12, 12, 22))
        draw.rectangle([x0 + 78, sea_y - 46, x0 + 86, sea_y - 38], fill=(12, 12, 22))
        for wy in range(sea_y - 22, sea_y - 4, 8):
            draw.rectangle([x0 + 16, wy, x0 + 20, wy + 4], fill=(255, 210, 90))
            draw.rectangle([x0 + 40, wy, x0 + 44, wy + 4], fill=(255, 210, 90))
        _star(draw, x0 + 62, sea_y - 30, 9, 3, fill=(255, 150, 40))
        _star(draw, x0 + 62, sea_y - 30, 5, 2, fill=(255, 220, 90))
        # Tanker, right, burning at the hull.
        tx0, tx1 = x0 + w - 128, x0 + w - 14
        draw.polygon([(tx0, sea_y + 4), (tx1, sea_y + 4), (tx1 - 8, sea_y + 16),
                      (tx0 + 10, sea_y + 16)], fill=(8, 8, 14))
        draw.rectangle([tx0 + 30, sea_y - 8, tx0 + 52, sea_y + 4], fill=(8, 8, 14))
        draw.rectangle([tx0 + 78, sea_y - 6, tx0 + 96, sea_y + 4], fill=(8, 8, 14))
        _star(draw, tx0 + 62, sea_y + 2, 10, 4, fill=(255, 150, 40))
        _star(draw, tx0 + 62, sea_y + 2, 5, 2, fill=(255, 220, 90))
        # Wave lines.
        for wy in [sea_y + 22, sea_y + 30]:
            for wx in range(0, w, 26):
                draw.arc([x0 + wx, wy, x0 + wx + 22, wy + 10], 180, 360,
                         fill=(140, 190, 220), width=2)


def draw_grid_icon(draw, x0, y0, w, h, kind):
    """Small flat icon inside a grid card image box."""
    mid_y = y0 + h // 2
    if kind == "ship":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 70, 105))
        for wy in [y0 + h - 8, y0 + h - 4]:
            for wx in range(0, w, 18):
                draw.arc([x0 + wx, wy, x0 + wx + 16, wy + 7], 180, 360,
                         fill=(150, 200, 235), width=2)
        draw.polygon([(x0 + 60, mid_y + 6), (x0 + 130, mid_y + 6),
                      (x0 + 122, mid_y + 14), (x0 + 68, mid_y + 14)], fill=(20, 20, 30))
        draw.rectangle([x0 + 84, mid_y - 6, x0 + 104, mid_y + 6], fill=(20, 20, 30))
        _star(draw, x0 + 94, mid_y - 10, 10, 4, fill=(255, 150, 40))
        _star(draw, x0 + 94, mid_y - 10, 5, 2, fill=(255, 220, 90))
    elif kind == "blast":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(70, 72, 78))
        base = y0 + h
        for bx, bw, bh in [(6, 30, 16), (40, 26, 12), (70, 34, 18), (108, 28, 13),
                           (140, 30, 17), (168, 14, 11)]:
            draw.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(30, 30, 38))
        _star(draw, x0 + 96, y0 + 14, 13, 5, fill=(255, 150, 40))
        _star(draw, x0 + 96, y0 + 14, 7, 3, fill=(255, 220, 90))
        _star(draw, x0 + 150, y0 + 10, 7, 3, fill=(255, 150, 40))
    elif kind == "boat":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(52, 130, 170))
        for wy in [y0 + h - 10, y0 + h - 5]:
            for wx in range(0, w, 20):
                draw.arc([x0 + wx, wy, x0 + wx + 18, wy + 7], 180, 360,
                         fill=(220, 240, 250), width=2)
        draw.polygon([(x0 + 70, mid_y + 4), (x0 + 120, mid_y + 4),
                      (x0 + 112, mid_y + 12), (x0 + 78, mid_y + 12)], fill=(120, 70, 30))
        draw.line([x0 + 95, mid_y + 4, x0 + 95, mid_y - 12], fill=(90, 60, 30), width=2)
        draw.polygon([(x0 + 95, mid_y - 12), (x0 + 95, mid_y + 2), (x0 + 110, mid_y + 2)],
                     fill=WHITE)
    elif kind == "talks":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(240, 234, 214))
        draw.rounded_rectangle([x0 + 52, y0 + 6, x0 + 106, y0 + 24], radius=7,
                               fill=(36, 110, 100))
        draw.polygon([(x0 + 62, y0 + 24), (x0 + 70, y0 + 24), (x0 + 60, y0 + 31)],
                     fill=(36, 110, 100))
        draw.rounded_rectangle([x0 + 92, y0 + 20, x0 + 142, y0 + 36], radius=7,
                               fill=(176, 124, 32))
        draw.polygon([(x0 + 122, y0 + 36), (x0 + 130, y0 + 36), (x0 + 132, y0 + 42)],
                     fill=(176, 124, 32))
        draw.line([x0 + 62, y0 + 15, x0 + 96, y0 + 15], fill=WHITE, width=2)
        draw.line([x0 + 102, y0 + 28, x0 + 132, y0 + 28], fill=WHITE, width=2)
    elif kind == "aid":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 226, 208))
        draw.rectangle([x0 + 62, mid_y - 10, x0 + 122, mid_y + 8], fill=WHITE,
                       outline=(26, 26, 40), width=2)
        draw.rectangle([x0 + 122, mid_y - 6, x0 + 140, mid_y + 8], fill=WHITE,
                       outline=(26, 26, 40), width=2)
        draw.ellipse([x0 + 72, mid_y + 6, x0 + 80, mid_y + 14], fill=(26, 26, 40))
        draw.ellipse([x0 + 126, mid_y + 6, x0 + 134, mid_y + 14], fill=(26, 26, 40))
        cx, cy = x0 + 92, mid_y - 1
        draw.rectangle([cx - 2, cy - 7, cx + 2, cy + 7], fill=RED)
        draw.rectangle([cx - 7, cy - 2, cx + 7, cy + 2], fill=RED)
    elif kind == "badge":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(26, 26, 40))
        cx, cy = x0 + w // 2, mid_y
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=GOLD,
                     outline=(255, 220, 120), width=2)
        _star(draw, cx, cy, 10, 4, fill=(255, 240, 180))
    elif kind == "power":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(58, 58, 72))
        cx = x0 + 62
        draw.polygon([(cx - 14, y0 + h - 4), (cx + 14, y0 + h - 4), (cx + 6, y0 + 6),
                      (cx - 6, y0 + 6)], fill=(26, 26, 40))
        draw.line([cx - 12, y0 + h - 12, cx + 12, y0 + h - 12], fill=(26, 26, 40), width=2)
        draw.line([cx - 8, y0 + 16, cx + 8, y0 + 16], fill=(26, 26, 40), width=2)
        lx = x0 + 128
        draw.polygon([(lx + 4, y0 + 4), (lx - 6, y0 + 22), (lx + 1, y0 + 22),
                      (lx - 4, y0 + 40), (lx + 8, y0 + 20), (lx + 1, y0 + 20)],
                     fill=(255, 220, 60))
    elif kind == "chip":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(240, 234, 214))
        draw.rectangle([x0 + 58, mid_y - 13, x0 + 100, mid_y + 13], fill=(26, 26, 40))
        draw.rectangle([x0 + 68, mid_y - 6, x0 + 90, mid_y + 6], outline=GOLD, width=2)
        for dx in (-14, 0, 14):
            draw.line([x0 + 66, mid_y + dx - 6, x0 + 58, mid_y + dx - 6],
                      fill=GOLD, width=2)
            draw.line([x0 + 100, mid_y + dx - 6, x0 + 108, mid_y + dx - 6],
                      fill=GOLD, width=2)
        cx, cy = x0 + 132, mid_y + 2
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=TEAL, width=3)
        draw.line([cx + 9, cy + 9, cx + 17, cy + 17], fill=TEAL, width=3)
    elif kind == "ekg":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 40, 34))
        pts = [(x0 + 8, mid_y), (x0 + 52, mid_y), (x0 + 66, mid_y - 12),
               (x0 + 78, mid_y + 10), (x0 + 90, mid_y - 4), (x0 + 100, mid_y),
               (x0 + 140, mid_y), (x0 + 152, mid_y - 12), (x0 + 164, mid_y + 10),
               (x0 + 176, mid_y)]
        draw.line(pts, fill=(90, 230, 120), width=3, joint="curve")
    else:  # sub
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 70, 105))
        for wy in [y0 + h - 8, y0 + h - 4]:
            for wx in range(0, w, 18):
                draw.arc([x0 + wx, wy, x0 + wx + 7, wy + 7], 180, 360,
                         fill=(150, 200, 235), width=2)
        cx, cy = x0 + w // 2, mid_y + 2
        draw.rounded_rectangle([cx - 48, cy - 9, cx + 48, cy + 9], radius=9,
                               fill=(20, 20, 30))
        draw.rectangle([cx - 12, cy - 16, cx + 14, cy - 9], fill=(20, 20, 30))
        draw.ellipse([cx + 34, cy - 3, cx + 40, cy + 3], fill=(255, 220, 90))
        draw.polygon([(cx - 48, cy - 6), (cx - 58, cy), (cx - 48, cy + 6)],
                     fill=(20, 20, 30))


def draw_map(draw, x0, y0, w, h):
    """Dotted world map from the ASCII mask + 13 numbered red pins."""
    cols, rows = 100, 34
    sx = w / cols
    sy = h / rows
    dot_r = 1.4
    for gy in range(rows):
        line = WORLD_MAP[gy]
        cy = y0 + (gy + 0.5) * sy
        for gx in range(cols):
            if line[gx] == "#":
                cx = x0 + (gx + 0.5) * sx
                draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                             fill=(168, 158, 130))
    fnt_pin = font(F_SANS_B, 9)
    for num, gx, gy in PINS:
        cx = x0 + (gx + 0.5) * sx
        cy = y0 + (gy + 0.5) * sy
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=WHITE, width=1)
        t = str(num)
        tw = text_w(draw, t, fnt_pin)
        draw.text((cx - tw / 2, cy - 6.5), t, font=fnt_pin, fill=WHITE)

# -------------------------------------------------------------- layout -----
def build():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    x0, x1 = MARGIN, MARGIN + CW
    y = MARGIN

    # 1. Top strip.
    f_top_l = font(F_SANS_B, 13)
    f_top_r = font(F_SANS_B, 11)
    draw.text((x0, y), "THE WORLD IN ONE DAY", font=f_top_l, fill=RED)
    right = "35 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    rw = text_w(draw, right, f_top_r)
    draw.text((x1 - rw, y + 1), right, font=f_top_r, fill=INK)
    draw.line([x0, y + 18, x1, y + 18], fill=INK, width=1)
    y += 24

    # 2. Masthead.
    f_date = fit_size(draw, "Sunday 22 November 2026", F_SERIF_B, 92, 58, CW)
    center_text(draw, W // 2, y, "Sunday 22 November 2026", f_date, INK)
    y += f_date.size + 8

    # 3. Sub-deck.
    f_sub = font(F_SERIF_I, 18)
    center_text(draw, W // 2, y,
                "Climate deal in sight at COP31 \u00b7 Iran hits US bases in "
                "Bahrain \u00b7 Russia's 400-drone barrage on Ukraine",
                f_sub, RED)
    y += 26

    # 4. Stats strip (6 columns).
    col_w = CW // 6
    f_num = font(F_SERIF_B, 30)
    f_lab = font(F_SANS, 11)
    for i, (num, lab) in enumerate(STATS):
        cx = x0 + col_w * i + col_w // 2
        center_text(draw, cx, y, num, f_num, RED)
        lines = wrap_text(draw, lab, f_lab, col_w - 12)
        ly = y + 36
        for ln in lines:
            center_text(draw, cx, ly, ln, f_lab, MUTED)
            ly += 13
    y += 62
    draw.line([x0, y, x1, y], fill=LINE, width=1)
    y += 6

    # 5. Region bar.
    seg_w = CW // 6
    f_reg = font(F_SANS_B, 11)
    for i, (label, color) in enumerate(REGIONS):
        sx = x0 + seg_w * i
        draw.rectangle([sx, y, sx + seg_w - 1, y + 21], fill=color)
        center_text(draw, sx + seg_w // 2, y + 4, label, f_reg, WHITE)
    y += 28

    # 6. Heroes.
    hero_w, hero_h, hero_gap = 316, 208, 12
    f_banner = font(F_SANS_B, 13)
    f_place = font(F_SANS_B, 11)
    f_chip = font(F_SANS_B, 10)
    f_h_head = font(F_SERIF_B, 23)
    f_h_deck = font(F_SANS, 12)
    for hi, (num, banner, bcol, place, chip, head, deck, art) in enumerate(HEROES):
        hx = x0 + hi * (hero_w + hero_gap)
        hy = y
        # Image box + banner + art.
        draw.rectangle([hx, hy, hx + hero_w, hy + 82], outline=LINE, width=1)
        draw.rectangle([hx + 1, hy + 1, hx + hero_w - 1, hy + 20], fill=bcol)
        draw.text((hx + 8, hy + 3), banner, font=f_banner, fill=WHITE)
        draw_hero_art(draw, hx + 1, hy + 21, hero_w - 2, 61, art)
        # Tag row: red circle number + place + chip.
        ty = hy + 88
        draw.ellipse([hx, ty, hx + 15, ty + 15], fill=RED)
        f_num_s = font(F_SANS_B, 10)
        nw = text_w(draw, str(num), f_num_s)
        draw.text((hx + 7 - nw / 2, ty + 2), str(num), font=f_num_s, fill=WHITE)
        draw.text((hx + 20, ty + 2), place, font=f_place, fill=RED)
        cw = text_w(draw, chip, f_chip) + 10
        draw.rounded_rectangle([hx + hero_w - cw, ty, hx + hero_w, ty + 15],
                               radius=3, outline=TEAL, width=1)
        draw.text((hx + hero_w - cw + 5, ty + 2), chip, font=f_chip, fill=TEAL)
        # Headline (max 2 lines) + deck (max 3 lines).
        hgt, _, _ = draw_wrapped(draw, hx, ty + 20, head, f_h_head, hero_w,
                                 INK, line_h=26, max_lines=2, shrink_to=19)
        draw_wrapped(draw, hx, ty + 20 + hgt + 3, deck, f_h_deck, hero_w,
                     BODY, line_h=15, max_lines=3, shrink_to=10)
    y += hero_h + 8

    # 7. Grid (2 rows x 5).
    card_w, card_h, card_gap = 186, 116, 10
    row_gap = 8
    f_gbanner = font(F_SANS_B, 11)
    f_gplace = font(F_SANS_B, 10)
    f_ghead = font(F_SANS_B, 15)
    f_gdeck = font(F_SANS, 11)
    for gi, (num, banner, bcol, place, head, deck, art) in enumerate(GRID):
        row, col = divmod(gi, 5)
        gx = x0 + col * (card_w + card_gap)
        gy = y + row * (card_h + row_gap)
        # Image box + banner + icon.
        draw.rectangle([gx, gy, gx + card_w, gy + 44], outline=LINE, width=1)
        draw.rectangle([gx + 1, gy + 1, gx + card_w - 1, gy + 15], fill=bcol)
        draw.text((gx + 6, gy + 2), banner, font=f_gbanner, fill=WHITE)
        draw_grid_icon(draw, gx + 1, gy + 16, card_w - 2, 28, art)
        # Place line: circle number + place.
        py = gy + 48
        draw.ellipse([gx, py, gx + 11, py + 11], fill=RED)
        f_gnum = font(F_SANS_B, 8)
        nw = text_w(draw, str(num), f_gnum)
        draw.text((gx + 5.5 - nw / 2, py + 1), str(num), font=f_gnum, fill=WHITE)
        draw.text((gx + 15, py + 1), place, font=f_gplace, fill=RED)
        # Headline (max 2) + deck (max 2).
        hgt, _, _ = draw_wrapped(draw, gx, py + 14, head, f_ghead, card_w,
                                 INK, line_h=17, max_lines=2, shrink_to=12)
        draw_wrapped(draw, gx, py + 14 + hgt + 2, deck, f_gdeck, card_w,
                     BODY, line_h=13, max_lines=2, shrink_to=9)
    y += 2 * card_h + row_gap + 8

    # 8. Bottom block: map (left) + ALSO ON (right).
    map_w = 330
    also_x = x0 + map_w + 16
    also_w = x1 - also_x
    f_sec = font(F_SANS_B, 12)
    draw.text((x0, y), "WHERE IT HAPPENED", font=f_sec, fill=RED)
    draw.text((also_x, y), "ALSO ON SUNDAY 22 NOVEMBER \u2014 22 MORE STORIES",
              font=f_sec, fill=RED)
    map_y = y + 18
    draw_map(draw, x0, map_y, map_w, 146)
    f_cap = font(F_SANS, 9)
    draw.text((x0, map_y + 148), "13 lead & grid locations \u00b7 6 continents",
              font=f_cap, fill=MUTED)
    # Briefs: 2 columns x 11, one line each, auto-shrink to fit.
    col2_w = (also_w - 12) // 2
    for bi, (num, lead, rest) in enumerate(BRIEFS):
        col, rowi = divmod(bi, 11)
        bx = also_x + col * (col2_w + 12)
        by = map_y + rowi * 15
        size = 12
        while size >= 10:
            f_b = font(F_SANS_B, size)
            f_r = font(F_SANS, size)
            f_n = font(F_SANS_B, size)
            full = "%d. %s%s" % (num, lead, rest)
            w_num = text_w(draw, "%d. " % num, f_n)
            w_lead = text_w(draw, lead, f_b)
            w_rest = text_w(draw, rest, f_r)
            if w_num + w_lead + w_rest <= col2_w:
                break
            size -= 1
        f_b = font(F_SANS_B, size)
        f_r = font(F_SANS, size)
        f_n = font(F_SANS_B, size)
        draw.text((bx, by), "%d. " % num, font=f_n, fill=RED)
        nx = bx + text_w(draw, "%d. " % num, f_n)
        draw.text((nx, by), lead, font=f_b, fill=INK)
        nx += text_w(draw, lead, f_b)
        draw.text((nx, by), rest, font=f_r, fill=BODY)
    y += 178

    # 9. DATE CHECK box.
    draw.rectangle([x0, y, x1, y + 68], outline=RED, width=2)
    f_dc_t = font(F_SANS_B, 11)
    f_dc_b = font(F_SANS, 10)
    draw.text((x0 + 8, y + 5), "DATE CHECK", font=f_dc_t, fill=RED)
    hgt, _, _ = draw_wrapped(draw, x0 + 8, y + 21, DATE_CHECK, f_dc_b, CW - 16,
                             BODY, line_h=13, max_lines=3)
    y += 76

    # 10. Footer.
    f_src = font(F_SANS, 10)
    hgt, _, _ = draw_wrapped(draw, x0, y, FOOTER_SOURCES, f_src, CW, MUTED,
                             line_h=12, max_lines=2)
    yy = y + hgt + 2
    f_att = font(F_SANS, 10)
    draw.text((x0, yy), FOOTER_ATTEST, font=f_att, fill=MUTED)
    yy += 16
    draw.rectangle([x0, yy, x1, yy + 19], fill=DARKBAR)
    f_bar = font(F_SANS_B, 11)
    draw.text((x0 + 8, yy + 3), "THE WORLD IN ONE DAY", font=f_bar, fill=WHITE)
    rb = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    rw = text_w(draw, rb, f_bar)
    draw.text((x1 - 8 - rw, yy + 3), rb, font=f_bar, fill=WHITE)
    yy += 19
    return img, yy


def main():
    img, end_y = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("saved", out, "size", os.path.getsize(out), "end_y", end_y)


if __name__ == "__main__":
    main()
