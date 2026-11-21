"""Draw the invented passport spread of the Republic of Valtoria.

Everything on the spread is fixed data in this file: no network, no
clock and no randomness (the paper grain uses a fixed seed), so every
run produces the same bytes. The picture is an open passport spread,
1024 by 724 pixels: a data page on the left and a visa page on the
right, for a country that does not exist.

The Republic of Valtoria is a small Adriatic republic (capital
Mirenna) invented for this document. Its neighbours in the travel
history are the invented Dravnia and the real Croatia. Every date is
consistent: the passport was issued 12 FEB 2024, it expires
12 FEB 2034, and every stamp falls between those dates, in
chronological order, with matching entry/exit pairs.

Run it from the repository root with:  python3 tools/generate_passport.py
It writes entry.png next to main.py.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 724
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

# --- palette ---------------------------------------------------------------
INK = (28, 30, 38)
MUTED = (104, 98, 88)
RULE = (60, 58, 52)
PAGE_L = (245, 240, 225)   # data page cream
PAGE_R = (248, 243, 230)   # visa page cream
DESK = (52, 55, 63)        # dark desk around the spread
NAVY = (31, 58, 96)
GOLD = (176, 138, 58)
RED = (143, 58, 42)
BLUE_STAMP = (42, 77, 143)
PURPLE_STAMP = (107, 63, 160)
RED_STAMP = (143, 58, 42)
SKIN = (224, 170, 128)
SKIN_SHADOW = (203, 148, 106)
HAIR = (51, 38, 31)
TEAL = (47, 93, 99)


def pick_font(stem: str, size: int) -> ImageFont.FreeTypeFont:
    candidate = FONT_DIR / stem
    if candidate.exists():
        return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def serif_bold(size: int):
    return pick_font("DejaVuSerif-Bold.ttf", size)


def serif(size: int):
    return pick_font("DejaVuSerif.ttf", size)


def sans_bold(size: int):
    return pick_font("DejaVuSans-Bold.ttf", size)


def sans(size: int):
    return pick_font("DejaVuSans.ttf", size)


def mono(size: int):
    return pick_font("DejaVuSansMono.ttf", size)


def mono_bold(size: int):
    return pick_font("DejaVuSansMono-Bold.ttf", size)


def spaced(draw: ImageDraw.ImageDraw, cx: int, y: int, text: str,
           font: ImageFont.FreeTypeFont, fill, tracking: int = 2):
    """Draw text centred on cx, with extra letter spacing."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


# --- ICAO MRZ check digits -------------------------------------------------
_MRZ_VALUES = {chr(ord("0") + i): i for i in range(10)}
_MRZ_VALUES.update({chr(ord("A") + i): 10 + i for i in range(26)})
_MRZ_VALUES["<"] = 0


def check_digit(field: str) -> str:
    total = 0
    for i, ch in enumerate(field):
        total += _MRZ_VALUES[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines() -> tuple[str, str]:
    line1 = ("P<VTAKOVAC<<MARA<ELENA").ljust(44, "<")
    assert len(line1) == 44
    doc_no = "VT4829137"
    dob = "940314"          # 14 MAR 1994
    expiry = "340212"       # 12 FEB 2034
    personal = "14039477<<<<<<"
    body = (
        doc_no + check_digit(doc_no)
        + "VTA"
        + dob + check_digit(dob)
        + "F"
        + expiry + check_digit(expiry)
        + personal + check_digit(personal)
    )
    line2 = body + check_digit(body)
    assert len(line2) == 44
    return line1, line2


# --- small drawn emblems ---------------------------------------------------
def coat_of_arms(draw: ImageDraw.ImageDraw, cx: int, cy: int, s: float,
                 line: tuple, fill: tuple):
    """Valtoria's arms: a shield with a star over twin peaks."""
    w, h = 34 * s, 40 * s
    x0, y0 = cx - w / 2, cy - h / 2
    shield = [
        (x0, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.62),
        (cx, y0 + h), (x0, y0 + h * 0.62),
    ]
    draw.polygon(shield, outline=line, fill=fill, width=max(1, int(2 * s)))
    # twin peaks
    draw.line([(x0 + w * 0.18, y0 + h * 0.66), (x0 + w * 0.38, y0 + h * 0.38),
               (x0 + w * 0.52, y0 + h * 0.60), (x0 + w * 0.68, y0 + h * 0.34),
               (x0 + w * 0.84, y0 + h * 0.66)], fill=line,
              width=max(1, int(2 * s)))
    # star above the peaks
    sx, sy, r = cx, y0 + h * 0.24, 5 * s
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=line)


def ghost_emblem(img: Image.Image, cx: int, cy: int, scale: float):
    """A faint watermark of the arms, stamped into a page."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    coat_of_arms(d, cx, cy, scale, (NAVY[0], NAVY[1], NAVY[2], 26),
                 (NAVY[0], NAVY[1], NAVY[2], 10))
    img.alpha_composite(layer)


# --- the portrait ----------------------------------------------------------
def draw_portrait(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int):
    """A stylised flat-illustration portrait: a Valtorian woman, 32.

    Drawn entirely with PIL shapes, in the manner of a passport
    photograph rendered as a line-and-flat-colour illustration. The
    drawing happens on its own layer, clipped to the photo frame.
    """
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = w // 2
    # backdrop: pale studio gradient
    for i in range(h):
        t = i / h
        r = int(178 + (138 - 178) * t)
        g = int(192 + (158 - 192) * t)
        b = int(198 + (168 - 198) * t)
        d.line([(0, i), (w, i)], fill=(r, g, b))
    # soft light halo behind the head
    d.ellipse([-30, -50, w + 30, 92], fill=(206, 215, 217))
    # shoulders / jacket
    d.polygon([
        (8, h), (18, h - 52), (cx - 52, h - 62),
        (cx - 30, h - 34), (cx, h - 26),
        (cx + 30, h - 34), (cx + 52, h - 62),
        (w - 18, h - 52), (w - 8, h),
    ], fill=TEAL)
    # blouse V, small
    d.polygon([(cx - 18, h - 48), (cx, h - 28),
               (cx + 18, h - 48), (cx + 12, h - 52),
               (cx, h - 38), (cx - 12, h - 52)],
              fill=(238, 234, 222))
    # neck
    d.polygon([(cx - 13, 108), (cx + 13, 108),
               (cx + 20, 138), (cx - 20, 138)], fill=SKIN_SHADOW)
    d.rectangle([cx - 13, 96, cx + 13, 122], fill=SKIN)
    # hair, back mass
    d.ellipse([cx - 46, 6, cx + 46, 108], fill=HAIR)
    d.polygon([(cx - 46, 40), (cx - 52, 150), (cx - 30, 158),
               (cx - 38, 60)], fill=HAIR)
    d.polygon([(cx + 46, 40), (cx + 52, 150), (cx + 30, 158),
               (cx + 38, 60)], fill=HAIR)
    # face
    d.ellipse([cx - 34, 26, cx + 34, 112], fill=SKIN)
    # jaw shading, right side
    d.ellipse([cx + 8, 30, cx + 36, 112], fill=SKIN_SHADOW)
    d.ellipse([cx - 32, 28, cx + 26, 106], fill=SKIN)
    # fringe: a band across the forehead, side-parted
    d.polygon([(cx - 37, 46), (cx - 36, 16), (cx - 18, 6), (cx + 2, 4),
               (cx + 22, 10), (cx + 35, 20), (cx + 37, 46),
               (cx + 26, 34), (cx + 8, 28), (cx - 12, 28),
               (cx - 26, 34)], fill=HAIR)
    d.polygon([(cx - 36, 30), (cx - 40, 70), (cx - 30, 66),
               (cx - 32, 40)], fill=HAIR)
    d.polygon([(cx + 36, 30), (cx + 40, 70), (cx + 30, 66),
               (cx + 32, 40)], fill=HAIR)
    # ears
    d.ellipse([cx - 40, 62, cx - 30, 82], fill=SKIN)
    d.ellipse([cx + 30, 62, cx + 40, 82], fill=SKIN)
    # earring
    d.ellipse([cx - 37, 82, cx - 33, 86], fill=GOLD)
    # brows, gently curved
    d.line([(cx - 24, 62), (cx - 16, 58), (cx - 8, 58)], fill=HAIR, width=3)
    d.line([(cx + 8, 58), (cx + 16, 58), (cx + 24, 62)], fill=HAIR, width=3)
    # eyes
    for ex in (-16, 16):
        d.ellipse([cx + ex - 8, 66, cx + ex + 8, 74],
                  fill=(250, 248, 242))
        d.ellipse([cx + ex - 4, 67, cx + ex + 4, 74],
                  fill=(46, 32, 24))
        d.line([(cx + ex - 8, 66), (cx + ex + 8, 66)],
               fill=(46, 32, 24), width=2)
    # nose
    d.line([(cx + 1, 76), (cx - 1, 90), (cx + 4, 93)],
           fill=SKIN_SHADOW, width=2)
    # lips
    d.polygon([(cx - 9, 100), (cx, 97), (cx + 9, 100),
               (cx, 106)], fill=(176, 106, 94))
    d.line([(cx - 9, 100), (cx + 9, 100)], fill=(140, 78, 68),
           width=1)
    # cheek hint
    d.ellipse([cx - 30, 84, cx - 14, 94], fill=(226, 158, 128))
    d.ellipse([cx + 14, 84, cx + 30, 94], fill=(226, 158, 128))
    return layer


# --- stamps ----------------------------------------------------------------
def round_stamp(cx: int, cy: int, diameter: int, colour, lines, tilt: float,
                img: Image.Image):
    """A circular border-control stamp, drawn on its own layer so the
    ink can be translucent and slightly rotated, like a real stamp."""
    size = diameter + 24
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size // 2
    r = diameter // 2
    ink = colour + (215,)
    faint = colour + (170,)
    d.ellipse([c - r, c - r, c + r, c + r], outline=ink, width=3)
    d.ellipse([c - r + 7, c - r + 7, c + r - 7, c + r - 7], outline=faint,
              width=1)
    kind, country, place, date = lines
    d.text((c, c - 28), kind, font=sans_bold(13), fill=ink, anchor="mm")
    d.text((c, c - 10), country, font=sans_bold(12), fill=ink, anchor="mm")
    d.text((c, c + 6), place, font=sans(8), fill=ink, anchor="mm")
    d.text((c, c + 27), date, font=sans_bold(9), fill=ink, anchor="mm")
    # small star between place and date
    sx, sy, sr = c, c + 17, 3
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else sr * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(star, fill=ink)
    layer = layer.rotate(tilt, resample=Image.BICUBIC, center=(c, c))
    img.alpha_composite(layer, (cx - size // 2, cy - size // 2))


# --- the spread ------------------------------------------------------------
def field(draw, x, y, label, value, label_font, value_font, width=240):
    draw.text((x, y), label, font=label_font, fill=MUTED)
    draw.text((x, y + 12), value, font=value_font, fill=INK)


def draw_spread() -> Image.Image:
    img = Image.new("RGBA", (W, H), DESK + (255,))
    draw = ImageDraw.Draw(img)

    # desk vignette
    for i in range(40):
        draw.rectangle([i, i, W - 1 - i, H - 1 - i],
                       outline=(52 - i // 3, 55 - i // 3, 63 - i // 3))

    # spread body
    x0, y0, x1, y1 = 24, 24, 1000, 700
    mid = (x0 + x1) // 2
    draw.rectangle([x0, y0, mid, y1], fill=PAGE_L)
    draw.rectangle([mid, y0, x1, y1], fill=PAGE_R)
    # gutter shadow + centre fold
    for i in range(14):
        a = 70 - i * 5
        draw.line([(mid - 7 + i, y0), (mid - 7 + i, y1)],
                  fill=(0, 0, 0, a))
        draw.line([(mid + 7 - i, y0), (mid + 7 - i, y1)],
                  fill=(0, 0, 0, a))
    draw.line([(mid, y0), (mid, y1)], fill=(120, 112, 96), width=1)
    # outer border of the spread
    draw.rectangle([x0, y0, x1, y1], outline=(90, 82, 68), width=2)
    # paper grain, fixed seed
    rnd = random.Random(7)
    grain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grain)
    for _ in range(2600):
        gx = rnd.randint(x0, x1)
        gy = rnd.randint(y0, y1)
        gd.point((gx, gy), fill=(120, 110, 90, rnd.randint(8, 22)))
    img.alpha_composite(grain)
    draw = ImageDraw.Draw(img)

    ghost_emblem(img, 264, 430, 4.2)
    ghost_emblem(img, 760, 380, 5.2)
    draw = ImageDraw.Draw(img)

    # ================= LEFT PAGE: data page =================
    lx, lw = x0, mid - x0          # 24, 488
    # header
    coat_of_arms(draw, lx + 42, 62, 0.95, NAVY, (0, 0, 0, 0))
    draw.text((lx + 70, 44), "REPUBLIC OF VALTORIA",
              font=serif_bold(20), fill=NAVY)
    spaced(draw, lx + lw // 2 + 14, 72, "REPUBLIKA VALTORIJA",
           sans(9), MUTED, tracking=3)
    draw.line([(lx + 24, 92), (lx + lw - 24, 92)], fill=RULE, width=1)
    draw.line([(lx + 24, 95), (lx + lw - 24, 95)], fill=RULE, width=1)
    # document row
    draw.text((lx + 24, 104), "PASSPORT  •  PUTOVNICA",
              font=sans_bold(10), fill=INK)
    draw.text((lx + lw - 24, 104), "TYPE P  •  CODE VTA",
              font=sans_bold(10), fill=INK, anchor="ra")

    # portrait
    px, py, pw, ph = lx + 24, 132, 148, 188
    draw.rectangle([px - 2, py - 2, px + pw + 2, py + ph + 2],
                   outline=INK, width=2)
    img.alpha_composite(draw_portrait(draw, px, py, pw, ph), (px, py))
    draw = ImageDraw.Draw(img)
    draw.text((px + pw // 2, py + ph + 6), "PHOTOGRAPH",
              font=sans(8), fill=MUTED, anchor="ma")

    # fields right of the portrait
    fx = lx + 196
    lab_f, val_f = sans(9), sans_bold(13)
    field(draw, fx, 132, "SURNAME / PREZIME", "KOVAC", lab_f, val_f)
    field(draw, fx, 164, "GIVEN NAMES / IME", "MARA ELENA", lab_f, val_f)
    field(draw, fx, 196, "NATIONALITY / DRŽAVLJANSTVO", "VALTORIAN",
          lab_f, val_f)
    field(draw, fx, 228, "SEX / SPOL  •  DATE OF BIRTH / ROĐENJE",
          "F  •  14 MAR 1994", lab_f, val_f)
    field(draw, fx, 260, "PLACE OF BIRTH / MJESTO ROĐENJA",
          "MIRENNA, VALTORIA", lab_f, val_f)
    field(draw, fx, 292, "PERSONAL NO. / OSOBNI BROJ", "140394-77",
          lab_f, val_f)

    # lower data rows, full width
    draw.line([(lx + 24, 352), (lx + lw - 24, 352)], fill=RULE, width=1)
    field(draw, lx + 24, 364, "PASSPORT NO. / BROJ PUTOVNICE",
          "VT 4829137", lab_f, sans_bold(15))
    field(draw, lx + 196, 364, "DATE OF ISSUE / IZDANO",
          "12 FEB 2024", lab_f, sans_bold(15))
    field(draw, lx + 348, 364, "EXPIRY / VRIJEDI DO",
          "12 FEB 2034", lab_f, sans_bold(15))
    field(draw, lx + 24, 404, "AUTHORITY / TIJELO",
          "MINISTRY OF THE INTERIOR — MIRENNA", lab_f, sans_bold(12))
    field(draw, lx + 348, 404, "HEIGHT / VISINA", "172 cm",
          lab_f, sans_bold(13))

    # signature
    draw.line([(lx + 24, 470), (lx + 240, 470)], fill=RULE, width=1)
    draw.text((lx + 24, 442), "Mara Elena Kovac",
              font=serif(20), fill=(52, 58, 92))
    draw.text((lx + 24, 474), "HOLDER'S SIGNATURE / POTPIS",
              font=sans(8), fill=MUTED)
    # issuing stamp, small rectangular, bottom right of data area
    draw.rectangle([lx + 300, 436, lx + 464, 486], outline=NAVY, width=2)
    draw.text((lx + 382, 444), "ISSUED AT MIRENNA",
              font=sans_bold(9), fill=NAVY, anchor="ma")
    draw.text((lx + 382, 458), "12 FEB 2024",
              font=sans_bold(11), fill=NAVY, anchor="ma")
    draw.text((lx + 382, 472), "No. 004821", font=sans(8), fill=NAVY,
              anchor="ma")

    # MRZ
    draw.rectangle([lx + 24, 500, lx + lw - 24, 560], fill=(253, 252, 247),
                   outline=RULE, width=1)
    l1, l2 = mrz_lines()
    draw.text((lx + lw // 2, 508), l1, font=mono(13), fill=INK, anchor="ma")
    draw.text((lx + lw // 2, 530), l2, font=mono(13), fill=INK, anchor="ma")
    draw.text((lx + 24, 566), "P<VTAKOVAC<<MARA<ELENA — MACHINE READABLE ZONE",
              font=sans(8), fill=MUTED)
    draw.text((lx + lw - 24, 566), "PAGE 2", font=sans_bold(9), fill=MUTED,
              anchor="ra")

    # ================= RIGHT PAGE: visas =================
    rx, rw = mid, x1 - mid        # 512, 488
    draw.text((rx + rw // 2, 40), "VISAS", font=serif_bold(18), fill=NAVY,
              anchor="ma")
    spaced(draw, rx + rw // 2, 64, "VIZE", sans(9), MUTED, tracking=4)
    draw.line([(rx + 24, 84), (rx + rw - 24, 84)], fill=RULE, width=1)
    draw.line([(rx + 24, 87), (rx + rw - 24, 87)], fill=RULE, width=1)

    # --- Ostara visa sticker ---
    vx, vy, vw, vh = rx + 24, 100, rw - 48, 138
    draw.rectangle([vx, vy, vx + vw, vy + vh], fill=(220, 232, 228),
                   outline=NAVY, width=2)
    draw.rectangle([vx + 5, vy + 5, vx + vw - 5, vy + vh - 5],
                   outline=NAVY, width=1)
    coat_of_arms(draw, vx + 30, vy + 28, 0.55, NAVY, (0, 0, 0, 0))
    draw.text((vx + 56, vy + 12), "KINGDOM OF OSTARA",
              font=serif_bold(14), fill=NAVY)
    draw.text((vx + 56, vy + 32), "VISA — TYPE C  •  SHORT STAY",
              font=sans_bold(9), fill=INK)
    draw.text((vx + 14, vy + 58), "VALID  08 SEP 2024  —  07 DEC 2024",
              font=sans_bold(11), fill=INK)
    draw.text((vx + 14, vy + 76), "ENTRIES: SINGLE  •  STAY: UP TO 90 DAYS",
              font=sans(10), fill=INK)
    draw.text((vx + 14, vy + 94), "CONDITION: NO EMPLOYMENT — NO PUBLIC FUNDS",
              font=sans_bold(10), fill=RED)
    draw.text((vx + 14, vy + 112), "ISSUED AT MIRENNA, 02 SEP 2024  •  FEE PAID 45 VTD",
              font=sans(9), fill=INK)
    draw.text((vx + vw - 14, vy + 112), "No. OS-22914",
              font=sans_bold(9), fill=NAVY, anchor="ra")

    # --- stamps, 2 columns x 4 rows ---
    stamps = [
        ("EXIT", "VALTORIA", "MIRENNA INTL APT", "03 MAY 2024",
         BLUE_STAMP, -6),
        ("ENTRY", "DRAVNIA", "KOROVO BORDER", "03 MAY 2024",
         PURPLE_STAMP, 5),
        ("EXIT", "DRAVNIA", "KOROVO BORDER", "17 MAY 2024",
         PURPLE_STAMP, -4),
        ("ENTRY", "VALTORIA", "MIRENNA", "17 MAY 2024", BLUE_STAMP, 7),
        ("EXIT", "VALTORIA", "MIRENNA INTL APT", "08 SEP 2024",
         BLUE_STAMP, -5),
        ("ENTRY", "CROATIA", "DUBROVNIK", "08 SEP 2024", RED_STAMP, 4),
        ("EXIT", "CROATIA", "DUBROVNIK", "21 SEP 2024", RED_STAMP, -7),
        ("ENTRY", "VALTORIA", "MIRENNA", "21 SEP 2024", BLUE_STAMP, 6),
    ]
    grid_x0, grid_y0 = rx + 24, 258
    cell_w, cell_h = (rw - 48) // 2, 104
    for i, (kind, country, place, date, colour, tilt) in enumerate(stamps):
        col, row = i % 2, i // 2
        cx = grid_x0 + col * cell_w + cell_w // 2
        cy = grid_y0 + row * cell_h + cell_h // 2
        round_stamp(cx, cy, 92, colour, (kind, country, place, date),
                    tilt, img)
    draw = ImageDraw.Draw(img)

    draw.text((rx + 24, 678),
              "PAGES 12–13  •  CONDITIONS OVERLEAF  •  SEE PAGE 14",
              font=sans(8), fill=MUTED)
    draw.text((rx + rw - 24, 678), "VALTORIA", font=sans_bold(8),
              fill=MUTED, anchor="ra")
    return img.convert("RGB")


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    out = here / "entry.png"
    img = draw_spread()
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
