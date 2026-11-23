#!/usr/bin/env python3
"""Draw the front page of 'The World in One Day' for Monday 23 November 2026.

Pure standard library. No network, no external assets, no fonts on disk:
every glyph is a 5x7 bitmap defined below and rendered as filled rectangles.
Output is a deterministic 1024x1024 PNG written to <outdir>/entry.png.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 242, 231)   # newsprint cream
INK = (26, 26, 26)        # near-black ink
RED = (176, 42, 32)       # headline red
BLUE = (31, 78, 121)      # deep blue
SKY = (126, 180, 214)     # pale sky blue
SEA = (46, 110, 158)      # sea blue
GREEN = (74, 124, 64)     # land green
GOLD = (214, 164, 32)     # gold
ORANGE = (224, 110, 24)   # flame orange
FLAME = (232, 64, 24)     # flame red
GREY = (120, 116, 106)    # muted grey
LGREY = (226, 220, 208)   # light panel grey
WHITE = (255, 255, 255)
DARK = (16, 16, 16)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 strings of 5 bits, '#' = pixel on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
}

CHAR_W = 6  # 5 pixels + 1 spacing, at scale 1


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self._set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self._set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self._set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self._set(xx, yy, c)

    def polygon(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self._set(x, y, c)

    def triangle(self, a, b, c_, color):
        self.polygon([a, b, c_], color)

    # ------------------------------------------------------------ text ----
    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += CHAR_W * scale
        return x + w

    def wrap(self, text, max_w, scale):
        """Greedy word wrap; returns list of lines fitting max_w pixels."""
        words = text.upper().split()
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, text, max_w, scale, c, leading=None):
        if leading is None:
            leading = 7 * scale + 3
        yy = y
        for line in self.wrap(text, max_w, scale):
            self.text(x, yy, line, scale, c)
            yy += leading
        return yy


# -------------------------------------------------------------- PNG write ---
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ----------------------------------------------------------- illustrations --
def draw_globe_crack(cv, x, y, w, h):
    """Lead illustration: a cracked Earth, smoke rising, for COP31's failure."""
    cv.fill_rect(x, y, w, h, SKY)
    cx, cy, r = x + w // 2, y + h // 2 + 6, min(w, h) // 2 - 14
    cv.circle(cx, cy, r, BLUE)
    # land blobs
    cv.ellipse(cx - r // 2, cy - r // 3, r // 3, r // 4, GREEN)
    cv.ellipse(cx + r // 3, cy + r // 5, r // 4, r // 5, GREEN)
    cv.ellipse(cx + r // 10, cy - r // 2, r // 5, r // 6, GREEN)
    cv.ellipse(cx - r // 3, cy + r // 2, r // 4, r // 6, GREEN)
    # latitude lines
    for dy, rr in ((-r // 2, None), (0, None), (r // 2, None)):
        import math
        rr = int((r * r - dy * dy) ** 0.5)
        cv.fill_rect(cx - rr, cy + dy, 2 * rr, 2, (200, 220, 235))
    # the crack: jagged red lightning across the globe
    pts = [(cx - r // 3, cy - r + 6), (cx - r // 6, cy - r // 2),
           (cx - r // 2, cy - r // 6), (cx, cy + r // 6),
           (cx - r // 4, cy + r // 2), (cx + r // 6, cy + r - 8)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 5)
    # smoke puffs
    cv.circle(x + w - 34, y + 22, 10, GREY)
    cv.circle(x + w - 48, y + 12, 7, GREY)
    # caption tag
    cv.fill_rect(x, y + h - 24, 118, 24, RED)
    cv.text(x + 8, y + h - 19, "ANTALYA", 2, WHITE)


def draw_ship_fire(cv, x, y, w, h):
    """Burning cargo ship at sea (Sparta II) + drone above."""
    cv.fill_rect(x, y, w, h, SKY)
    # sun
    cv.circle(x + w - 30, y + 26, 14, GOLD)
    # sea
    cv.fill_rect(x, y + h - 46, w, 46, SEA)
    for i in range(4):
        cv.fill_rect(x + 8 + i * 34, y + h - 34 + (i % 2) * 12, 26, 3, WHITE)
    # ship hull
    hx, hy = x + 16, y + h - 78
    cv.polygon([(hx, hy), (hx + w - 40, hy), (hx + w - 56, hy + 30),
                (hx + 12, hy + 30)], INK)
    cv.fill_rect(hx + 8, hy - 22, 44, 22, RED)          # bridge block
    cv.fill_rect(hx + 8, hy - 22, 44, 4, WHITE)
    for i in range(4):                                     # containers
        cv.fill_rect(hx + 58 + i * 26, hy - 20, 22, 20, GOLD if i % 2 else BLUE)
    # flames above the hull
    for fx, fh in ((hx + 70, 34), (hx + 96, 46), (hx + 122, 30)):
        cv.triangle((fx, hy - fh), (fx - 12, hy), (fx + 12, hy), FLAME)
        cv.triangle((fx, hy - fh + 12), (fx - 6, hy), (fx + 6, hy), ORANGE)
    # smoke
    cv.circle(hx + 100, hy - 52, 10, GREY)
    cv.circle(hx + 116, hy - 64, 7, GREY)
    # small drone
    dx, dy = x + w // 2 + 8, y + 22
    cv.fill_rect(dx - 10, dy - 2, 20, 4, INK)
    cv.circle(dx - 12, dy, 4, INK)
    cv.circle(dx + 12, dy, 4, INK)
    cv.fill_rect(dx - 3, dy + 2, 6, 5, INK)


def draw_tanker_gulf(cv, x, y, w, h):
    """Tanker in the Strait of Hormuz with missile streaks overhead."""
    cv.fill_rect(x, y, w, h, (232, 214, 176))  # hazy desert sky
    cv.circle(x + 30, y + 26, 14, GOLD)
    cv.fill_rect(x, y + h - 44, w, 44, SEA)
    for i in range(4):
        cv.fill_rect(x + 10 + i * 36, y + h - 30 + (i % 2) * 10, 26, 3, WHITE)
    # tanker
    hx, hy = x + 14, y + h - 72
    cv.fill_rect(hx, hy, w - 30, 26, RED)
    cv.fill_rect(hx, hy, w - 30, 5, WHITE)
    cv.fill_rect(hx + 8, hy - 18, 20, 18, INK)   # bridge
    cv.fill_rect(hx + w - 46, hy - 14, 12, 14, INK)  # funnel
    # missile streaks
    for my in (y + 16, y + 34, y + 52):
        cv.line(x + 20, my, x + 84, my + 8, INK, 2)
        cv.triangle((x + 84, my + 8), (x + 72, my + 2), (x + 72, my + 14), FLAME)


def draw_factory_fire(cv, x, y, w, h):
    """Factory with sawtooth roof, flames and smoke (Java candy factory)."""
    cv.fill_rect(x, y, w, h, (44, 44, 48))  # night sky
    cv.circle(x + w - 28, y + 24, 10, (220, 220, 200))
    # factory block
    fx, fy = x + 14, y + h - 66
    cv.fill_rect(fx, fy, w - 28, 44, (96, 88, 80))
    for i in range(3):  # sawtooth roof
        cv.triangle((fx + i * 46, fy), (fx + i * 46 + 23, fy - 18),
                    (fx + i * 46 + 46, fy), (120, 110, 100))
    for i in range(4):  # lit windows
        cv.fill_rect(fx + 10 + i * 32, fy + 12, 18, 16, GOLD)
    # flames from the roof
    for px, ph in ((fx + 30, 40), (fx + 66, 52), (fx + 100, 36)):
        cv.triangle((px, fy - ph), (px - 13, fy), (px + 13, fy), FLAME)
        cv.triangle((px, fy - ph + 14), (px - 6, fy), (px + 6, fy), ORANGE)
    # smoke
    cv.circle(fx + 66, fy - 66, 11, GREY)
    cv.circle(fx + 84, fy - 80, 8, GREY)
    cv.fill_rect(x, y + h - 22, w, 22, INK)
    cv.text(x + 8, y + h - 17, "SERANG", 2, WHITE)


def draw_exam_ai(cv, x, y, w, h):
    """Exam desk with paper and a big AI chip — South Korea minister resigns."""
    cv.fill_rect(x, y, w, h, LGREY)
    # desk
    cv.fill_rect(x + 12, y + h - 52, w - 24, 12, (150, 110, 70))
    cv.fill_rect(x + 18, y + h - 40, 8, 40, (120, 88, 56))
    cv.fill_rect(x + w - 26, y + h - 40, 8, 40, (120, 88, 56))
    # exam paper
    cv.fill_rect(x + 26, y + 18, 62, 76, WHITE)
    cv.rect(x + 26, y + 18, 62, 76, INK, 2)
    for i in range(5):
        cv.fill_rect(x + 34, y + 28 + i * 12, 46, 3, INK)
    cv.fill_rect(x + 34, y + 28, 20, 3, RED)
    # big AI chip
    cx, cy = x + w - 58, y + 52
    cv.fill_rect(cx - 26, cy - 26, 52, 52, BLUE)
    cv.rect(cx - 26, cy - 26, 52, 52, INK, 2)
    for dx in (-32, 32):
        cv.fill_rect(cx + dx - 2, cy - 14, 6, 28, GOLD)
    for dy in (-32, 32):
        cv.fill_rect(cx - 14, cy + dy - 2, 28, 6, GOLD)
    cv.text(cx - 13, cy - 11, "AI", 3, WHITE)
    # red X over the paper (cheating caught)
    cv.line(x + 26, y + 18, x + 88, y + 94, RED, 4)
    cv.line(x + 88, y + 18, x + 26, y + 94, RED, 4)


def draw_flags(cv, x, y, w, h):
    """Nepal + India flags side by side for the Delhi talks story."""
    cv.fill_rect(x, y, w, h, LGREY)
    # Nepal flag: two stacked crimson pennons with blue border
    nx, ny = x + 12, y + 10
    cv.polygon([(nx, ny), (nx + 52, ny + 22), (nx, ny + 22)], RED)
    cv.polygon([(nx, ny + 24), (nx + 44, ny + 42), (nx, ny + 42)], RED)
    cv.line(nx, ny, nx, ny + 42, BLUE, 2)
    cv.circle(nx + 14, ny + 30, 3, WHITE)
    # India flag: saffron / white / green with chakra
    ix, iy = x + 84, y + 12
    cv.fill_rect(ix, iy, 66, 14, (255, 153, 51))
    cv.fill_rect(ix, iy + 14, 66, 14, WHITE)
    cv.fill_rect(ix, iy + 28, 66, 14, (19, 136, 8))
    cv.circle(ix + 33, iy + 21, 7, BLUE)
    cv.circle(ix + 33, iy + 21, 2, BLUE)
    # divider between the two flags
    cv.fill_rect(x + 76, y + 12, 2, 42, GREY)


# ---------------------------------------------------------------- layout ---
def story_cell(cv, x, y, w, h, kicker, headline, body, draw_fn):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)
    iw = 150
    cv.rect(x + 8, y + 8, iw, h - 16, INK, 2)
    draw_fn(cv, x + 9, y + 9, iw - 2, h - 18)
    tx = x + iw + 20
    tw = x + w - 12 - tx
    cv.text(tx, y + 12, kicker, 2, RED)
    yy = y + 12 + 18
    for line in cv.wrap(headline, tw, 3):
        cv.text(tx, yy, line, 3, INK)
        yy += 24
    yy += 2
    cv.paragraph(tx, yy, body, tw, 2, INK)


def build():
    cv = Canvas(W, H, PAPER)
    M = 24
    CW = W - 2 * M  # 976

    # ------------------------------------------------------------- masthead --
    cv.fill_rect(M, 26, CW, 3, INK)
    title = "THE WORLD IN ONE DAY"
    cv.text(W // 2, 40, title, 6, INK, align="center")
    cv.text(W // 2, 92, "MONDAY 23 NOVEMBER 2026", 3, RED, align="center")
    cv.text(W // 2, 118, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, INK,
            align="center")
    cv.fill_rect(M, 140, CW, 4, INK)
    cv.fill_rect(M, 148, CW, 2, INK)

    # ---------------------------------------------------------- lead story --
    ly, lh = 160, 262
    cv.fill_rect(M, ly, CW, lh, WHITE)
    cv.rect(M, ly, CW, lh, INK, 3)
    ix, iy, iw, ih = M + 10, ly + 10, 320, lh - 20
    cv.rect(ix, iy, iw, ih, INK, 2)
    draw_globe_crack(cv, ix + 1, iy + 1, iw - 2, ih - 2)
    tx = M + iw + 30
    tw = M + CW - 14 - tx
    cv.text(tx, ly + 14, "CLIMATE  |  ANTALYA, TURKIYE", 2, RED)
    cv.text(tx, ly + 40, "COP31", 7, INK)
    cv.text(tx, ly + 40 + 53, "COLLAPSES", 7, RED)
    by = ly + 40 + 53 + 53 + 8
    by = cv.paragraph(
        tx, by,
        "Nearly 200 nations fail to agree a climate deal as fossil fuels are "
        "cut from the text. The longest COP ever ends in failure.",
        tw, 2, INK)
    cv.text(tx, ly + lh - 26, "NO DEAL, NO PLAN FOR 1.5C", 2, BLUE)

    # ------------------------------------------------------------ grid 2x2 --
    gy, gh, gap = 434, 200, 12
    colw = (CW - gap) // 2
    cells = [
        ("UKRAINE WAR", "KYIV FLATS HIT",
         "Russian drone strike leaves 14 missing in the Kyiv region. "
         "Russian ships burn in the Baltic and off Libya.",
         draw_ship_fire),
        ("MIDDLE EAST", "GULF WAR WIDENS",
         "Iran hits Bahrain and tankers in the Strait of Hormuz as oil "
         "flows fall. Two wounded in Bahrain.",
         draw_tanker_gulf),
        ("ASIA", "FACTORY FIRE HORROR",
         "Seven body bags found and about 50 workers missing after a "
         "blaze at a Java candy factory.",
         draw_factory_fire),
        ("ASIA", "MINISTER QUITS OVER AI CHEATS",
         "South Korea's education chief resigns after AI-assisted "
         "cheating chaos in college exams.",
         draw_exam_ai),
    ]
    for i, (kick, head, body, fn) in enumerate(cells):
        cx = M + (i % 2) * (colw + gap)
        cy = gy + (i // 2) * (gh + gap)
        story_cell(cv, cx, cy, colw, gh, kick, head, body, fn)

    # ------------------------------------------------------- bottom story ---
    by, bh = 858, 84
    cv.fill_rect(M, by, CW, bh, WHITE)
    cv.rect(M, by, CW, bh, INK, 2)
    draw_flags(cv, M + 8, by + 7, 190, bh - 14)
    tx = M + 214
    cv.text(tx, by + 12, "SOUTH ASIA", 2, RED)
    cv.text(tx, by + 32, "NEPAL PM IN DELHI", 3, INK)
    cv.text(tx, by + 60, "BALENDRA SHAH HOLDS TALKS WITH MODI IN DELHI.", 2, INK)

    # --------------------------------------------------------------- ticker --
    ty, th = 954, 40
    cv.fill_rect(M, ty, CW, th, DARK)
    cv.text(M + 12, ty + 12,
            "SPORT: INDIA 720/9 - RECORD TEST TOTAL  |  "
            "MARKETS: ANTHROPIC'S RECORD DEBUT",
            2, WHITE)
    cv.text(W // 2, 1004, "SOURCES: REUTERS, BBC, CNN, AP, AL JAZEERA, LE MONDE",
            1, GREY, align="center")
    return cv


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "/output"
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
