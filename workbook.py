#!/usr/bin/env python3
"""
مولّد كتب تمارين تعليمية (PDF) جاهزة لـ Amazon KDP - مقاس 8.5x11 إنش.

تثبيت (مرة واحدة):
    pip install reportlab arabic-reshaper python-bidi

تشغيل:
    python workbook.py grade1              # كتاب واحد (80 صفحة افتراضياً)
    python workbook.py grade2 --pages 100  # عدد صفحات مخصص
    python workbook.py all                 # كل المستويات
    python workbook.py all --author "اسمك"

الخط: يبحث السكريبت عن DejaVu/Noto تلقائياً. لاستعمال خط آخر ضع ملف font.ttf
بجانب السكريبت أو حدّد المتغير FONT_PATH.
"""
import argparse
import math
import os
import random
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ======================= الإعدادات (عدّلها هنا فقط) =======================
AUTHOR = "Mihwar Hadid"
YEAR = 2026
SEED = "kdp-v1"                      # غيّره لتحصل على تمارين مختلفة
PAGE_W, PAGE_H = 8.5 * 72, 11 * 72   # مقاس KDP
M = 0.75 * 72                        # الهوامش
TOP = PAGE_H - M - 85                # بداية منطقة التمارين
BOTTOM = M + 25
CONTENT_H = TOP - BOTTOM

# خطة كل مستوى: (نوع الصفحة، المعامل) تتكرر بالترتيب حتى يكتمل عدد الصفحات
LEVELS = {
    "prek": {
        "title": "تمارين الرياضيات",
        "sub": "مستوى التحضيري",
        "age": "من 4 إلى 5 سنوات",
        "plan": [("count", 10), ("trace", 10), ("compare", 10), ("add", 5),
                 ("count", 10), ("compare", 10), ("add", 10), ("trace", 10)],
    },
    "grade1": {
        "title": "تمارين الرياضيات",
        "sub": "السنة الأولى",
        "age": "من 6 إلى 7 سنوات",
        "plan": [("add", 10), ("sub", 10), ("count", 20), ("compare", 20),
                 ("add", 20), ("sub", 20), ("missing", 20), ("compare", 20)],
    },
    "grade2": {
        "title": "تمارين الرياضيات",
        "sub": "السنة الثانية",
        "age": "من 7 إلى 8 سنوات",
        "plan": [("add", 100), ("sub", 100), ("missing", 100), ("compare", 100),
                 ("mult", [2, 5, 10]), ("add", 100), ("sub", 100), ("mult", [2, 3, 4, 5, 10])],
    },
}

TYPES = {
    "count":   ("العدّ", "عدّ الأشكال ثم اكتب العدد في المربع"),
    "trace":   ("كتابة الأرقام", "تتبّع الأرقام ثم اكتبها بنفسك"),
    "compare": ("المقارنة", "اكتب في الدائرة: >  أو  <  أو  ="),
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


# ----------------------------- أدوات الرسم -----------------------------
def star(c, x, y, r):
    p = c.beginPath()
    for k in range(10):
        ang = math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.45
        px, py = x + rad * math.cos(ang), y + rad * math.sin(ang)
        p.moveTo(px, py) if k == 0 else p.lineTo(px, py)
    p.close()
    c.drawPath(p, stroke=1, fill=1)


def shape(c, kind, x, y, r):
    if kind == "circle":
        c.circle(x, y, r, stroke=1, fill=1)
    elif kind == "square":
        c.rect(x - r, y - r, 2 * r, 2 * r, stroke=1, fill=1)
    else:
        star(c, x, y, r * 1.25)


def header(c, kind):
    title, instr = TYPES[kind]
    c.setFillGray(0)
    c.setStrokeGray(0)
    c.setLineWidth(1)
    c.setFont(FONT, 24)
    c.drawRightString(PAGE_W - M, PAGE_H - M - 8, ar(title))
    c.setFont(FONT, 13)
    label = ar("الاسم:")
    c.drawRightString(PAGE_W - M, PAGE_H - M - 36, label)
    w = pdfmetrics.stringWidth(label, FONT, 13)
    c.line(PAGE_W - M - w - 8, PAGE_H - M - 38, PAGE_W / 2, PAGE_H - M - 38)
    c.setFont(FONT, 15)
    c.drawRightString(PAGE_W - M, PAGE_H - M - 64, ar(instr))
    c.line(M, PAGE_H - M - 74, PAGE_W - M, PAGE_H - M - 74)


def footer(c):
    c.setFont(FONT, 11)
    c.setFillGray(0.3)
    c.drawCentredString(PAGE_W / 2, M / 2, str(c.getPageNumber()))
    c.setFillGray(0)


def draw_tokens(c, x, y, tokens, size=30):
    """tokens: نص | "[]" مربع إجابة | "()" دائرة | "__" خط إجابة"""
    c.setFont(FONT, size)
    for t in tokens:
        if t == "[]":
            c.setLineWidth(1.5)
            c.rect(x, y - 10, 46, 46)
            x += 56
        elif t == "()":
            c.setLineWidth(1.5)
            c.circle(x + 23, y + 13, 23)
            x += 56
        elif t == "__":
            c.setLineWidth(1.5)
            c.line(x, y - 4, x + 80, y - 4)
            x += 90
        else:
            c.drawString(x, y, t)
            x += pdfmetrics.stringWidth(t, FONT, size)


def problem_grid(c, items):
    """items: قائمة من 10 عناصر، كل عنصر قائمة tokens"""
    cw = (PAGE_W - 2 * M) / 2
    rh = CONTENT_H / 5
    for i, tokens in enumerate(items):
        col, row = i % 2, i // 2
        x = M + cw * (1 - col) + 15
        y = TOP - rh * row - rh / 2 - 10
        draw_tokens(c, x, y, tokens)


# ----------------------------- أنواع الصفحات -----------------------------
# كل دالة ترسم الصفحة وترجع قائمة الأجوبة

def page_add(c, mx, rng):
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
    problem_grid(c, items)
    return ans


def page_sub(c, mx, rng):
    lo = 1 if mx <= 20 else 10
    items, ans = [], []
    for _ in range(10):
        a = rng.randint(lo, mx)
        b = rng.randint(0 if mx <= 20 else 1, a)
        items.append([f"{a} - {b} =", "__"])
        ans.append(str(a - b))
    problem_grid(c, items)
    return ans


def page_missing(c, mx, rng):
    items, ans = [], []
    for _ in range(10):
        total = rng.randint(2, mx)
        a = rng.randint(0, total)
        items.append([f"{a} + ", "[]", f" = {total}"])
        ans.append(str(total - a))
    problem_grid(c, items)
    return ans


def page_mult(c, tables, rng):
    items, ans = [], []
    for _ in range(10):
        a, b = rng.choice(tables), rng.randint(1, 10)
        if rng.random() < 0.5:
            a, b = b, a
        items.append([f"{a} × {b} =", "__"])
        ans.append(str(a * b))
    problem_grid(c, items)
    return ans


def page_compare(c, mx, rng):
    items, ans = [], []
    for _ in range(10):
        a = rng.randint(0, mx)
        b = a if rng.random() < 0.15 else rng.randint(0, mx)
        items.append([f"{a}   ", "()", f"   {b}"])
        ans.append(">" if a > b else "<" if a < b else "=")
    problem_grid(c, items)
    return ans


def page_count(c, mx, rng):
    cw, ch = (PAGE_W - 2 * M) / 2, CONTENT_H / 4
    kinds = ["circle", "square", "star"]
    ans = []
    c.setLineWidth(1)
    for i in range(8):
        col, row = i % 2, i // 2
        bx, by = M + cw * (1 - col), TOP - ch * (row + 1)
        c.setStrokeGray(0.6)
        c.roundRect(bx + 5, by + 5, cw - 10, ch - 10, 10)
        n = rng.randint(1, mx)
        kind = rng.choice(kinds)
        c.setStrokeGray(0)
        c.setFillGray(0.85)
        for k in range(n):
            shape(c, kind, bx + 28 + (k % 5) * 28, by + ch - 30 - (k // 5) * 28, 9)
        c.setFillGray(0)
        c.setLineWidth(1.5)
        c.rect(bx + cw - 62, by + ch / 2 - 20, 40, 40)
        ans.append(str(n))
    return ans


def page_trace(c, mx, rng):
    nums = sorted(rng.sample(range(1, mx + 1), 5))
    rh = CONTENT_H / 5
    for r, n in enumerate(nums):
        y = TOP - rh * r - rh / 2 - 25
        for k in range(6):
            x = M + 5 + k * 82
            c.setFont(FONT, 72)
            c.setFillGray(0 if k == 0 else 0.8)
            c.drawString(x, y, str(n))
        c.setFillGray(0)
        c.setDash(2, 4)
        c.setLineWidth(1)
        c.line(M, y - 8, PAGE_W - M, y - 8)
        c.setDash()
    return []


PAGES = {"count": page_count, "trace": page_trace, "compare": page_compare,
         "add": page_add, "sub": page_sub, "missing": page_missing, "mult": page_mult}


# ----------------------------- بناء الكتاب -----------------------------
def front_pages(c, cfg, author):
    c.setFont(FONT, 44)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 230, ar(cfg["title"]))
    c.setFont(FONT, 32)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 290, ar(cfg["sub"]))
    c.setFont(FONT, 20)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 335, ar(cfg["age"]))
    c.setFillGray(0.85)
    c.setStrokeGray(0)
    for k in range(5):
        star(c, PAGE_W / 2 - 100 + k * 50, PAGE_H - 410, 16)
    c.setFillGray(0)
    c.setFont(FONT, 16)
    c.drawCentredString(PAGE_W / 2, 150, ar(author) if any("\u0600" <= ch <= "\u06ff" for ch in author) else author)
    c.showPage()
    c.setFont(FONT, 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 10, f"© {YEAR} {author}")
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 12, ar("جميع الحقوق محفوظة"))
    c.showPage()


def answer_pages(c, answers):
    def new_page():
        c.showPage()
        c.setFont(FONT, 24)
        c.drawRightString(PAGE_W - M, PAGE_H - M - 8, ar("الأجوبة"))
        c.line(M, PAGE_H - M - 20, PAGE_W - M, PAGE_H - M - 20)
        return PAGE_H - M - 55

    y = new_page()
    for page_no, items in answers:
        if not items:
            continue
        if y < BOTTOM:
            footer(c)
            y = new_page()
        c.setFont(FONT, 13)
        c.drawRightString(PAGE_W - M, y, ar(f"صفحة {page_no}"))
        c.drawString(M, y, "   ".join(f"{i + 1}) {a}" for i, a in enumerate(items)))
        y -= 24
    footer(c)


def build(level, pages, author):
    cfg = LEVELS[level]
    out = f"workbook_{level}.pdf"
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"{cfg['title']} - {cfg['sub']}")
    c.setAuthor(author)
    front_pages(c, cfg, author)

    answers = []
    for i in range(pages):
        kind, param = cfg["plan"][i % len(cfg["plan"])]
        rng = random.Random(f"{SEED}-{level}-{i}")
        header(c, kind)
        answers.append((c.getPageNumber(), PAGES[kind](c, param, rng)))
        footer(c)
        c.showPage()

    answer_pages(c, answers)
    c.showPage()
    total = c.getPageNumber() - 1
    if total % 2:  # عدد زوجي من الصفحات
        c.setFont(FONT, 24)
        c.drawRightString(PAGE_W - M, PAGE_H - M - 8, ar("ملاحظات"))
        c.showPage()
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
