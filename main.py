# The World Today - Thursday 26 November 2026.
# A one-page broadsheet rendered pixel by pixel with the Python
# standard library alone. Letters come from the compact bitmap
# table below (seven rows per glyph, five bits per row), pictures
# from filled boxes, discs and triangles, and the PNG bytes from
# a fixed zlib stream, so every run writes identical output.
import os
import struct
import zlib

SIDE = 1024

# Ink palette on warm paper.
CREAM = (248, 242, 224)
BLACK = (24, 24, 24)
CRIMSON = (172, 32, 32)
NAVY = (30, 76, 140)
PALE = (196, 220, 238)
VIOLET = (110, 64, 158)
GOLD = (244, 196, 0)
SNOW = (255, 255, 255)
ASH = (122, 120, 112)
SAND = (234, 227, 206)
LEAF = (48, 128, 54)
EMBER = (232, 122, 32)
DEEP = (20, 54, 98)
TEAL = (18, 128, 128)

# Glyph table: char -> seven row masks, bit 4 leftmost.
GLYPH = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "a": (0, 0, 14, 1, 15, 17, 15),
    "b": (16, 16, 30, 17, 17, 17, 30),
    "c": (0, 0, 14, 16, 16, 17, 14),
    "d": (1, 1, 15, 17, 17, 17, 15),
    "e": (0, 0, 14, 17, 31, 16, 14),
    "f": (6, 8, 8, 30, 8, 8, 8),
    "g": (0, 15, 17, 17, 15, 1, 14),
    "h": (16, 16, 30, 17, 17, 17, 17),
    "i": (4, 0, 12, 4, 4, 4, 14),
    "j": (2, 0, 6, 2, 2, 2, 12),
    "k": (16, 16, 18, 20, 24, 20, 18),
    "l": (12, 4, 4, 4, 4, 4, 14),
    "m": (0, 0, 26, 21, 21, 21, 21),
    "n": (0, 0, 30, 17, 17, 17, 17),
    "o": (0, 0, 14, 17, 17, 17, 14),
    "p": (0, 0, 30, 17, 17, 30, 16),
    "q": (0, 0, 15, 17, 17, 15, 1),
    "r": (0, 0, 22, 25, 16, 16, 16),
    "s": (0, 0, 15, 16, 14, 1, 30),
    "t": (8, 8, 30, 8, 8, 8, 6),
    "u": (0, 0, 17, 17, 17, 19, 13),
    "v": (0, 0, 17, 17, 17, 10, 4),
    "w": (0, 0, 17, 21, 21, 21, 10),
    "x": (0, 0, 17, 10, 4, 10, 17),
    "y": (0, 0, 17, 17, 15, 1, 14),
    "z": (0, 0, 31, 2, 4, 8, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '"': (10, 10, 10, 0, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "%": (24, 25, 2, 4, 8, 19, 3),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "*": (0, 4, 21, 14, 21, 4, 0),
    "#": (10, 10, 31, 10, 31, 10, 10),
    "[": (14, 8, 8, 8, 8, 8, 14),
    "]": (14, 2, 2, 2, 2, 2, 14),
    "_": (0, 0, 0, 0, 0, 0, 31),
    "<": (2, 4, 8, 16, 8, 4, 2),
    ">": (8, 4, 2, 1, 2, 4, 8),
}

buf = bytearray(SIDE * SIDE * 3)


def plot(px, py, col):
    if 0 <= px < SIDE and 0 <= py < SIDE:
        k = (py * SIDE + px) * 3
        buf[k] = col[0]
        buf[k + 1] = col[1]
        buf[k + 2] = col[2]


def fill_box(x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            plot(xx, yy, col)


def frame_box(x, y, w, h, col, thick=1):
    fill_box(x, y, w, thick, col)
    fill_box(x, y + h - thick, w, thick, col)
    fill_box(x, y, thick, h, col)
    fill_box(x + w - thick, y, thick, h, col)


def rule_h(x, y, length, col, thick=1):
    fill_box(x, y, length, thick, col)


def rule_v(x, y, length, col, thick=1):
    fill_box(x, y, thick, length, col)


def stroke(x0, y0, x1, y1, col):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    xx, yy = x0, y0
    while True:
        plot(xx, yy, col)
        if xx == x1 and yy == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            xx += sx
        if e2 <= dx:
            err += dx
            yy += sy


def disc(cx, cy, rad, col):
    for yy in range(-rad, rad + 1):
        span = int((rad * rad - yy * yy) ** 0.5)
        for xx in range(-span, span + 1):
            plot(cx + xx, cy + yy, col)


def wedge(x0, y0, x1, y1, x2, y2, col):
    top = min(y0, y1, y2)
    bot = max(y0, y1, y2)
    sides = ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0))
    for yy in range(top, bot + 1):
        hits = []
        for ax, ay, bx, by in sides:
            if (ay <= yy < by) or (by <= yy < ay):
                hits.append(ax + (yy - ay) * (bx - ax) / (by - ay))
        if len(hits) >= 2:
            lo = int(min(hits) + 0.999)
            hi = int(max(hits))
            for xx in range(lo, hi + 1):
                plot(xx, yy, col)


STEP = 6


def ink_width(text, scale):
    return len(text) * STEP * scale


def write_line(text, x, y, scale, col):
    cursor = x
    for ch in text:
        rows = GLYPH.get(ch, GLYPH[" "])
        for r in range(7):
            mask = rows[r]
            for c in range(5):
                if mask & (16 >> c):
                    fill_box(cursor + c * scale, y + r * scale, scale, scale, col)
        cursor += STEP * scale


def write_mid(text, centre, y, scale, col):
    write_line(text, centre - ink_width(text, scale) // 2, y, scale, col)


def flow_lines(text, max_w, scale):
    out = []
    current = ""
    for word in text.split(" "):
        trial = word if current == "" else current + " " + word
        if ink_width(trial, scale) <= max_w or current == "":
            current = trial
        else:
            out.append(current)
            current = word
    if current != "":
        out.append(current)
    return out


def write_block(text, x, y, max_w, scale, col, gap):
    for ln in flow_lines(text, max_w, scale):
        write_line(ln, x, y, scale, col)
        y += gap
    return y


def kicker(num, label, x, y):
    fill_box(x, y, 20, 20, CRIMSON)
    write_line(num, x + 7, y + 3, 2, SNOW)
    write_line(label, x + 28, y + 3, 2, CRIMSON)


# Page ground and double border.
fill_box(0, 0, SIDE, SIDE, CREAM)
frame_box(12, 12, 1000, 1000, BLACK, 2)
frame_box(18, 18, 988, 988, BLACK, 1)

# Masthead block.
write_mid("THE WORLD TODAY", 512, 34, 7, BLACK)
rule_h(30, 92, 964, BLACK, 2)
write_mid("THURSDAY 26 NOVEMBER 2026", 512, 100, 4, CRIMSON)
rule_h(30, 134, 964, BLACK, 1)
rule_h(30, 137, 964, BLACK, 2)
write_mid("FIVE STORIES FROM FIVE CORNERS OF THE WORLD", 512, 148, 2, BLACK)
rule_h(30, 168, 964, ASH, 1)

# Story one: Pyongyang nuclear call.
kicker("1", "SECURITY - NORTH KOREA", 48, 188)
write_line("KIM PUSHES TACTICAL", 48, 214, 4, BLACK)
write_line("NUCLEAR WEAPONS", 48, 248, 4, BLACK)
write_block(
    "North Korean leader Kim Jong Un, inspecting nuclear material and weapons research sites, said on Thursday that tactical nuclear weapons should be used across multiple domains and called the nuclear status absolutely inviolable, KCNA reported.",
    48, 288, 648, 2, BLACK, 18,
)
rule_h(48, 386, 648, ASH, 1)
write_line("SEOUL - KCNA VIA REUTERS", 48, 392, 2, BLACK)

# Missile panel beside the lead.
fill_box(720, 184, 256, 216, PALE)
frame_box(720, 184, 256, 216, BLACK, 1)
write_line("PYONGYANG", 732, 194, 2, NAVY)
disc(752, 222, 2, SNOW)
disc(946, 226, 2, SNOW)
disc(738, 352, 2, SNOW)
fill_box(800, 244, 44, 104, SNOW)
frame_box(800, 244, 44, 104, BLACK, 1)
wedge(800, 244, 844, 244, 822, 202, CRIMSON)
disc(822, 274, 8, BLACK)
disc(822, 274, 6, PALE)
fill_box(800, 318, 44, 12, CRIMSON)
wedge(800, 330, 780, 368, 800, 368, CRIMSON)
wedge(844, 330, 864, 368, 844, 368, CRIMSON)
wedge(807, 348, 837, 348, 822, 388, EMBER)
wedge(813, 348, 831, 348, 822, 378, GOLD)
rule_h(720, 392, 256, BLACK, 3)

rule_h(30, 424, 964, BLACK, 2)

# Story two: Taipei tariff answer.
kicker("2", "TRADE - TAIWAN AND THE US", 48, 440)
write_line("TAIWAN SAYS 15% US", 48, 468, 3, BLACK)
write_line("TARIFF WILL HOLD", 48, 494, 3, BLACK)
write_block(
    "Taiwan said on Thursday it is confident its 15% US tariff rate will stay, after Washington proposed 20% to 40% maximum rates for 14 partners.",
    48, 522, 436, 2, BLACK, 18,
)
fill_box(48, 612, 120, 34, NAVY)
fill_box(176, 612, 120, 34, CRIMSON)
fill_box(304, 612, 120, 34, TEAL)
frame_box(48, 612, 120, 34, BLACK, 1)
frame_box(176, 612, 120, 34, BLACK, 1)
frame_box(304, 612, 120, 34, BLACK, 1)
write_mid("15%", 108, 620, 3, SNOW)
write_mid("20-40%", 236, 620, 2, SNOW)
write_mid("14", 364, 620, 3, SNOW)
write_line("KEPT RATE   PROPOSED   PARTNERS", 48, 652, 2, BLACK)

# Story three: Seoul rate decision.
kicker("3", "MARKETS - SOUTH KOREA", 540, 440)
write_line("KOREA RATE CALL", 540, 468, 3, BLACK)
write_line("DUE TODAY", 540, 494, 3, BLACK)
write_block(
    "The Bank of Korea gives its last 2026 decision today. In a Reuters poll, 32 of 34 economists expect a rise to 3.25% from 3.00%.",
    540, 522, 436, 2, BLACK, 18,
)
write_mid("3.00%", 640, 598, 2, BLACK)
write_mid("3.25%", 856, 598, 2, CRIMSON)
fill_box(613, 643, 54, 30, NAVY)
fill_box(829, 618, 54, 55, CRIMSON)
stroke(667, 633, 829, 633, BLACK)
wedge(829, 628, 829, 638, 845, 633, BLACK)
rule_h(540, 673, 436, BLACK, 2)
write_line("NOW          EXPECTED", 588, 680, 2, BLACK)

rule_v(512, 436, 260, ASH, 1)
rule_h(30, 706, 964, BLACK, 2)

# Story four: airline records warning.
kicker("4", "AUSTRALIA - TRAVEL", 48, 722)
write_line("FLIGHT CENTRE WARNS", 48, 750, 3, BLACK)
write_line("RECORDS AT RISK", 48, 776, 3, BLACK)
write_block(
    "Flight Centre Travel said on Thursday it is investigating unusual activity in a booking system. An unauthorised party may have accessed many records.",
    48, 804, 436, 2, BLACK, 18,
)
fill_box(48, 918, 90, 26, DEEP)
wedge(138, 918, 206, 931, 138, 944, DEEP)
fill_box(70, 892, 14, 28, DEEP)
fill_box(70, 942, 14, 16, DEEP)
disc(300, 927, 22, GOLD)
frame_box(278, 905, 44, 44, BLACK, 2)
fill_box(292, 894, 16, 14, BLACK)
write_line("CHECK", 336, 920, 2, CRIMSON)

# Story five: Constitution Day in India.
kicker("5", "INDIA - SOCIETY", 540, 722)
write_line("INDIA MARKS", 540, 750, 3, BLACK)
write_line("CONSTITUTION DAY", 540, 776, 3, BLACK)
write_block(
    "India is to mark Constitution Day today in New Delhi, on the theme The Constitution at 76. A former chief justice is to read the Preamble.",
    540, 804, 436, 2, BLACK, 18,
)
fill_box(540, 912, 436, 14, EMBER)
fill_box(540, 926, 436, 14, SNOW)
fill_box(540, 940, 436, 14, LEAF)
frame_box(540, 912, 436, 42, BLACK, 1)
disc(758, 933, 6, NAVY)
write_mid("CONSTITUTION AT 76", 758, 892, 2, BLACK)

# Colophon with sources.
rule_h(30, 962, 964, BLACK, 1)
colophon_lines = (
    "Sources: Reuters via Northland News Radio and Daily Fox News,",
    "InvestingLive, PIB. Events of Thursday 26 November 2026.",
)
for row, text in enumerate(colophon_lines):
    write_mid(text, SIDE // 2, 970 + row * 18, 2, BLACK)


def chunk(kind, payload):
    head = struct.pack(">I", len(payload)) + kind
    tail = struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return head + payload + tail


def render_png():
    rows = bytearray()
    for yy in range(SIDE):
        rows.append(0)
        start = yy * SIDE * 3
        rows.extend(buf[start:start + SIDE * 3])
    header = struct.pack(">IIBBBBB", SIDE, SIDE, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


target = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(target, exist_ok=True)
with open(os.path.join(target, "entry.png"), "wb") as fh:
    fh.write(render_png())
