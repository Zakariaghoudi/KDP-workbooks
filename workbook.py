#!/usr/bin/env python3
"""
مولّد كتب تمارين تعليمية ملوّنة (PDF) لـ Amazon KDP - مقاس 8.5x11 إنش.

    pip install reportlab arabic-reshaper python-bidi
    python workbook.py all
    python workbook.py grade1 --pages 100
"""
import argparse
import math
import os
import random
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ======================= الإعدادات (عدّلها هنا فقط) =======================
AUTHOR = "ZAKARIA GHOUDI"
YEAR = 2026
SEED = "kdp-v1"
PAGE_W, PAGE_H = 8.5 * 72, 11 * 72
M = 0.75 * 72
TOP = PAGE_H - M - 92
BOTTOM = M + 28
CONTENT_H = TOP - BOTTOM
INK = HexColor("#1F2A44")

LEVELS = {
    "prek": {
        "title": "تمارين الرياضيات", "sub": "مستوى التحضيري", "age": "من 4 إلى 5 سنوات",
        "symbols": ["1", "2", "3", "4", "5"],
        "pal": {"main": "#FF7A59", "light": "#FFF1EB", "accent": "#FFC93C", "tint": "#FFC9B8",
                "shapes": ["#FF7A59", "#FFC93C", "#26A69A", "#7E57C2"]},
        "plan": [("count", 10), ("trace", 10), ("compare", 10), ("add", 5),
                 ("count", 10), ("compare", 10), ("add", 10), ("trace", 10)],
    },
    "grade1": {
        "title": "تمارين الرياضيات", "sub": "السنة الأولى", "age": "من 6 إلى 7 سنوات",
        "symbols": ["+", "7", "-", "3", "="],
        "pal": {"main": "#2E86DE", "light": "#EBF4FD", "accent": "#FF9F43", "tint": "#B5D5F5",
                "shapes": ["#2E86DE", "#FF9F43", "#1DB98A", "#EE5A6F"]},
        "plan": [("add", 10), ("sub", 10), ("count", 20), ("compare", 20),
                 ("add", 20), ("sub", 20), ("missing", 20), ("compare", 20)],
    },
    "grade2": {
        "title": "تمارين الرياضيات", "sub": "السنة الثانية", "age": "من 7 إلى 8 سنوات",
        "symbols": ["×", "12", "+", "9", "="],
        "pal": {"main": "#7C4DFF", "light": "#F1ECFF", "accent": "#1DD1A1", "tint": "#CDBEFF",
                "shapes": ["#7C4DFF", "#1DD1A1", "#FF6B6B", "#FECA57"]},
        "plan": [("add", 100), ("sub", 100), ("missing", 100), ("compare", 100),
                 ("mult", [2, 5, 10]), ("add", 100), ("sub", 100), ("mult", [2, 3, 4, 5, 10])],
    },
}

TYPES = {
    "count":   ("العدّ", "عدّ الأشكال ثم اكتب العدد في المربع"),
    "trace":   ("كتابة الأرقام", "تتبّع الأرقام ثم اكتبها بنفسك"),
    "compare": ("المقارنة", "اكتب في الدائرة:  >  أو  <  أو  ="),
    "add":     ("الجمع", "احسب ناتج الجمع"),
    "sub":     ("الطرح", "احسب ناتج الطرح"),
    "missing": ("العدد الناقص", "أكمل بالعدد الناقص"),
    "mult":    ("الضرب", "احسب ناتج الضرب"),
}
# ==========================================================================

FONT = "AR"


def setup_font():
    candidates = [
        os.environ.get("FONT_PATH", ""),
        "font.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(FONT, path))
                return path
            except Exception:
                continue
    sys.exit("لم أجد خطاً عربياً. ثبّت: sudo apt-get install -y fonts-dejavu-core "
             "أو ضع ملف font.ttf بجانب السكريبت.")


def ar(text):
    return get_display(arabic_reshaper.reshape(text))


def col(h):
    return HexColor(h)


# ----------------------------- أدوات الرسم -----------------------------
def star(c, x, y, r, stroke=0):
    p = c.beginPath()
    for k in range(10):
        ang = math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.45
        px, py = x + rad * math.cos(ang), y + rad * math.sin(ang)
        p.moveTo(px, py) if k == 0 else p.lineTo(px, py)
    p.close()
    c.drawPath(p, stroke=stroke, fill=1)


def shape(c, kind, x, y, r):
    if kind == "circle":
        c.circle(x, y, r, stroke=0, fill=1)
    elif kind == "square":
        c.roundRect(x - r, y - r, 2 * r, 2 * r, 3, stroke=0, fill=1)
    else:
        star(c, x, y, r * 1.3)


def band(c, pal, title, name=True):
    """شريط ملوّن في أعلى الصفحة"""
    bh = 50
    y = PAGE_H - M - bh
    c.setFillColor(col(pal["main"]))
    c.roundRect(M, y, PAGE_W - 2 * M, bh, 14, stroke=0, fill=1)
    c.setFillColor(col(pal["accent"]))
    star(c, PAGE_W / 2 + 20, y + bh / 2, 11)
    c.circle(PAGE_W / 2 + 52, y + bh / 2 + 8, 4, stroke=0, fill=1)
    c.circle(PAGE_W / 2 - 12, y + bh / 2 - 9, 3, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT, 24)
    c.drawRightString(PAGE_W - M - 18, y + 15, ar(title))
    if name:
        c.setFont(FONT, 13)
        c.roundRect(M + 14, y + 12, 170, 26, 8, stroke=0, fill=1)
        c.drawString(M + 14 + 170 + 8, y + 19, ar("الاسم:"))


def header(c, kind, pal):
    title, instr = TYPES[kind]
    band(c, pal, title)
    c.setFillColor(INK)
    c.setFont(FONT, 15)
    c.drawRightString(PAGE_W - M, PAGE_H - M - 74, ar(instr))
    c.setStrokeColor(col(pal["tint"]))
    c.setLineWidth(2)
    c.line(M, PAGE_H - M - 82, PAGE_W - M, PAGE_H - M - 82)


def footer(c, pal):
    c.setFillColor(col(pal["main"]))
    c.circle(PAGE_W / 2, M / 2 + 4, 12, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT, 10)
    c.drawCentredString(PAGE_W / 2, M / 2 + 0.5, str(c.getPageNumber()))
    c.setFillColor(INK)


def draw_tokens(c, x, y, tokens, pal, size=26):
    """tokens: نص | "[]" مربع إجابة | "()" دائرة | "__" خط إجابة"""
    for t in tokens:
        if t in ("[]", "()"):
            c.setFillColor(white)
            c.setStrokeColor(col(pal["main"]))
            c.setLineWidth(2)
            if t == "[]":
                c.roundRect(x, y - 8, 40, 40, 8, stroke=1, fill=1)
            else:
                c.circle(x + 20, y + 12, 20, stroke=1, fill=1)
            x += 50
        elif t == "__":
            c.setStrokeColor(INK)
            c.setLineWidth(1.5)
            c.line(x, y - 4, x + 60, y - 4)
            x += 70
        else:
            c.setFillColor(INK)
            c.setFont(FONT, size)
            c.drawString(x, y, t)
            x += pdfmetrics.stringWidth(t, FONT, size)


def badge(c, x, y, n, pal):
    c.setFillColor(col(pal["main"]))
    c.circle(x, y, 11, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT, 11)
    c.drawCentredString(x, y - 4, str(n))


def problem_grid(c, items, pal):
    cw = (PAGE_W - 2 * M) / 2
    rh = CONTENT_H / 5
    for i, tokens in enumerate(items):
        col_i, row = i % 2, i // 2
        x = M + cw * (1 - col_i) + 7
        top = TOP - rh * row - 7
        w, h = cw - 14, rh - 14
        c.setFillColor(col(pal["light"]))
        c.setStrokeColor(col(pal["tint"]))
        c.setLineWidth(1.5)
        c.roundRect(x, top - h, w, h, 14, stroke=1, fill=1)
        badge(c, x + w - 18, top - 18, i + 1, pal)
        draw_tokens(c, x + 16, top - h / 2 - 8, tokens, pal)


# ----------------------------- أنواع الصفحات -----------------------------
def page_add(c, mx, rng, pal):
    items, ans = [], []
    for _ in range(10):
        if mx <= 20:
            a = rng.randint(0, mx - 1)
            b = rng.randint(1, mx - a)
        else:
            a = rng.randint(10, mx - 5)
            b = rng.randint(5, mx - a)
        items.append([f"{a} + {b} =", "__"])
        ans.append(str(a + b))
    problem_grid(c, items, pal)
    return ans


def page_sub(c, mx, rng, pal):
    lo = 1 if mx <= 20 else 10
    items, ans = [], []
    for _ in range(10):
        a = rng.randint(lo, mx)
        b = rng.randint(0 if mx <= 20 else 1, a)
        items.append([f"{a} - {b} =", "__"])
        ans.append(str(a - b))
    problem_grid(c, items, pal)
    return ans


def page_missing(c, mx, rng, pal):
    items, ans = [], []
    for _ in range(10):
        total = rng.randint(2, mx)
        a = rng.randint(0, total)
        items.append([f"{a} + ", "[]", f" = {total}"])
        ans.append(str(total - a))
    problem_grid(c, items, pal)
    return ans


def page_mult(c, tables, rng, pal):
    items, ans = [], []
    for _ in range(10):
        a, b = rng.choice(tables), rng.randint(1, 10)
        if rng.random() < 0.5:
            a, b = b, a
        items.append([f"{a} × {b} =", "__"])
        ans.append(str(a * b))
    problem_grid(c, items, pal)
    return ans


def page_compare(c, mx, rng, pal):
    items, ans = [], []
    for _ in range(10):
        a = rng.randint(0, mx)
        b = a if rng.random() < 0.15 else rng.randint(0, mx)
        items.append([f"{a}  ", "()", f"  {b}"])
        ans.append(">" if a > b else "<" if a < b else "=")
    problem_grid(c, items, pal)
    return ans


def page_count(c, mx, rng, pal):
    cw, ch = (PAGE_W - 2 * M) / 2, CONTENT_H / 4
    kinds = ["circle", "square", "star"]
    ans = []
    for i in range(8):
        col_i, row = i % 2, i // 2
        bx, by = M + cw * (1 - col_i), TOP - ch * (row + 1)
        c.setFillColor(col(pal["light"]))
        c.setStrokeColor(col(pal["tint"]))
        c.setLineWidth(1.5)
        c.roundRect(bx + 7, by + 7, cw - 14, ch - 14, 14, stroke=1, fill=1)
        n = rng.randint(1, mx)
        kind = rng.choice(kinds)
        c.setFillColor(col(rng.choice(pal["shapes"])))
        for k in range(n):
            shape(c, kind, bx + 30 + (k % 5) * 28, by + ch - 36 - (k // 5) * 28, 10)
        c.setFillColor(white)
        c.setStrokeColor(col(pal["main"]))
        c.setLineWidth(2)
        c.roundRect(bx + cw - 66, by + ch / 2 - 22, 42, 42, 8, stroke=1, fill=1)
        badge(c, bx + cw - 24, by + ch - 24, i + 1, pal)
        ans.append(str(n))
    return ans


def page_trace(c, mx, rng, pal):
    nums = sorted(rng.sample(range(1, mx + 1), 5))
    rh = CONTENT_H / 5
    for r, n in enumerate(nums):
        top = TOP - rh * r - 6
        h = rh - 12
        c.setFillColor(col(pal["light"]))
        c.setStrokeColor(col(pal["tint"]))
        c.setLineWidth(1.5)
        c.roundRect(M, top - h, PAGE_W - 2 * M, h, 14, stroke=1, fill=1)
        y = top - h + 28
        c.setFont(FONT, 72)
        for k in range(6):
            c.setFillColor(col(pal["main"]) if k == 0 else col(pal["tint"]))
            c.drawString(M + 16 + k * 78, y, str(n))
        c.setStrokeColor(col(pal["main"]))
        c.setLineWidth(1)
        c.setDash(2, 4)
        c.line(M + 12, y - 8, PAGE_W - M - 12, y - 8)
        c.setDash()
    return []


PAGES = {"count": page_count, "trace": page_trace, "compare": page_compare,
         "add": page_add, "sub": page_sub, "missing": page_missing, "mult": page_mult}


# ----------------------------- الغلاف والصفحات الخاصة -----------------------------
def cover(c, cfg, author):
    pal = cfg["pal"]
    bx, bw = M, PAGE_W - 2 * M
    c.setFillColor(col(pal["light"]))
    c.roundRect(bx, M, bw, PAGE_H - 2 * M, 28, stroke=0, fill=1)
    by, bh = PAGE_H - M - 380, 380
    c.setFillColor(col(pal["main"]))
    c.roundRect(bx, by, bw, bh, 28, stroke=0, fill=1)

    rng = random.Random(11)
    for _ in range(26):
        x = rng.uniform(bx + 20, bx + bw - 20)
        y = rng.uniform(by + 20, by + bh - 20)
        if abs(x - PAGE_W / 2) < 190 and 90 < PAGE_H - M - y < 330:
            continue
        c.setFillColor(col(rng.choice([pal["accent"], "#FFFFFF", pal["tint"]])))
        if rng.random() < 0.5:
            star(c, x, y, rng.uniform(8, 16))
        else:
            c.circle(x, y, rng.uniform(4, 9), stroke=0, fill=1)

    c.setFillColor(white)
    c.setFont(FONT, 42)
    c.drawCentredString(PAGE_W / 2, PAGE_H - M - 140, ar(cfg["title"]))
    c.setFillColor(col(pal["accent"]))
    c.roundRect(PAGE_W / 2 - 160, PAGE_H - M - 240, 320, 62, 31, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont(FONT, 30)
    c.drawCentredString(PAGE_W / 2, PAGE_H - M - 220, ar(cfg["sub"]))
    c.setFillColor(white)
    c.setFont(FONT, 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - M - 295, ar(cfg["age"]))

    for k, s in enumerate(cfg["symbols"]):
        cx = PAGE_W / 2 + (k - 2) * 92
        c.setFillColor(col(pal["shapes"][k % 4]))
        c.circle(cx, 262, 38, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont(FONT, 38)
        c.drawCentredString(cx, 249, s)

    c.setFillColor(INK)
    c.setFont(FONT, 22)
    c.drawCentredString(PAGE_W / 2, 165, ar("كتاب تمارين وأنشطة ممتعة"))
    c.setFillColor(col(pal["main"]))
    c.roundRect(PAGE_W / 2 - 150, M + 28, 300, 46, 23, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont(FONT, 18)
    c.drawCentredString(PAGE_W / 2, M + 44, author)
    c.showPage()


def copyright_page(c, pal, author):
    c.setFillColor(col(pal["main"]))
    c.roundRect(PAGE_W / 2 - 40, PAGE_H / 2 + 40, 80, 6, 3, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont(FONT, 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 10, f"© {YEAR} {author}")
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 12, ar("جميع الحقوق محفوظة"))
    c.showPage()


def answer_pages(c, answers, pal):
    def new_page(first=False):
        if not first:
            c.showPage()
        band(c, pal, "الأجوبة", name=False)
        return PAGE_H - M - 85

    y = new_page(first=True)
    n = 0
    for page_no, items in answers:
        if not items:
            continue
        if y - 40 < BOTTOM:
            footer(c, pal)
            y = new_page()
        if n % 2 == 0:
            c.setFillColor(col(pal["light"]))
            c.roundRect(M, y - 26, PAGE_W - 2 * M, 38, 8, stroke=0, fill=1)
        n += 1
        c.setFillColor(col(pal["main"]))
        c.setFont(FONT, 13)
        c.drawRightString(PAGE_W - M - 12, y - 8, ar(f"صفحة {page_no}"))
        c.setFillColor(INK)
        c.setFont(FONT, 12)
        for part in (0, 1):
            chunk = items[part * 5:(part + 1) * 5]
            line = "    ".join(f"{part * 5 + i + 1}) {a}" for i, a in enumerate(chunk))
            c.drawString(M + 12, y - (part * 16), line)
        y -= 42
    footer(c, pal)


def notes_page(c, pal):
    band(c, pal, "ملاحظات", name=False)
    c.setStrokeColor(col(pal["tint"]))
    c.setLineWidth(1)
    y = PAGE_H - M - 90
    while y > BOTTOM:
        c.line(M, y, PAGE_W - M, y)
        y -= 32
    footer(c, pal)
    c.showPage()


def build(level, pages, author):
    cfg = LEVELS[level]
    pal = cfg["pal"]
    out = f"workbook_{level}.pdf"
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"{cfg['title']} - {cfg['sub']}")
    c.setAuthor(author)
    cover(c, cfg, author)
    copyright_page(c, pal, author)

    answers = []
    for i in range(pages):
        kind, param = cfg["plan"][i % len(cfg["plan"])]
        rng = random.Random(f"{SEED}-{level}-{i}")
        header(c, kind, pal)
        answers.append((c.getPageNumber(), PAGES[kind](c, param, rng, pal)))
        footer(c, pal)
        c.showPage()

    answer_pages(c, answers, pal)
    c.showPage()
    total = c.getPageNumber() - 1
    if total % 2:
        notes_page(c, pal)
        total += 1
    c.save()
    print(f"✔ {out}  ({total} صفحة)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("level", choices=list(LEVELS) + ["all"])
    ap.add_argument("--pages", type=int, default=80, help="عدد صفحات التمارين")
    ap.add_argument("--author", default=AUTHOR)
    args = ap.parse_args()
    if args.pages < 20:
        sys.exit("KDP يحتاج 24 صفحة على الأقل. استعمل --pages 20 أو أكثر.")
    setup_font()
    for lv in (LEVELS if args.level == "all" else [args.level]):
        build(lv, args.pages, args.author)
