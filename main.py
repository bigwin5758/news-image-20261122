#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Sunday 22 November 2026 (news-image-20261122).
Top-leaderboard format: 35 stories, number strip, region tabs, map with pins,
ALSO ON index, BY THE CLOCK, DATE CHECK. Stroke (vector) font, stdlib only.
"""
import os
import struct
import zlib
import math

W, H = 1024, 853

# ---------------- palette ----------------
PAPER   = (247, 241, 222)
INK     = (28, 28, 28)
RED     = (178, 34, 34)
DARKRED = (140, 22, 22)
NAVY    = (31, 58, 95)
TEAL    = (0, 110, 110)
GREY    = (110, 105, 90)
LGREY   = (200, 194, 175)
WHITE   = (255, 252, 245)
BOXBG   = (255, 253, 246)
WATER   = (214, 227, 237)
LAND    = (196, 203, 176)
LANDLN  = (160, 168, 140)
SKY     = (226, 233, 240)
GOLD    = (196, 148, 32)
ORANGE  = (224, 110, 20)
YELLOW  = (240, 200, 60)
DARK    = (38, 44, 58)

# ---------------- pixel buffer ----------------
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(W, int(x + w))
    y1 = min(H, int(y + h))
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def rect_outline(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def fill_circle(cx, cy, r, c):
    cx = int(cx)
    cy = int(cy)
    r = int(r)
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        y = cy + dy
        if 0 <= y < H:
            x0 = max(0, cx - dx)
            x1 = min(W - 1, cx + dx)
            base = (y * W + x0) * 3
            for xx in range(x0, x1 + 1):
                i = base + (xx - x0) * 3
                buf[i] = c[0]
                buf[i + 1] = c[1]
                buf[i + 2] = c[2]


def circle_outline(cx, cy, r, c, t=1):
    cx = int(cx)
    cy = int(cy)
    r = int(r)
    steps = max(24, int(2 * math.pi * r))
    for k in range(steps + 1):
        a = 2 * math.pi * k / steps
        px(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)
    if t > 1:
        for rr in range(r - t + 1, r):
            for k in range(steps + 1):
                a = 2 * math.pi * k / steps
                px(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), c)


def fill_poly(pts, c):
    """Scanline fill, even-odd rule. pts: list of (x, y)."""
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    y0 = max(0, int(math.ceil(min(ys))))
    y1 = min(H - 1, int(math.floor(max(ys))))
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1a = pts[i]
            x2, y2a = pts[(i + 1) % n]
            if (y1a <= y < y2a) or (y2a <= y < y1a):
                if y2a != y1a:
                    xs.append(x1 + (y - y1a) * (x2 - x1) / (y2a - y1a))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa = max(0, int(math.ceil(xs[k])))
            xb = min(W - 1, int(math.floor(xs[k + 1])))
            base = (y * W + xa) * 3
            for xx in range(xa, xb + 1):
                i = base + (xx - xa) * 3
                buf[i] = c[0]
                buf[i + 1] = c[1]
                buf[i + 2] = c[2]


def draw_line(x0, y0, x1, y1, c, w=1):
    """Thick line: quad + end caps. Thin line: Bresenham."""
    x0 = float(x0)
    y0 = float(y0)
    x1 = float(x1)
    y1 = float(y1)
    dx = x1 - x0
    dy = y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.01:
        fill_circle(x0, y0, max(1, w // 2), c)
        return
    if w <= 1:
        steps = int(L) + 1
        for k in range(steps + 1):
            t = k / steps
            px(int(round(x0 + dx * t)), int(round(y0 + dy * t)), c)
        return
    ux = dx / L
    uy = dy / L
    hw = w / 2.0
    nx = -uy * hw
    ny = ux * hw
    fill_poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
               (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], c)
    fill_circle(x0, y0, hw, c)
    fill_circle(x1, y1, hw, c)


def draw_polyline(pts, c, w=1):
    if len(pts) == 1:
        draw_line(pts[0][0], pts[0][1], pts[0][0], pts[0][1], c, w)
        return
    if w <= 1:
        for i in range(len(pts) - 1):
            draw_line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, 1)
        return
    # thick stroke: quad per segment, round caps only at the two ends
    # (no circles at interior joints -> no blobs on curves)
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dx = x1 - x0
        dy = y1 - y0
        L = math.hypot(dx, dy)
        if L < 0.01:
            continue
        ux = dx / L
        uy = dy / L
        hw = w / 2.0
        nx = -uy * hw
        ny = ux * hw
        fill_poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                   (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], c)
    fill_circle(pts[0][0], pts[0][1], w / 2.0, c)
    fill_circle(pts[-1][0], pts[-1][1], w / 2.0, c)


# ---------------- PNG encode ----------------
def write_png(path, w, h, data):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += data[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, payload):
        out = struct.pack(">I", len(payload)) + typ + payload
        out += struct.pack(">I", zlib.crc32(typ + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

# ---------------- stroke font (Hershey-simplex style) ----------------
# Glyph grid: x 0..7ish, y 0 (top) .. 10 (baseline), descenders to 13.
# Each glyph: (advance_units, [stroke, ...]); stroke = list of (x, y).
# Single-point strokes render as dots.
GLYPHS = {
    "A": (7.5, [[(0, 10), (3.75, 0), (7.5, 10)], [(2, 6.5), (5.5, 6.5)]]),
    "B": (7, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (4.5, 0), (6, 1.5), (6, 3.5), (4.5, 5), (0.5, 5)], [(0.5, 5), (4.5, 5), (6, 6.5), (6, 8.5), (4.5, 10), (0.5, 10)]]),
    "C": (7, [[(6, 1.5), (4, 0), (2, 0), (0.5, 1.5), (0.5, 8.5), (2, 10), (4, 10), (6, 8.5)]]),
    "D": (7.5, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (4, 0), (6.5, 2), (6.5, 8), (4, 10), (0.5, 10)]]),
    "E": (6.5, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (6, 0)], [(0.5, 5), (4.5, 5)], [(0.5, 10), (6, 10)]]),
    "F": (6.5, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (6, 0)], [(0.5, 5), (4.5, 5)]]),
    "G": (7.5, [[(6, 1.5), (4, 0), (2, 0), (0.5, 1.5), (0.5, 8.5), (2, 10), (4, 10), (6, 8.5), (6, 6), (3.5, 6)]]),
    "H": (7.5, [[(0.5, 0), (0.5, 10)], [(7, 0), (7, 10)], [(0.5, 5), (7, 5)]]),
    "I": (4, [[(2, 0), (2, 10)], [(0.5, 0), (3.5, 0)], [(0.5, 10), (3.5, 10)]]),
    "J": (6, [[(5, 0), (5, 8), (4, 10), (2, 10), (0.5, 8.5)]]),
    "K": (7, [[(0.5, 0), (0.5, 10)], [(6.5, 0), (0.5, 5)], [(2.5, 4), (6.5, 10)]]),
    "L": (6.5, [[(0.5, 0), (0.5, 10)], [(0.5, 10), (6, 10)]]),
    "M": (9, [[(0.5, 10), (0.5, 0), (4.5, 6), (8.5, 0), (8.5, 10)]]),
    "N": (8, [[(0.5, 10), (0.5, 0), (7.5, 10), (7.5, 0)]]),
    "O": (8, [[(4, 0), (6, 1), (7, 3), (7, 7), (6, 9), (4, 10), (2, 9), (1, 7), (1, 3), (2, 1), (4, 0)]]),
    "P": (7, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (4.5, 0), (6.5, 1.5), (6.5, 3.5), (4.5, 5), (0.5, 5)]]),
    "Q": (8, [[(4, 0), (6, 1), (7, 3), (7, 7), (6, 9), (4, 10), (2, 9), (1, 7), (1, 3), (2, 1), (4, 0)], [(5, 7), (7.5, 10.5)]]),
    "R": (7.5, [[(0.5, 0), (0.5, 10)], [(0.5, 0), (4.5, 0), (6.5, 1.5), (6.5, 3.5), (4.5, 5), (0.5, 5)], [(3, 5), (7, 10)]]),
    "S": (7, [[(6, 1.5), (4.5, 0), (2, 0), (0.5, 1.5), (0.5, 3.5), (2, 5), (4.5, 5), (6, 6.5), (6, 8.5), (4.5, 10), (2, 10), (0.5, 8.5)]]),
    "T": (7, [[(0.5, 0), (6.5, 0)], [(3.5, 0), (3.5, 10)]]),
    "U": (7.5, [[(0.5, 0), (0.5, 8), (2, 10), (5, 10), (6.5, 8), (6.5, 0)]]),
    "V": (7.5, [[(0.5, 0), (3.75, 10), (7, 0)]]),
    "W": (10, [[(0.5, 0), (2.5, 10), (5, 4), (7.5, 10), (9.5, 0)]]),
    "X": (7.5, [[(0.5, 0), (7, 10)], [(7, 0), (0.5, 10)]]),
    "Y": (7, [[(0.5, 0), (3.5, 5), (6.5, 0)], [(3.5, 5), (3.5, 10)]]),
    "Z": (7, [[(0.5, 0), (6.5, 0), (0.5, 10), (6.5, 10)]]),
    # lowercase: single-storey a/g (oval + stem / oval + hook) for clean, regular shapes
    "a": (6.5, [[(3.25, 4.5), (5, 5.5), (5.5, 7.5), (5, 9), (3.25, 10), (1.5, 9), (1, 7.5), (1.5, 5.5), (3.25, 4.5)], [(5.5, 4.5), (5.5, 10)]]),
    "b": (6.5, [[(1, 0), (1, 10)], [(1, 7), (2.5, 4.5), (4, 4.5), (5, 6), (5, 8.5), (4, 10), (2.5, 10), (1, 8)]]),
    "c": (6, [[(5.5, 5.5), (4, 4.5), (2, 4.5), (1, 6), (1, 8.5), (2, 10), (4, 10), (5.5, 8.5)]]),
    "d": (6.5, [[(5.5, 0), (5.5, 10)], [(5.5, 7), (4, 4.5), (2, 4.5), (1, 6), (1, 8.5), (2, 10), (4, 10), (5.5, 8)]]),
    "e": (6.5, [[(3.25, 4.5), (5, 5.5), (5.5, 7.5), (5, 9), (3.25, 10), (1.5, 9), (1, 7.5), (1.5, 5.5), (3.25, 4.5)], [(1, 7), (5.5, 7)]]),
    "f": (5.5, [[(3.5, 1), (2.5, 0), (1.5, 0.5), (1, 2), (1, 10)], [(1, 5), (4, 5)]]),
    "g": (6.5, [[(3.25, 4.5), (5, 5.5), (5.5, 7.5), (5, 9), (3.25, 10), (1.5, 9), (1, 7.5), (1.5, 5.5), (3.25, 4.5)], [(5, 9), (5, 12), (4, 13), (2, 13), (1, 12)]]),
    "h": (6.5, [[(1, 0), (1, 10)], [(1, 7), (2.5, 4.5), (4, 4.5), (5, 5.5), (5, 10)]]),
    "i": (3.5, [[(1.75, 4.5), (1.75, 10)], [(1.75, 1.5)]]),
    "j": (4, [[(2.5, 4.5), (2.5, 11), (2, 12.5), (0.5, 12.5)], [(2.5, 1.5)]]),
    "k": (6.5, [[(1, 0), (1, 10)], [(5.5, 4.5), (1, 7.5)], [(3, 6), (5.5, 10)]]),
    "l": (3.5, [[(1.75, 0), (1.75, 10)]]),
    "m": (9.5, [[(1, 10), (1, 4.5)], [(1, 7), (2, 4.5), (3.5, 4.5), (4.5, 5.5), (4.5, 10)], [(4.5, 7), (5.5, 4.5), (7, 4.5), (8, 5.5), (8, 10)]]),
    "n": (6.5, [[(1, 10), (1, 4.5)], [(1, 7), (2.5, 4.5), (4, 4.5), (5, 5.5), (5, 10)]]),
    "o": (6.5, [[(3.25, 4.5), (5, 5.5), (5.5, 7.5), (5, 9), (3.25, 10), (1.5, 9), (1, 7.5), (1.5, 5.5), (3.25, 4.5)]]),
    "p": (6.5, [[(1, 4.5), (1, 13)], [(1, 7), (2.5, 4.5), (4, 4.5), (5, 6), (5, 8.5), (4, 10), (2.5, 10), (1, 8)]]),
    "q": (6.5, [[(5.5, 4.5), (5.5, 13)], [(5.5, 7), (4, 4.5), (2, 4.5), (1, 6), (1, 8.5), (2, 10), (4, 10), (5.5, 8)]]),
    "r": (5, [[(1, 10), (1, 4.5)], [(1, 6.5), (2, 4.5), (3.5, 4.5), (4.5, 5.5), (4.5, 7)]]),
    "s": (6, [[(5, 5.5), (3.5, 4.5), (2, 4.5), (1, 5.5), (1, 7), (2, 7.5), (4, 7.5), (5, 8.5), (5, 9.5), (3.5, 10), (2, 10), (1, 9)]]),
    "t": (5, [[(2.5, 0), (2.5, 9), (3, 10), (4.5, 10)], [(1, 5), (4.5, 5)]]),
    "u": (6.5, [[(1, 4.5), (1, 8.5), (2.5, 10), (4, 10), (5, 8.5), (5, 4.5)]]),
    "v": (6.5, [[(1, 4.5), (3.25, 10), (5.5, 4.5)]]),
    "w": (9.5, [[(0.5, 4.5), (2, 10), (4.75, 6), (7.5, 10), (9, 4.5)]]),
    "x": (6.5, [[(1, 4.5), (5.5, 10)], [(5.5, 4.5), (1, 10)]]),
    "y": (6.5, [[(1, 4.5), (3.25, 10), (5.5, 4.5)], [(3.25, 10), (3, 12.5), (2, 13), (1, 12)]]),
    "z": (6, [[(1, 4.5), (5, 4.5), (1, 10), (5, 10)]]),
    "0": (7, [[(3.5, 0), (5.5, 1), (6.5, 3), (6.5, 7), (5.5, 9), (3.5, 10), (1.5, 9), (0.5, 7), (0.5, 3), (1.5, 1), (3.5, 0)]]),
    "1": (4.5, [[(2.25, 0), (2.25, 10)], [(1, 2.5), (2.25, 0)], [(1, 10), (3.5, 10)]]),
    "2": (7, [[(1, 2), (2, 0.5), (4, 0), (5.5, 1), (6, 3), (6, 4.5), (4, 6.5), (1, 10), (6, 10)]]),
    "3": (7, [[(1, 1.5), (2.5, 0), (4.5, 0), (6, 1.5), (6, 3.5), (4.5, 5), (6, 5.5), (6, 8), (4.5, 10), (2.5, 10), (1, 8.5)]]),
    "4": (7, [[(5, 0), (5, 10)], [(0.5, 7), (6.5, 7)], [(5, 0), (0.5, 7)]]),
    "5": (7, [[(6, 0), (1, 0), (1, 4.5), (4, 4.5), (6, 6), (6, 8.5), (4.5, 10), (2, 10), (1, 9)]]),
    "6": (7, [[(5.5, 1), (4, 0), (2, 0.5), (1, 2.5), (1, 7), (2, 9.5), (4, 10), (5.5, 9), (6, 7), (5, 5.5), (3, 5.5), (1.5, 6.5)]]),
    "7": (7, [[(0.5, 0), (6.5, 0), (3.5, 10)]]),
    "8": (7, [[(2, 5), (1, 3.5), (1.5, 1.5), (3, 0), (4.5, 0), (6, 1.5), (6, 3.5), (5, 5), (2, 5)], [(2, 5), (1, 6.5), (1.5, 8.5), (3, 10), (4.5, 10), (6, 8.5), (6, 6.5), (5, 5)]]),
    "9": (7, [[(1.5, 6), (1, 4.5), (2, 3), (4, 3), (5.5, 4), (6, 6), (5, 7.5), (3, 8), (1.5, 6)], [(6, 4), (5.5, 8), (4, 10), (2, 10)]]),
    " ": (3.5, []),
    ".": (3.5, [[(1.75, 9.5)]]),
    ",": (3.5, [[(1.75, 9.5), (1.25, 11.5), (0.75, 12.5)]]),
    ":": (3.5, [[(1.75, 4)], [(1.75, 8)]]),
    ";": (3.5, [[(1.75, 4)], [(1.75, 7.5), (1.25, 10), (0.75, 11.5)]]),
    "!": (3.5, [[(1.75, 0), (1.75, 7)], [(1.75, 9.5)]]),
    "?": (6.5, [[(1.5, 2), (2.5, 0.5), (4.5, 0.5), (5.5, 2), (5.5, 3.5), (4.5, 5), (3.25, 5.5), (3.25, 7)], [(3.25, 9.5)]]),
    "'": (3, [[(2, 0), (1.5, 2.5)]]),
    "\u2019": (3, [[(2, 0), (1.5, 2.5)]]),
    "\u2018": (3, [[(1, 0), (1.5, 2.5)]]),
    '"': (5, [[(1.5, 0), (1, 2.5)], [(4, 0), (3.5, 2.5)]]),
    "\u201c": (5, [[(1.5, 0), (1, 2.5)], [(4, 0), (3.5, 2.5)]]),
    "\u201d": (5, [[(1, 0), (1.5, 2.5)], [(3.5, 0), (4, 2.5)]]),
    "(": (4, [[(3.5, 0), (2, 2.5), (2, 7.5), (3.5, 10)]]),
    ")": (4, [[(0.5, 0), (2, 2.5), (2, 7.5), (0.5, 10)]]),
    "%": (9, [[(1, 0), (8, 10)], [(2.5, 1), (1.5, 1), (1, 2), (1.5, 3), (2.5, 3), (3, 2), (2.5, 1)], [(6.5, 7), (5.5, 7), (5, 8), (5.5, 9), (6.5, 9), (7, 8), (6.5, 7)]]),
    "-": (5, [[(1, 5), (4, 5)]]),
    "\u2013": (6, [[(0.5, 5), (5.5, 5)]]),
    "\u2014": (8, [[(0.5, 5), (7.5, 5)]]),
    "/": (4, [[(1, 10), (3, 0)]]),
    "$": (7, [[(3.5, 0), (3.5, 10)], [(5.5, 2), (4, 0.5), (2, 0.5), (1, 2), (1, 3.5), (2.5, 5), (4.5, 5), (6, 6.5), (6, 8), (4.5, 10), (2, 10), (1, 8.5)]]),
    "\u20ac": (7, [[(6, 1.5), (4, 0), (1.5, 0), (0, 2), (0, 8), (1.5, 10), (4, 10), (6, 8.5)], [(0.5, 4), (5, 4)], [(0.5, 6.5), (5, 6.5)]]),
    "&": (8, [[(4.5, 0.5), (2.5, 0.5), (1, 2), (1, 4), (2.5, 5.5), (5, 5.5), (6, 7), (5.5, 8.5), (4, 9.5), (2, 9.5), (1, 8.5)], [(6, 5.5), (1, 10)]]),
    "+": (6.5, [[(3.25, 1.5), (3.25, 8.5)], [(1, 5), (5.5, 5)]]),
    "=": (6.5, [[(1, 3.5), (5.5, 3.5)], [(1, 6.5), (5.5, 6.5)]]),
    "~": (6.5, [[(1, 6), (2.5, 4), (4, 6), (5.5, 4), (6, 6)]]),
    "\u00b7": (3.5, [[(1.75, 4.5)]]),
    "\u00d7": (6.5, [[(1, 2), (5.5, 8)], [(5.5, 2), (1, 8)]]),
    "#": (7, [[(2.5, 0), (2, 10)], [(4.5, 0), (4, 10)], [(0.5, 3.5), (6.5, 3.5)], [(0.5, 6.5), (6.5, 6.5)]]),
}

FALLBACK = (7, [[(0.5, 0), (6.5, 0), (6.5, 10), (0.5, 10), (0.5, 0)]])


def glyph_of(ch):
    return GLYPHS.get(ch, FALLBACK)


def text_w(s, scale):
    w = 0.0
    for ch in s:
        w += glyph_of(ch)[0] * scale
    return w


def draw_text(x, y, s, scale, color, bold=False):
    """Draw text; (x, y) is the top-left of the cap-height box."""
    lw = max(1, int(round(scale * 1.5))) if bold else max(1, int(round(scale * 1.0)))
    cx = float(x)
    for ch in s:
        adv, strokes = glyph_of(ch)
        for st in strokes:
            pts = [(cx + px_ * scale, y + py * scale) for (px_, py) in st]
            if len(pts) == 1:
                fill_circle(pts[0][0], pts[0][1], max(1, lw // 2 + 1), color)
            else:
                draw_polyline(pts, color, lw)
        cx += adv * scale
    return cx


def wrap_text(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w) if cur else w
        if text_w(t, scale) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            # long single word: split by chars
            while text_w(w, scale) > max_w:
                cut = 1
                while cut < len(w) and text_w(w[:cut + 1], scale) <= max_w:
                    cut += 1
                lines.append(w[:cut])
                w = w[cut:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_block(x, y, lines, scale, color, bold=False, lh=None):
    if lh is None:
        lh = int(round(scale * 13.5))
    for ln in lines:
        draw_text(x, y, ln, scale, color, bold)
        y += lh
    return y

# ---------------- illustration helpers ----------------
def flame(x, y, w, h, c1=ORANGE, c2=YELLOW):
    """Simple flame: stacked triangles in two colours."""
    hw = w / 2.0
    fill_poly([(x, y + h), (x + hw * 0.25, y + h * 0.45), (x + hw * 0.55, y + h * 0.7),
               (x + hw * 0.8, y), (x + hw * 1.1, y + h * 0.55), (x + hw * 1.6, y + h * 0.35),
               (x + hw * 1.85, y + h * 0.6), (x + w, y + h)], c1)
    fill_poly([(x + hw * 0.5, y + h), (x + hw * 0.75, y + h * 0.55), (x + hw * 1.0, y + h * 0.35),
               (x + hw * 1.25, y + h * 0.6), (x + hw * 1.5, y + h)], c2)


def smoke(x, y, r, c=(150, 150, 150)):
    fill_circle(x, y, r, c)
    fill_circle(x + r, y - r * 0.5, int(r * 0.8), c)
    fill_circle(x - r, y - r * 0.4, int(r * 0.7), c)


def skyline(x, y, w, h, c=DARK):
    """Night skyline: dark buildings with lit windows."""
    bw = w / 6.0
    heights = [0.55, 0.8, 0.45, 0.95, 0.6, 0.75]
    for i in range(6):
        bh = h * heights[i]
        bx = x + i * bw
        fill_rect(bx + 1, y + h - bh, bw - 2, bh, c)
        # lit windows
        for wy in range(int(y + h - bh + 4), int(y + h - 4), 7):
            for wx in (bx + 3, bx + bw - 7):
                if (i * 7 + int(wy)) % 3 == 0:
                    fill_rect(wx, wy, 3, 3, YELLOW)


def missile_streak(x0, y0, x1, y1, c=ORANGE):
    draw_line(x0, y0, x1, y1, c, 2)
    fill_circle(x1, y1, 3, YELLOW)
    fill_circle(x1, y1, 1, WHITE)


def globe(cx, cy, r, c=TEAL):
    fill_circle(cx, cy, r, (200, 225, 230))
    circle_outline(cx, cy, r, c, 2)
    draw_line(cx - r, cy, cx + r, cy, c, 1)
    # meridian ellipses (front half)
    for rx in (r * 0.55, r * 0.25):
        steps = 28
        for i in range(steps + 1):
            a = -math.pi / 2 + math.pi * i / steps
            px(int(cx + rx * math.cos(a)), int(cy + r * math.sin(a)), c)
            px(int(cx - rx * math.cos(a)), int(cy + r * math.sin(a)), c)


def doc_icon(x, y, w, h, c=WHITE, ln=GREY):
    fill_rect(x, y, w, h, c)
    rect_outline(x, y, w, h, INK, 1)
    for i in range(3):
        draw_line(x + 3, y + 5 + i * 5, x + w - 3, y + 5 + i * 5, ln, 1)


def thermometer(x, y, w, h, c=RED):
    fill_rect(x + w // 2 - 2, y, 4, h - 4, c)
    fill_circle(x + w // 2, y + h - 3, 4, c)
    circle_outline(x + w // 2, y + h - 3, 4, DARKRED, 1)


def ship_icon(x, y, w, h, c=DARK):
    # hull
    fill_poly([(x, y + h * 0.4), (x + w, y + h * 0.4), (x + w * 0.85, y + h), (x + w * 0.15, y + h)], c)
    # containers
    fill_rect(x + w * 0.15, y, w * 0.2, h * 0.35, RED)
    fill_rect(x + w * 0.4, y, w * 0.2, h * 0.35, GOLD)
    fill_rect(x + w * 0.65, y, w * 0.2, h * 0.35, TEAL)


def truck_icon(x, y, w, h, c=(210, 210, 210)):
    fill_rect(x, y + h * 0.2, w * 0.65, h * 0.55, c)
    rect_outline(x, y + h * 0.2, w * 0.65, h * 0.55, INK, 1)
    fill_rect(x + w * 0.65, y + h * 0.35, w * 0.3, h * 0.4, c)
    rect_outline(x + w * 0.65, y + h * 0.35, w * 0.3, h * 0.4, INK, 1)
    fill_circle(x + w * 0.2, y + h * 0.85, h * 0.15, INK)
    fill_circle(x + w * 0.8, y + h * 0.85, h * 0.15, INK)
    fill_rect(x + w * 0.1, y + h * 0.3, w * 0.45, h * 0.35, WHITE)
    draw_line(x + w * 0.1, y + h * 0.3, x + w * 0.55, y + h * 0.65, RED, 2)
    draw_line(x + w * 0.55, y + h * 0.3, x + w * 0.1, y + h * 0.65, RED, 2)


def bolt(x, y, w, h, c=YELLOW):
    fill_poly([(x + w * 0.55, y), (x + w * 0.15, y + h * 0.55), (x + w * 0.45, y + h * 0.55),
               (x + w * 0.35, y + h), (x + w * 0.85, y + h * 0.4), (x + w * 0.55, y + h * 0.4)], c)


def badge_star(cx, cy, r, c=GOLD):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    fill_poly(pts, c)


def sub_icon(x, y, w, h, c=NAVY):
    fill_poly([(x, y + h * 0.35), (x + w * 0.15, y + h * 0.2), (x + w * 0.8, y + h * 0.2),
               (x + w, y + h * 0.35), (x + w, y + h * 0.6), (x + w * 0.85, y + h * 0.75),
               (x + w * 0.15, y + h * 0.75), (x, y + h * 0.6)], c)
    fill_rect(x + w * 0.55, y, w * 0.15, h * 0.25, c)
    draw_line(x + w * 0.62, y, x + w * 0.62, y - h * 0.2, c, 1)


def building_icon(x, y, w, h, c=GREY):
    fill_rect(x, y + h * 0.25, w, h * 0.75, c)
    fill_poly([(x, y + h * 0.25), (x + w / 2, y), (x + w, y + h * 0.25)], c)
    for i in range(3):
        fill_rect(x + w * 0.15 + i * w * 0.3, y + h * 0.45, w * 0.12, h * 0.4, WHITE)


def magnifier(x, y, r, c=NAVY):
    circle_outline(x, y, r, c, 2)
    draw_line(x + r * 0.7, y + r * 0.7, x + r * 1.5, y + r * 1.5, c, 2)


# ---------------- world map ----------------
# Rough continent polygons in (lon, lat)
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-75, 62), (-60, 47), (-55, 45), (-70, 42), (-75, 35), (-80, 32), (-85, 30), (-90, 21), (-95, 18), (-105, 20), (-110, 23), (-120, 34), (-125, 40), (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -50), (-70, -35), (-72, -20), (-78, -10), (-80, 5)],
    [(-10, 36), (-5, 44), (0, 48), (5, 53), (8, 57), (12, 55), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65), (20, 70), (15, 70), (10, 64), (5, 60), (0, 55), (-5, 50), (-10, 43)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30), (20, -35), (15, -30), (12, -18), (9, -5), (9, 5), (0, 5), (-8, 5), (-15, 10)],
    [(30, 62), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (160, 55), (150, 45), (140, 40), (130, 35), (127, 35), (122, 30), (115, 25), (108, 18), (105, 10), (100, 8), (95, 15), (90, 20), (85, 20), (80, 10), (75, 8), (70, 20), (65, 25), (60, 25), (55, 26), (50, 30), (45, 30), (40, 35), (35, 36), (30, 40), (28, 45), (30, 55)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32), (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -25), (145, -20), (142, -15), (140, -12), (135, -12), (130, -13), (125, -15), (120, -20), (115, -22)],
]

# story pins: number -> (lat, lon, dx, dy) offset in px for crowded pins
PINS = {
    1: (36.9, 30.7, 0, 0),
    2: (50.4, 30.5, 0, 0),
    3: (26.2, 50.6, 0, 0),
    4: (60.0, 27.0, 0, -9),
    5: (47.9, 33.4, -13, 9),
    6: (4.9, 6.3, 0, 0),
    7: (31.8, 35.2, -11, -8),
    8: (31.5, 34.5, 11, 9),
    9: (25.0, -108.0, 0, 0),
    10: (35.7, 51.4, 0, 0),
    11: (38.9, -77.0, 0, 0),
    12: (-15.8, -47.9, 0, 0),
    13: (-35.3, 149.1, 0, 0),
}


def draw_map(mx, my, mw, mh):
    fill_rect(mx, my, mw, mh, WATER)
    rect_outline(mx, my, mw, mh, LGREY, 1)
    lon0, lon1 = -170.0, 190.0
    lat0, lat1 = 72.0, -58.0

    def proj(lon, lat):
        x = mx + (lon - lon0) / (lon1 - lon0) * mw
        y = my + (lat0 - lat) / (lat0 - lat1) * mh
        return (x, y)

    for poly in CONTINENTS:
        fill_poly([proj(lon, lat) for (lon, lat) in poly], LAND)
    # pin true positions (small dots) + offset pins with leader lines
    for num in sorted(PINS):
        lat, lon, dx, dy = PINS[num]
        tx, ty = proj(lon, lat)
        px_, py_ = tx + dx, ty + dy
        if dx or dy:
            draw_line(tx, ty, px_, py_, RED, 1)
        fill_circle(tx, ty, 1, RED)
        fill_circle(px_, py_, 7, RED)
        circle_outline(px_, py_, 7, WHITE, 1)
        draw_text(px_ - text_w(str(num), 0.9) / 2, py_ - 5, str(num), 0.9, WHITE, bold=True)

# ---------------- story data (spec v2, verbatim) ----------------
HEROES = [
    (1, "ANTALYA, TURKEY \u00b7 CLIMATE", "COP31: DEAL CLOSE",
     "COP31 climate talks close in on a final deal",
     "A new package lands after a fight over fossil fuels; delegations have until 03:00 GMT to object before a final plenary. (Reuters, BBC)",
     "cop31"),
    (2, "KYIV, UKRAINE \u00b7 WAR", "UKRAINE: BARRAGE",
     "Russia fires 400 drones and 110 missiles",
     "One of the war's largest overnight attacks; at least seven people are killed in Kyiv. (Al Jazeera)",
     "kyiv"),
    (3, "MANAMA, BAHRAIN \u00b7 IRAN WAR", "BAHRAIN: STRUCK",
     "Iran strikes US bases in Bahrain",
     "An industrial site burns, no injuries; tankers are hit in Hormuz. (Al Jazeera, CNA)",
     "bahrain"),
]

GRID = [
    (4, "GULF OF FINLAND", "SHIP ABLAZE", "Russian cargo ship burns after drone strike",
     "Finland says Ukraine was likely behind it. (BBC)", "ship"),
    (5, "KRYVYI RIH", "2 DEAD, 60 HURT", "Strike hits Zelenskyy's home city",
     "Russian strike on the central Ukrainian city. (Al Jazeera)", "blast"),
    (6, "BAYELSA, NIGERIA", "24 DEAD", "Boat carrying mourners capsizes",
     "Passengers were going to a funeral. (DW, Sky News)", "boat"),
    (7, "JERUSALEM", "COALITION TALKS", "Eisenkot invites Likud to talks",
     "He seeks the broadest possible government. (Straits Times)", "talks"),
    (8, "GAZA", "3 KILLED", "Strike hits food aid vehicle",
     "Three Palestinians die in an air attack. (Al Jazeera, Reuters)", "truck"),
    (9, "SINALOA, MEXICO", "11 DEAD", "'El Chapo Isidro' caught; violence follows",
     "FBI top-ten fugitive held after a shoot-out. (Sky News, BBC)", "badge"),
    (10, "TEHRAN, IRAN", "POWER CUTS", "Iran to ration electricity",
     "War damage hits the energy network. (Straits Times)", "bolt"),
    (11, "WASHINGTON", "SEC PROBE", "Nvidia faces US accounting probe",
     "The SEC inquiry is at an early stage. (Straits Times)", "mag"),
    (12, "BRASILIA, BRAZIL", "BOLSONARO: ICU", "Bolsonaro in intensive care",
     "Ex-president stable, breathing on his own. (Al Jazeera, Reuters)", "cross"),
    (13, "CANBERRA", "AUKUS ROW", "Marles rejects US report on AUKUS subs",
     "He says the budget office is wrong. (ABC, Reuters)", "sub"),
]

BRIEFS = [
    (14, "US: FBI looks into apparent hack of its crime database. (BBC)"),
    (15, "US: Teen gamer and his mother help FBI rescue a girl. (BBC)"),
    (16, "US: Midterm loss corners Vance as 2028 field widens. (ST)"),
    (17, "Saudi Arabia: Air defences down a missile. (Investing.com)"),
    (18, "Lebanon: Aoun demands Israeli withdrawal. (Al Jazeera)"),
    (19, "Iran: President warns of a 'silent economic war'. (Al Jazeera)"),
    (20, "Hormuz: Lewis Pugh swims strait as tanker is struck. (BBC)"),
    (21, "Moldova: Reports a Russian airspace breach. (Kyiv Ind.)"),
    (22, "Belgium: Air traffic to halt in 23 Nov national strike. (ST)"),
    (23, "Germany: IG Metall widens car and shipyard strikes. (Reuters)"),
    (24, "Portugal: Thousands march in Lisbon on living costs. (Reuters)"),
    (25, "Denmark: Expels Russian attache over rapper plot. (Guardian)"),
    (26, "Bangladesh: 30 Awami League homes set on fire. (TOI)"),
    (27, "Australia: Fred Nile, ex-NSW MP, dies aged 92. (ABC)"),
    (28, "Australia: Bystanders pull driver from burning car. (ABC)"),
    (29, "Melbourne: 70 years since the 1956 Olympics opened. (ABC)"),
    (30, "Trade: EU and Indonesia sign deal after 10 years. (DW)"),
    (31, "Rugby: England beat New Zealand 37-12. (Reuters)"),
    (32, "Rugby: France beat Argentina to reach the final. (Reuters)"),
    (33, "Football: Arsenal 2-2 Newcastle. (Reuters)"),
    (34, "Football: Liverpool host Manchester United today. (Al Jazeera)"),
    (35, "Tennis: Zverev v Alcaraz in today's ATP Finals final. (TOI)"),
]

NUMBERS = [
    ("~200", "nations at the COP31 talks"),
    ("03:00", "GMT deadline for objections"),
    ("400+", "drones fired at Ukraine"),
    ("110", "missiles in the same night"),
    ("7+", "people killed in Kyiv"),
    ("2", "US bases targeted in Bahrain"),
]

REGIONS = [("EUROPE", 11), ("MIDDLE EAST", 8), ("AMERICAS", 6),
           ("ASIA-PACIFIC", 5), ("AFRICA", 1), ("WORLD", 4)]

CLOCK_ITEMS = ("UTC Sat 07:35 Sparta II fire reported \u00b7 "
               "Sat 12:08 Mexico announces capture \u00b7 "
               "03:00 GMT COP31 objection deadline \u00b7 "
               "Sun 10:00 COP31 plenary reconvenes")

DATE_CHECK_LINES = [
    "Wires read to Sunday 22 November 2026. Every story was reported or still developing on 22 November.",
    "LEFT OUT as other days' news: Peru earthquake (20 Nov local) \u00b7 Russian missiles in Poland (19 Nov) \u00b7 Kerch Bridge",
    "strikes (earlier this week) \u00b7 Shenzhen summit (19 Nov) \u00b7 GTA VI launch (19 Nov) \u00b7 Anthropic IPO debut (19 Nov) \u00b7 Wall Street correction (20 Nov).",
]

FOOTER_SRC = ("Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, CNA, ABC Australia, Times of India, "
              "The Guardian, Kyiv Independent. Every story names its outlet. Pictures and map: original, drawn in code.")


def tag_box(x, y, text, scale=0.9):
    tw = text_w(text, scale) + 10
    fill_rect(x, y, tw, 14, RED)
    draw_text(x + 5, y + 2, text, scale, WHITE, bold=True)
    return tw


def num_badge(x, y, num, r=11):
    fill_circle(x, y, r, RED)
    circle_outline(x, y, r, WHITE, 1)
    s = str(num)
    sc = 1.2 if r >= 11 else 0.9
    draw_text(x - text_w(s, sc) / 2, y - 5 * sc, s, sc, WHITE, bold=True)


def draw_illus(kind, x, y, w, h):
    if kind == "cop31":
        fill_rect(x, y, w, h, SKY)
        # summit table with delegates (fills the panel like the top entries)
        fill_rect(x + w * 0.05, y + h * 0.62, w * 0.9, h * 0.12, (120, 85, 50))
        fill_rect(x + w * 0.05, y + h * 0.62, w * 0.9, 2, (90, 60, 35))
        for i, dc in enumerate((RED, TEAL, GOLD, NAVY, ORANGE, (90, 140, 60))):
            px_ = x + w * (0.10 + i * 0.15)
            fill_circle(px_, y + h * 0.52, 5, dc)
            fill_rect(px_ - 4, y + h * 0.56, 8, h * 0.08, dc)
        globe(x + w * 0.13, y + h * 0.26, h * 0.20)
        doc_icon(x + w * 0.36, y + 4, w * 0.24, h * 0.38)
        thermometer(x + w * 0.66, y + 4, 7, h * 0.38)
        # wall clock
        fill_circle(x + w * 0.84, y + h * 0.24, 7, WHITE)
        circle_outline(x + w * 0.84, y + h * 0.24, 7, INK, 1)
        draw_line(x + w * 0.84, y + h * 0.24, x + w * 0.84 + 4, y + h * 0.24 - 3, INK, 1)
        draw_line(x + w * 0.84, y + h * 0.24, x + w * 0.84, y + h * 0.24 + 4, INK, 1)
    elif kind == "kyiv":
        fill_rect(x, y, w, h, (28, 36, 60))
        skyline(x + 2, y + h * 0.25, w - 4, h * 0.75)
        missile_streak(x + w * 0.55, y + 4, x + w * 0.30, y + h * 0.55)
        missile_streak(x + w * 0.85, y + 8, x + w * 0.65, y + h * 0.5)
        missile_streak(x + w * 0.95, y + 2, x + w * 0.80, y + h * 0.42)
        flame(x + w * 0.15, y + h - 12, w * 0.2, 12)
        flame(x + w * 0.6, y + h - 10, w * 0.16, 10)
    elif kind == "bahrain":
        fill_rect(x, y, w, h, (240, 226, 200))
        fill_rect(x + w * 0.06, y + h * 0.45, w * 0.22, h * 0.55, (120, 120, 120))
        fill_rect(x + w * 0.32, y + h * 0.30, w * 0.16, h * 0.70, (100, 100, 100))
        fill_rect(x + w * 0.52, y + h * 0.55, w * 0.26, h * 0.45, (140, 140, 140))
        smoke(x + w * 0.40, y + h * 0.18, 6)
        smoke(x + w * 0.62, y + h * 0.30, 5)
        flame(x + w * 0.10, y + h * 0.38, w * 0.18, h * 0.25)
        flame(x + w * 0.55, y + h * 0.48, w * 0.16, h * 0.22)
        ship_icon(x + w * 0.70, y + h - 14, w * 0.26, 12)
    elif kind == "ship":
        fill_rect(x, y, w, h, SKY)
        ship_icon(x + w * 0.08, y + h * 0.35, w * 0.6, h * 0.55)
        flame(x + w * 0.62, y + h * 0.15, w * 0.3, h * 0.5)
        smoke(x + w * 0.75, y + 3, 4)
    elif kind == "blast":
        fill_rect(x, y, w, h, (250, 230, 200))
        badge_star(x + w * 0.5, y + h * 0.5, h * 0.42, ORANGE)
        badge_star(x + w * 0.5, y + h * 0.5, h * 0.25, YELLOW)
        smoke(x + w * 0.15, y + h * 0.25, 4)
        smoke(x + w * 0.85, y + h * 0.7, 4)
    elif kind == "boat":
        fill_rect(x, y, w, h, SKY)
        fill_poly([(x + w * 0.15, y + h * 0.35), (x + w * 0.85, y + h * 0.25),
                   (x + w * 0.75, y + h * 0.6), (x + w * 0.25, y + h * 0.65)], (120, 90, 60))
        draw_line(x, y + h * 0.75, x + w, y + h * 0.75, TEAL, 2)
        draw_line(x, y + h * 0.88, x + w, y + h * 0.88, TEAL, 2)
    elif kind == "talks":
        fill_rect(x, y, w, h, SKY)
        building_icon(x + w * 0.08, y + h * 0.15, w * 0.4, h * 0.75)
        fill_rect(x + w * 0.58, y + h * 0.1, w * 0.34, h * 0.45, WHITE)
        rect_outline(x + w * 0.58, y + h * 0.1, w * 0.34, h * 0.45, INK, 1)
        fill_poly([(x + w * 0.62, y + h * 0.55), (x + w * 0.62, y + h * 0.75), (x + w * 0.72, y + h * 0.55)], WHITE)
    elif kind == "truck":
        fill_rect(x, y, w, h, SKY)
        truck_icon(x + w * 0.08, y + h * 0.1, w * 0.84, h * 0.85)
    elif kind == "badge":
        fill_rect(x, y, w, h, SKY)
        badge_star(x + w * 0.5, y + h * 0.5, h * 0.42, GOLD)
        fill_circle(x + w * 0.5, y + h * 0.5, h * 0.18, NAVY)
        draw_text(x + w * 0.5 - text_w("9", 0.8) / 2, y + h * 0.5 - 4, "9", 0.8, WHITE, bold=True)
    elif kind == "bolt":
        fill_rect(x, y, w, h, (250, 240, 200))
        bolt(x + w * 0.35, y + 2, w * 0.3, h - 4)
        fill_rect(x + w * 0.68, y + h * 0.55, w * 0.2, h * 0.3, DARK)
    elif kind == "mag":
        fill_rect(x, y, w, h, SKY)
        magnifier(x + w * 0.42, y + h * 0.42, h * 0.3)
        draw_text(x + w * 0.72, y + h * 0.3, "$", 1.0, DARKRED, bold=True)
    elif kind == "cross":
        fill_rect(x, y, w, h, WHITE)
        fill_rect(x + w * 0.44, y + h * 0.1, w * 0.12, h * 0.8, RED)
        fill_rect(x + w * 0.2, y + h * 0.34, w * 0.6, h * 0.32, RED)
    elif kind == "sub":
        fill_rect(x, y, w, h, SKY)
        sub_icon(x + w * 0.08, y + h * 0.25, w * 0.84, h * 0.55)
    else:
        fill_rect(x, y, w, h, SKY)

# ---------------- layout ----------------
def draw_hero(x, y, w, h, num, place, tag, headline, summary, kind):
    fill_rect(x, y, w, h, BOXBG)
    rect_outline(x, y, w, h, LGREY, 1)
    draw_illus(kind, x + 1, y + 1, w - 2, 46)
    num_badge(x + 16, y + 16, num, r=11)
    tag_box(x + 10, y + 50, tag, 0.9)
    draw_text(x + 10, y + 68, place, 1.0, NAVY, bold=True)
    hl = wrap_text(headline, 1.4, w - 20)
    yy = draw_block(x + 10, y + 82, hl, 1.4, INK, bold=True, lh=18)
    sm = wrap_text(summary, 1.0, w - 20)
    draw_block(x + 10, yy + 2, sm, 1.0, INK, lh=13)


def draw_grid_cell(x, y, w, h, num, place, tag, headline, summary, kind):
    fill_rect(x, y, w, h, BOXBG)
    rect_outline(x, y, w, h, LGREY, 1)
    draw_illus(kind, x + 1, y + 1, w - 2, 28)
    num_badge(x + 11, y + 11, num, r=8)
    tag_box(x + 6, y + 32, tag, 0.8)
    draw_text(x + 6, y + 48, place, 0.85, NAVY, bold=True)
    hl = wrap_text(headline, 1.05, w - 12)
    yy = draw_block(x + 6, y + 60, hl, 1.05, INK, bold=True, lh=14)
    sm = wrap_text(summary, 0.9, w - 12)
    draw_block(x + 6, yy + 2, sm, 0.9, INK, lh=12)


def build():
    fill_rect(0, 0, W, H, PAPER)
    # (a) title row
    draw_text(12, 8, "THE WORLD IN ONE DAY", 3.0, INK, bold=True)
    r1 = "35 STORIES \u00b7 6 REGIONS"
    draw_text(1012 - text_w(r1, 0.9), 10, r1, 0.9, INK, bold=True)
    r2 = "EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    draw_text(1012 - text_w(r2, 0.9), 24, r2, 0.9, GREY, bold=True)
    fill_rect(12, 46, 1000, 2, RED)
    # (b) huge date headline
    draw_text(12, 50, "Sunday 22 November 2026", 3.4, RED, bold=True)
    # (c) sub-headline strip
    sub = ("COP31 closes in on a deal  \u00b7  Russia fires 400 drones and 110 missiles  \u00b7  "
           "Iran strikes US bases in Bahrain")
    draw_text(12, 90, sub, 1.1, INK)
    fill_rect(12, 107, 1000, 1, LGREY)
    # (d) number strip
    cw = 1000 / 6.0
    for i, (num, label) in enumerate(NUMBERS):
        cx = 12 + i * cw
        nw = text_w(num, 2.6)
        draw_text(cx + (cw - nw) / 2, 112, num, 2.6, DARKRED, bold=True)
        lab = wrap_text(label, 0.9, cw - 12)
        draw_block(cx + 6, 140, lab, 0.9, GREY, lh=11)
        if i:
            draw_line(cx, 112, cx, 152, LGREY, 1)
    # (e) region tabs bar
    fill_rect(12, 157, 1000, 20, NAVY)
    tabs = "  \u00b7  ".join("%s %d" % (name, n) for name, n in REGIONS)
    draw_text(12 + (1000 - text_w(tabs, 1.0)) / 2, 161, tabs, 1.0, WHITE, bold=True)
    # (f) heroes
    hw = 326
    for i, (num, place, tag, headline, summary, kind) in enumerate(HEROES):
        draw_hero(12 + i * (hw + 11), 181, hw, 158, num, place, tag, headline, summary, kind)
    # (g) grid 5 x 2
    gw = 196
    for i, (num, place, tag, headline, summary, kind) in enumerate(GRID):
        row, col = divmod(i, 5)
        gx = 12 + col * (gw + 5)
        gy = 343 + row * 120
        draw_grid_cell(gx, gy, gw, 116, num, place, tag, headline, summary, kind)
    # (h) map + ALSO ON index
    draw_text(12, 583, "WHERE IT HAPPENED", 1.0, INK, bold=True)
    draw_map(16, 598, 310, 137)
    draw_text(340, 583, "ALSO ON SUNDAY 22 NOVEMBER \u2014 22 MORE STORIES", 1.1, INK, bold=True)
    for j, (num, txt) in enumerate(BRIEFS):
        col, row = divmod(j, 11)
        bx = 340 + col * 335
        by = 600 + row * 12
        draw_text(bx, by, "%d." % num, 0.9, RED, bold=True)
        draw_text(bx + text_w("%d. " % num, 0.9), by, txt, 0.9, INK)
    # (i) BY THE CLOCK
    draw_text(12, 743, "BY THE CLOCK", 1.0, RED, bold=True)
    draw_text(12 + text_w("BY THE CLOCK  ", 1.0), 743, CLOCK_ITEMS, 0.95, INK)
    # (j) DATE CHECK box
    rect_outline(12, 763, 1000, 54, RED, 2)
    draw_text(20, 767, "DATE CHECK", 1.1, RED, bold=True)
    yy = 781
    for ln in DATE_CHECK_LINES:
        draw_text(20, yy, ln, 0.95, INK)
        yy += 12
    # (k) footers
    draw_text(12, 821, FOOTER_SRC, 0.85, GREY)
    draw_text(12, 834, "THE WORLD IN ONE DAY", 0.9, INK, bold=True)
    pf = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    draw_text(1012 - text_w(pf, 0.9), 834, pf, 0.9, GREY, bold=True)


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    write_png(out_path, W, H, buf)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
