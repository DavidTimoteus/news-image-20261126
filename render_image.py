#!/usr/bin/env python3
"""news-image-20261126 v1 — broadsheet front page, 100% code-drawn (Pillow).

Fresh renderer written for this bounty day. Style: editorial broadsheet
(cream paper, ink, one muted red) following the v4 broadsheet language.
Deterministic: no timestamps, no randomness, fixed font paths.
1024x1024, RGB, saved as entry.png next to this script.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28                      # margin
CW = W - 2 * M              # 968 content width
PAPER = (245, 240, 225)     # #F5F0E1
INK = (26, 26, 26)          # #1A1A1A
RED = (166, 25, 46)         # #A6192E
MUTED = (95, 89, 77)        # small-caps grey, ~5.9:1 on paper
FAINT = (120, 114, 100)
LAND = (227, 217, 190)      # map land beige
SEA = (214, 227, 231)       # map sea pale blue
BLUE = (47, 93, 107)        # muted blue accent (charts / sea lines)
GOLD = (146, 106, 0)        # dark amber, AA-safe

FD = "/usr/share/fonts/truetype"
SERIF_BLACK = f"{FD}/noto/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FD}/noto/NotoSerif-Bold.ttf"
SERIF = f"{FD}/noto/NotoSerif-Regular.ttf"
SERIF_IT = f"{FD}/noto/NotoSerif-Italic.ttf"
SANS = f"{FD}/dejavu/DejaVuSans.ttf"
SANS_B = f"{FD}/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy wrap; returns list of lines, each <= max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit(draw, text, fnt, max_w, max_lines, what):
    lines = wrap(draw, text, fnt, max_w)
    assert len(lines) <= max_lines, f"{what}: {len(lines)} lines > {max_lines}: {lines}"
    return lines


def rule(draw, x, y, w, fill=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


def small_caps(draw, text, x, y, size=8, fill=MUTED, fnt=None):
    f = fnt or font(SANS_B, size)
    draw.text((x, y), text.upper(), font=f, fill=fill)
    return draw.textlength(text.upper(), font=f)


# ---------------------------------------------------------------- data
HEROES = [
    dict(num=1, kick="MIDDLE EAST  ·  ONGOING",
         head="Gulf war widens: blast rocks Sanaa, missiles over Riyadh",
         body="Saudi-led coalition intercepts missiles over Riyadh as Houthi forces target Red Sea ports. Brent holds at $94.71.",
         src="AL JAZEERA  ·  REUTERS", art="gulf"),
    dict(num=2, kick="EAST ASIA  ·  CONFIRMED",
         head="Kim orders wider spread of tactical nuclear weapons",
         body="KCNA reports Thursday: Kim inspected nuclear plants and called the North's nuclear status \u201cabsolutely unassailable\u201d.",
         src="REUTERS  ·  KCNA", art="korea"),
    dict(num=3, kick="GLOBAL MARKETS  ·  CONFIRMED",
         head="Asia rebounds as tech rallies and gold climbs back",
         body="Nikkei +1.6%, Korea +1.9%, Taiwan +1.96%, Hang Seng Tech +4%. Gold back above $3,600; bitcoin above $61,000.",
         src="REUTERS  ·  KUCOIN", art="chart"),
]

CARDS = [
    dict(num=4, kick="LONDON  ·  EUROPE  ·  CONFIRMED",
         head="UK to publish two EU treaties on Thursday",
         body="Texts agreed 20 Nov go public today, with a bill to enact the deal.",
         src="BBC  ·  AFP", art="doc", banner="10-YEAR EXIT CLAUSE"),
    dict(num=5, kick="HANOI  ·  SE ASIA  ·  CONFIRMED",
         head="Trade bloc meets in Vietnam as tariffs bite",
         body="CPTPP ministers open two days of talks with ASEAN and the EU trade chief.",
         src="REUTERS", art="ship", banner="12 NATIONS  ·  2 DAYS"),
    dict(num=6, kick="MADRID  ·  EUROPE  ·  REPORTED",
         head="Spain's boom is not reaching voters' wallets",
         body="Growth leads advanced economies, but prices bite before Sunday's election.",
         src="REUTERS", art="ballot", banner="INFLATION 4.9%"),
    dict(num=7, kick="TOKYO  ·  E ASIA  ·  OFFICIAL",
         head="Chinese firms now the top threat to Japanese rivals",
         body="JETRO survey of 7,695 firms: Chinese rivals lead on cost and decision speed.",
         src="REUTERS  ·  JETRO", art="factory", banner="38% SEE MORE RIVALS"),
    dict(num=8, kick="BOGOR  ·  SE ASIA  ·  CONFIRMED",
         head="Rescuers resume search at flooded illegal gold mine",
         body="26 miners were caught 100 m down when rain flooded the pit on Monday.",
         src="REUTERS", art="mine", banner="13 DEAD  ·  13 TRAPPED"),
    dict(num=9, kick="SAN FRANCISCO  ·  N AMERICA  ·  ONGOING",
         head="King tides peak as Thanksgiving travel surges",
         body="Flood warnings run to Thursday afternoon; SFO and Oakland brace with pumps.",
         src="BBC  ·  USA TODAY", art="wave", banner="8.23 FT RECORD TIDE"),
    dict(num=10, kick="MIAMI  ·  N AMERICA  ·  CONFIRMED",
         head="FedEx jet runs off the runway at Miami",
         body="FDX910 from Memphis slid past the runway; an FAA ground stop followed.",
         src="NY POST", art="plane", banner="01:40 UTC  ·  NO INJURIES"),
    dict(num=11, kick="INGLEWOOD  ·  N AMERICA  ·  CONFIRMED",
         head="Rams dump Packers 26\u201313 on Thanksgiving Eve",
         body="Corum ran for a career-high 184 yards and a TD; Rams won a fifth straight.",
         src="REUTERS", art="ball", banner="CORUM 184 YDS"),
    dict(num=12, kick="SYDNEY  ·  OCEANIA  ·  OFFICIAL",
         head="Nine arrested in dawn raids on \u2018crime as a service\u2019",
         body="Taskforce Falcon hit six suburbs from 06:00 over shootings and drug supply.",
         src="NSW POLICE", art="badge", banner="10 SEARCH WARRANTS"),
    dict(num=13, kick="SYDNEY  ·  OCEANIA  ·  CONFIRMED",
         head="Virgin ground staff walk out at four airports",
         body="ASU check-in and gate staff stop work in peak hours in a pay dispute.",
         src="TRAVEL WEEKLY  ·  ASU", art="tail", banner="4 AIRPORTS  ·  PEAK HOURS"),
]

ALSO = [
    (14, "Oil up on Hormuz mine claims \u2014 Brent $94.71, WTI $84.03", "REUTERS"),
    (15, "Gold rebounds above $3,600; bitcoin tops $61,000", "KUCOIN"),
    (16, "China tech rallies: Hang Seng Tech +4%, Zhipu +15%", "BLOCKBEATS"),
    (17, "Sensex 84,190; Nifty 25,873 as India trades flat-positive", "THE HINDU"),
    (18, "US officials split over China spying claims after Huang's return", "REUTERS"),
    (19, "Uber names Rakesh Ranjan to lead India and South Asia", "REUTERS"),
    (20, "BBC teams up with the Met Office on weather coverage", "BBC"),
    (21, "South Park finale leans on GTA 6 as season 29 ends", "VARIETY"),
    (22, "Vancouver coastal flood warning runs to Thursday 18:00", "WEATHER.COM"),
    (23, "Thanksgiving storm batters both US coasts; 81.5m travelling", "BBC"),
    (24, "Rugby: England's All Blacks test billed as World Cup rehearsal", "SKY SPORTS"),
    (25, "Two quakes, M5.2 and M5.0, off New Zealand's North Island", "USGS"),
    (26, "Thanksgiving Day: three NFL games, Bears\u2013Lions first at 13:00 ET", "USA TODAY"),
    (27, "CPTPP\u2013EU dialogue opens in Hanoi on fair, open trade", "STOCKBIZ"),
    (28, "Houthis claim strikes on two Saudi Red Sea ports", "AL MONITOR"),
    (29, "Dollar steady as yields slide; ECB accounts due Thursday", "REUTERS"),
    (30, "Roo-ver moon electronics pass radiation tests in Canberra", "ELECTRONICS ONLINE"),
    (31, "Thanksgiving: US markets shut; futures point higher", "REUTERS"),
]

NUMBERS = [
    ("$94.71", "Brent crude, Asian trade\n(+0.1%; +3.5% Wed)"),
    ("+1.6%", "Nikkei 225 rebounds\n(Korea +1.9%, Taiwan +1.96%)"),
    ("13 + 13", "dead and trapped\nin the Bogor mine"),
    ("100,000", "youth places a year\nunder the UK\u2013EU deal"),
    ("81.5m", "Americans travelling\nfor Thanksgiving (AAA)"),
]

TIMELINE = [
    ("00:00", "Al Jazeera live: blast rocks Sanaa; missiles intercepted over Riyadh"),
    ("01:37", "Reuters: Brent $94.71, WTI $84.03 in Asian trade"),
    ("01:40", "FedEx MD-11 runs off the runway at Miami (20:40 Wed local)"),
    ("02:02", "M5.2 quake off Hicks Bay, NZ; M5.0 follows at 02:25"),
    ("04:16", "NSW Police announce Falcon raids (15:16 AEDT)"),
]

# featured pin locations (lon, lat) + manual nudge (dx, dy) px
PINS = [
    (1, 44.20, 15.35, 0, 0),      # Sanaa
    (2, 125.75, 39.03, 0, 0),     # Pyongyang
    (3, 139.69, 35.68, 0, -6),    # Tokyo (markets)
    (4, -0.12, 51.50, 0, -8),     # London (nudged up)
    (5, 105.85, 21.03, 0, 0),     # Hanoi
    (6, -3.70, 40.42, -10, 8),    # Madrid (nudged down-left)
    (7, 135.50, 34.70, 0, 6),     # Japan (JETRO, Osaka-side nudge)
    (8, 106.80, -6.60, 0, 0),     # Bogor
    (9, -122.40, 37.80, 0, -5),   # San Francisco
    (10, -80.20, 25.80, 0, 0),    # Miami
    (11, -118.35, 33.96, 0, 11),  # Inglewood, nudged south
    (12, 151.20, -33.87, 0, 0),   # Sydney
    (13, 144.96, -37.81, -6, 6),  # Melbourne (Virgin, 4 airports)
]

# simplified continents (lon, lat) polygons, schematic
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-105, 72), (-90, 74), (-82, 73), (-76, 62),
     (-65, 60), (-60, 52), (-65, 45), (-70, 42), (-75, 35), (-81, 31), (-84, 30),
     (-90, 29), (-97, 26), (-97, 22), (-105, 20), (-95, 16), (-86, 13), (-83, 9),
     (-90, 14), (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-124, 40),
     (-125, 49), (-135, 58), (-150, 60), (-165, 60), (-168, 66)],
    [(-80, 9), (-77, 7), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-70, -52),
     (-73, -44), (-73, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 0), (-80, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70), (40, 68),
     (45, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 72), (80, 73),
     (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 70), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 59),
     (142, 55), (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
     (122, 28), (115, 22), (110, 20), (108, 12), (105, 9), (100, 7), (98, 12),
     (95, 16), (92, 21), (89, 22), (86, 20), (80, 13), (77, 8), (75, 15),
     (72, 20), (68, 23), (62, 25), (57, 26), (52, 28), (50, 30), (48, 30),
     (44, 29), (40, 32), (36, 36), (30, 36), (26, 38), (23, 36), (20, 40),
     (18, 42), (14, 45), (10, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37), (-10, 36)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 21),
     (43, 12), (48, 11), (51, 12), (44, 2), (41, -2), (40, -10), (40, -18),
     (36, -26), (32, -29), (28, -33), (20, -35), (18, -32), (15, -27),
     (12, -18), (13, -12), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
]


# ---------------------------------------------------------------- art
def art_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=1)
    # Arabian peninsula + Iran landmass (schematic, relative coords)
    land = [(0.42, 0.18), (0.62, 0.10), (0.80, 0.14), (0.98, 0.30), (0.96, 0.55),
            (0.88, 0.78), (0.78, 0.95), (0.62, 0.98), (0.50, 0.80), (0.44, 0.55),
            (0.38, 0.35), (0.42, 0.18)]
    d.polygon([(x + px * w, y + py * h) for px, py in land], fill=LAND, outline=INK)
    land2 = [(0.02, 0.05), (0.40, 0.05), (0.42, 0.18), (0.38, 0.30), (0.10, 0.28),
             (0.02, 0.18)]
    d.polygon([(x + px * w, y + py * h) for px, py in land2], fill=LAND, outline=INK)
    # Red Sea + Gulf strokes
    d.line([(x + 0.44 * w, y + 0.55 * h), (x + 0.52 * w, y + 0.92 * h)], fill=BLUE, width=2)
    # missile arc (dashed): Sanaa -> Riyadh, quadratic bezier
    sx, sy = x + 0.58 * w, y + 0.88 * h
    rx, ry = x + 0.72 * w, y + 0.42 * h
    mx, my = (sx + rx) / 2 - 26, (sy + ry) / 2 - 10
    prev = None
    for j in range(25):
        t = j / 24
        px = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t ** 2 * rx
        py = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t ** 2 * ry
        if prev is not None and j % 2 == 0:
            d.line([prev, (px, py)], fill=RED, width=2)
        prev = (px, py)
    # pins
    for (px, py, lab, lx, ly) in [
            (0.58, 0.88, "SANAA", 8, -3), (0.72, 0.42, "RIYADH", 6, -4),
            (0.84, 0.30, "HORMUZ", 6, -3), (0.80, 0.20, "RAS TANURA", -38, -13)]:
        cx, cy = x + px * w, y + py * h
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED, outline=PAPER, width=1)
        d.text((cx + lx, cy + ly), lab, font=font(SANS_B, 7), fill=INK)
    d.text((x + 6, y + 4), "RED SEA", font=font(SANS_B, 7), fill=BLUE)
    d.text((x + w - 52, y + 4), "GULF", font=font(SANS_B, 7), fill=BLUE)
    # callout (bottom-left, clear of the Sanaa label)
    bx, by = x + 6, y + h - 26
    d.rectangle([bx, by, bx + 112, by + 20], fill=PAPER, outline=INK, width=1)
    d.text((bx + 6, by + 4), "BRENT $94.71", font=font(SANS_B, 9), fill=RED)


def art_korea(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=1)
    # peninsula
    land = [(0.30, 0.02), (0.62, 0.02), (0.66, 0.20), (0.60, 0.45), (0.52, 0.70),
            (0.44, 0.92), (0.36, 0.98), (0.30, 0.75), (0.24, 0.50), (0.22, 0.25),
            (0.30, 0.02)]
    d.polygon([(x + px * w, y + py * h) for px, py in land], fill=LAND, outline=INK)
    # DMZ line
    d.line([(x + 0.24 * w, y + 0.42 * h), (x + 0.60 * w, y + 0.38 * h)],
           fill=RED, width=1)
    # centrifuge rings around Pyongyang
    cx, cy = x + 0.44 * w, y + 0.22 * h
    for r in (7, 12, 17):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED, outline=PAPER, width=1)
    d.text((cx + 8, cy - 12), "PYONGYANG", font=font(SANS_B, 7), fill=INK)
    sx, sy = x + 0.42 * w, y + 0.55 * h
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=INK)
    d.text((sx + 6, sy - 3), "SEOUL", font=font(SANS_B, 7), fill=INK)
    d.text((x + 6, y + 4), "YELLOW SEA", font=font(SANS_B, 7), fill=BLUE)
    d.text((x + w - 62, y + 4), "SEA OF JAPAN", font=font(SANS_B, 7), fill=BLUE)
    bx, by = x + w - 118, y + h - 26
    d.rectangle([bx, by, bx + 112, by + 20], fill=PAPER, outline=INK, width=1)
    d.text((bx + 6, by + 4), "HWASAN-31", font=font(SANS_B, 9), fill=RED)


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    bars = [("NIKKEI", 1.6), ("KOSPI", 1.9), ("TAIWAN", 1.96), ("HS TECH", 4.0)]
    base = y + h - 22
    bw = 52
    gap = (w - 4 * bw - 24) / 5
    for i, (lab, v) in enumerate(bars):
        bx = x + 12 + gap + i * (bw + gap)
        bh = (h - 44) * v / 4.0
        d.rectangle([bx, base - bh, bx + bw, base], fill=RED if i == 3 else INK)
        d.text((bx, base - bh - 12), f"+{v}%", font=font(SANS_B, 8), fill=INK)
        d.text((bx, base + 4), lab, font=font(SANS_B, 7), fill=MUTED)
    d.line([(x + 8, base), (x + w - 8, base)], fill=INK, width=1)
    d.text((x + 8, y + 4), "ASIA REBOUNDS, % CHANGE THU", font=font(SANS_B, 7), fill=MUTED)
    bx, by = x + w - 148, y + 4
    d.text((bx, by), "GOLD $3,600+  ·  BTC $61K", font=font(SANS_B, 8), fill=RED)


def art_panel(d, x, y, w, h, kind, banner):
    d.rectangle([x, y, x + w, y + h], fill=SEA if kind in ("wave", "ship") else PAPER,
                outline=INK, width=1)
    cx, cy = x + w / 2, y + h / 2
    if kind == "doc":
        d.rectangle([x + 58, y + 6, x + w - 58, y + h - 22], fill=PAPER, outline=INK, width=2)
        for i in range(4):
            d.line([(x + 66, y + 16 + i * 7), (x + w - 66, y + 16 + i * 7)], fill=INK, width=1)
        d.ellipse([x + w - 78, y + 10, x + w - 66, y + 22], outline=GOLD, width=2)
    elif kind == "ship":
        d.polygon([(x + 20, y + 34), (x + w - 20, y + 34), (x + w - 34, y + 52),
                   (x + 34, y + 52)], fill=INK)
        for i in range(3):
            d.rectangle([x + 34 + i * 30, y + 18, x + 56 + i * 30, y + 34],
                        fill=RED if i == 1 else BLUE, outline=INK, width=1)
        for i in range(3):
            d.arc([x + 14 + i * 52, y + 52, x + 50 + i * 52, y + 62], 0, 180, fill=BLUE, width=2)
    elif kind == "ballot":
        d.rectangle([x + 52, y + 22, x + w - 52, y + h - 18], fill=PAPER, outline=INK, width=2)
        d.line([(x + 66, y + 34), (x + 74, y + 42), (x + 92, y + 22)], fill=RED, width=3)
        d.rectangle([x + 40, y + h - 22, x + w - 40, y + h - 14], fill=INK)
    elif kind == "factory":
        d.polygon([(x + 22, y + 52), (x + 22, y + 28), (x + 52, y + 28), (x + 52, y + 18),
                   (x + 82, y + 18), (x + 82, y + 52)], fill=LAND, outline=INK, width=2)
        d.rectangle([x + 30, y + 36, x + 40, y + 46], fill=INK)
        d.rectangle([x + 46, y + 36, x + 56, y + 46], fill=INK)
        d.rectangle([x + 96, y + 12, x + 104, y + 52], fill=INK)
        d.line([(x + 116, y + 40), (x + 134, y + 28), (x + 152, y + 20)], fill=RED, width=3)
        d.polygon([(x + 152, y + 20), (x + 144, y + 20), (x + 152, y + 28)], fill=RED)
    elif kind == "mine":
        d.rectangle([x + 20, y + 14, x + w - 20, y + 22], fill=LAND, outline=INK, width=1)
        d.polygon([(x + 70, y + 22), (x + 114, y + 22), (x + 104, y + 52), (x + 80, y + 52)],
                  fill=INK)
        d.line([(x + 92, y + 22), (x + 92, y + 52)], fill=RED, width=2)
        for i in range(3):
            d.line([(x + 30 + i * 10, y + 44), (x + 44 + i * 10, y + 52)], fill=BLUE, width=2)
        d.text((x + 118, y + 30), "100 m", font=font(SANS_B, 8), fill=INK)
    elif kind == "wave":
        for i, yy in enumerate((26, 38, 50)):
            d.arc([x + 14, y + yy - 12, x + w - 14, y + yy + 12], 180, 360,
                  fill=BLUE, width=3)
        d.polygon([(x + 20, y + 52), (x + 40, y + 30), (x + 60, y + 52)], fill=INK)
        d.rectangle([x + 20, y + 52, x + 60, y + 56], fill=INK)
    elif kind == "plane":
        d.polygon([(x + 18, y + 34), (x + 120, y + 30), (x + 168, y + 38), (x + 120, y + 46),
                   (x + 18, y + 42)], fill=INK)
        d.polygon([(x + 130, y + 30), (x + 150, y + 14), (x + 158, y + 30)], fill=RED)
        d.line([(x + 60, y + 42), (x + 52, y + 56)], fill=INK, width=3)
        d.line([(x + 100, y + 44), (x + 94, y + 58)], fill=INK, width=3)
        d.line([(x + 14, y + 58), (x + w - 14, y + 58)], fill=INK, width=2)
    elif kind == "ball":
        d.ellipse([cx - 26, cy - 8, cx + 26, cy + 8], fill=(139, 69, 19), outline=INK, width=2)
        d.line([(cx - 26, cy - 8), (cx + 26, cy + 8)], fill=PAPER, width=1)
        d.line([(cx - 26, cy + 8), (cx + 26, cy - 8)], fill=PAPER, width=1)
        d.line([(cx - 8, cy - 2), (cx + 8, cy - 2)], fill=PAPER, width=2)
    elif kind == "badge":
        d.polygon([(cx, y + 8), (cx + 26, y + 18), (cx + 22, y + 46), (cx, y + 58),
                   (cx - 22, y + 46), (cx - 26, y + 18)], fill=GOLD, outline=INK, width=2)
        d.ellipse([cx - 8, cy - 6, cx + 8, cy + 10], fill=PAPER, outline=INK, width=1)
        d.text((cx - 3, cy - 4), "9", font=font(SANS_B, 10), fill=INK)
    elif kind == "tail":
        d.polygon([(x + 30, y + 50), (x + 60, y + 14), (x + 84, y + 14), (x + 84, y + 50)],
                  fill=RED, outline=INK, width=2)
        d.rectangle([x + 84, y + 40, x + 160, y + 52], fill=INK)
        d.text((x + 92, y + 42), "VIRGIN", font=font(SANS_B, 8), fill=PAPER)
        d.line([(x + 14, y + 56), (x + w - 14, y + 56)], fill=INK, width=2)
    # banner callout inside art, bottom
    bw = d.textlength(banner, font=font(SANS_B, 8)) + 12
    bx = x + 6
    by = y + h - 20
    d.rectangle([bx, by, bx + bw, by + 15], fill=INK)
    d.text((bx + 6, by + 3), banner, font=font(SANS_B, 8), fill=PAPER)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10
    # top bar
    small_caps(d, "Thursday 26 November 2026", M, y, size=9, fill=INK)
    r = d.textlength("31 STORIES  ·  8 REGIONS", font=font(SANS_B, 9))
    d.text((W - M - r, y), "31 STORIES  ·  8 REGIONS", font=font(SANS_B, 9), fill=INK)
    d.text((W / 2 - 4, y - 1), "◆", font=font(SANS_B, 9), fill=RED)
    y = 28
    rule(d, M, y, CW, width=2)
    # masthead
    mf = font(SERIF_BLACK, 54)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(t, font=mf)) / 2, 34), t, font=mf, fill=INK)
    # eyebrow row
    ey = 92
    small_caps(d, "From Sanaa to Sydney", M, ey, size=9)
    small_caps(d, "All times UTC unless stated", W - M - 190, ey, size=9)
    d.text((W / 2 - 4, ey - 1), "◆", font=font(SANS_B, 9), fill=RED)
    rule(d, M, 108, CW, width=1)
    # sub-headline
    sf = font(SERIF_IT, 15)
    sub = ("Missiles over Riyadh, a wider nuclear order from Pyongyang \u2014 and Asia\u2019s "
           "markets rebound as gold and bitcoin climb back.")
    d.text(((W - d.textlength(sub, font=sf)) / 2, 114), sub, font=sf, fill=INK)
    rule(d, M, 138, CW, width=1)

    # ---- Day in Numbers
    y = 144
    small_caps(d, "The day in numbers", M, y, size=9, fill=RED)
    y = 158
    colw = CW / 5
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * colw
        nf = font(SERIF_BOLD, 26)
        d.text((cx, y), num, font=nf, fill=INK)
        for j, ln in enumerate(lab.split("\n")):
            d.text((cx, y + 30 + j * 10), ln, font=font(SANS, 8), fill=MUTED)
        if i:
            d.line([(cx - 8, y + 2), (cx - 8, y + 46)], fill=FAINT, width=1)
    rule(d, M, 208, CW, width=1)

    # ---- Timeline
    y = 214
    small_caps(d, "Timeline \u2014 UTC", M, y, size=9, fill=RED)
    tw = (CW - 120) / 5
    for i, (tm, txt) in enumerate(TIMELINE):
        tx = M + 120 + i * tw
        d.text((tx, y), tm, font=font(SANS_B, 9), fill=RED)
        lines = fit(d, txt, font(SANS, 8), tw - 8, 3, f"timeline {tm}")
        draw_lines(d, lines, tx, y + 12, font(SANS, 8), INK, 10)
    rule(d, M, 252, CW, width=1)

    # ---- Heroes
    hy, hh = 260, 160
    hw = (CW - 2 * 16) / 3
    for i, hro in enumerate(HEROES):
        hx = M + i * (hw + 16)
        d.text((hx, hy), str(hro["num"]), font=font(SERIF_BOLD, 13), fill=RED)
        small_caps(d, hro["kick"], hx + 16, hy + 3, size=8)
        lines = fit(d, hro["head"], font(SERIF_BOLD, 16), hw, 3, f"hero {hro['num']}")
        draw_lines(d, lines, hx, hy + 16, font(SERIF_BOLD, 16), INK, 19)
        ay = hy + 16 + len(lines) * 19 + 4
        ah = 60
        if hro["art"] == "gulf":
            art_gulf(d, hx, ay, hw, ah)
        elif hro["art"] == "korea":
            art_korea(d, hx, ay, hw, ah)
        else:
            art_chart(d, hx, ay, hw, ah)
        by = ay + ah + 5
        blines = fit(d, hro["body"], font(SANS, 9), hw, 2, f"hero body {hro['num']}")
        draw_lines(d, blines, hx, by, font(SANS, 9), INK, 11)
        small_caps(d, hro["src"], hx, by + len(blines) * 11 + 4, size=7)
        assert by + len(blines) * 11 + 12 <= hy + hh, f"hero {hro['num']} overflows"
    rule(d, M, hy + hh + 6, CW, width=1)

    # ---- Cards (2 rows x 5)
    cw = (CW - 4 * 12) / 5
    ch = 148
    for row in range(2):
        cy0 = 432 + row * (ch + 8)
        for col in range(5):
            c = CARDS[row * 5 + col]
            cx = M + col * (cw + 12)
            rule(d, cx, cy0, cw, fill=INK, width=2)
            d.text((cx, cy0 + 5), str(c["num"]), font=font(SERIF_BOLD, 11), fill=RED)
            small_caps(d, c["kick"], cx + 14, cy0 + 7, size=7)
            lines = fit(d, c["head"], font(SERIF_BOLD, 12), cw, 2, f"card {c['num']}")
            draw_lines(d, lines, cx, cy0 + 20, font(SERIF_BOLD, 12), INK, 14)
            ay = cy0 + 20 + len(lines) * 14 + 4
            ah = 58
            art_panel(d, cx, ay, cw, ah, c["art"], c["banner"])
            by = ay + ah + 4
            blines = fit(d, c["body"], font(SANS, 8), cw, 2, f"card body {c['num']}")
            draw_lines(d, blines, cx, by, font(SANS, 8), INK, 10)
            small_caps(d, c["src"], cx, cy0 + ch - 9, size=7)
    rule(d, M, 738, CW, width=1)

    # ---- World map
    my = 740
    small_caps(d, "Where it happened", M, my, size=9, fill=RED)
    small_caps(d, "13 featured stories  ·  numbered pins  ·  schematic map, not to scale",
               M + 150, my, size=8)
    map_top, map_h = my + 14, 68
    mx0, mx1 = M, W - M
    lon2x = lambda lon: mx0 + (lon + 170) / 360 * (mx1 - mx0)
    lat2y = lambda lat: map_top + (78 - lat) / 136 * map_h
    for poly in CONTINENTS:
        d.polygon([(lon2x(lo), lat2y(la)) for lo, la in poly], fill=LAND, outline=INK)
    d.text((mx0 + 180, map_top + 52), "ATLANTIC", font=font(SANS_B, 7), fill=BLUE)
    d.text((mx0 + 700, map_top + 56), "PACIFIC", font=font(SANS_B, 7), fill=BLUE)
    d.text((mx0 + 430, map_top + 48), "INDIAN", font=font(SANS_B, 7), fill=BLUE)
    for (n, lo, la, dx, dy) in PINS:
        px, py = lon2x(lo) + dx, lat2y(la) + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=PAPER, width=1)
        tw_ = d.textlength(str(n), font=font(SANS_B, 7))
        d.text((px - tw_ / 2, py - 5), str(n), font=font(SANS_B, 7), fill=PAPER)
    # region counts line
    ry = map_top + map_h + 4
    small_caps(d, "Europe 4  ·  Middle East 3  ·  East Asia 4  ·  South Asia 2  ·  "
                  "SE Asia 3  ·  North America 9  ·  Oceania 4  ·  Global 2",
               M, ry, size=8)
    rule(d, M, ry + 14, CW, width=1)

    # ---- Also on
    ay0 = ry + 22
    small_caps(d, "Also on Thursday 26 November", M, ay0, size=9, fill=RED)
    colw2 = CW / 2
    for i, (n, head, src) in enumerate(ALSO):
        col, r = divmod(i, 9)
        ax = M + col * colw2
        ay = ay0 + 14 + r * 10
        d.text((ax, ay), str(n), font=font(SANS_B, 8), fill=RED)
        # headline + source on one line, truncate headline to fit
        hf = font(SANS, 8)
        srcw = d.textlength("  " + src, font=font(SANS_B, 7))
        max_hw = colw2 - 22 - srcw
        hh_ = head
        while d.textlength(hh_, font=hf) > max_hw and len(hh_) > 10:
            hh_ = hh_[:-1]
        if hh_ != head:
            hh_ = hh_.rstrip() + "\u2026"
        d.text((ax + 16, ay), hh_, font=hf, fill=INK)
        d.text((ax + 16 + d.textlength(hh_, font=hf) + 4, ay), src,
               font=font(SANS_B, 7), fill=MUTED)
    rule(d, M, ay0 + 14 + 9 * 10 + 4, CW, width=1)

    # ---- DATE CHECK
    dy = ay0 + 14 + 9 * 10 + 10
    small_caps(d, "Date check \u2014 left out on purpose", M, dy, size=9, fill=RED)
    dc = ("LEFT OUT \u2014 Wed 25 Nov: Champions League (Sporting 2\u20132 Man Utd; PSG 2\u20132 Roma; "
          "Lille 2\u20131 Bayern) \u00b7 Deloitte WA suspension \u00b7 SpaceX FCC approval \u00b7 German GDP +0.1% "
          "\u00b7 Macy\u2019s postponement announced \u00b7 Ras Tanura claim \u00b7 Tue 24 Nov: PIF Tower "
          "strike \u00b7 Mon 23 Nov: Zambia treason charges.  "
          "NOT YET \u2014 Macy\u2019s parade Sat 28 Nov \u00b7 Spain election Sun 29 Nov \u00b7 OPEC+ Sun 29 Nov \u00b7 "
          "CPTPP Council Fri 27 Nov.")
    dlines = fit(d, dc, font(SANS, 8), CW, 3, "date check")
    draw_lines(d, dlines, M, dy + 12, font(SANS, 8), INK, 10)
    rule(d, M, dy + 12 + len(dlines) * 10 + 4, CW, width=1)

    # ---- Footer
    fy = dy + 12 + len(dlines) * 10 + 10
    foot = ("HOW SURE:  CONFIRMED = verified by a named outlet  \u00b7  REPORTED = reported, not officially "
            "confirmed  \u00b7  CLAIM = one side\u2019s claim  \u00b7  ONGOING = still developing.")
    flines = fit(d, foot, font(SANS, 7), CW, 2, "footer")
    draw_lines(d, flines, M, fy, font(SANS, 7), MUTED, 9)
    assert fy + len(flines) * 9 <= H - 6, f"footer overflows: {fy}"
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    data = open(out, "rb").read()
    print(out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("size", img.size, img.mode)


if __name__ == "__main__":
    main()
