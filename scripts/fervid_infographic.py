# -*- coding: utf-8 -*-
"""
팀퍼비드 블로그 도식(인포그래픽) 생성기 — 썸네일과 같은 톤(HY헤드라인M 제목 + FERVID 레드)

사용:
  python fervid_infographic.py <spec.json> <out.png>

spec.json 공통:
  {"type": "flow" | "compare" | "steps",
   "title": "자동차 배기라인 구조",
   "subtitle": "엔진에서 머플러팁까지, 구간별로 할 수 있는 튜닝",   (선택)
   "footer": "팀퍼비드 · 부산 사상구"}                              (선택, 기본값 동일)

type별 필드:
  flow    — 가로 흐름도 (2~7칸)
    "items": [{"name":"엔진","sub":"매니폴드·터보","tag":null,"dark":true}, {"name":"촉매","sub":"다운파이프","tag":"다운파이프 교체"}, ...]
    "notes": [["배기가스 흐름","엔진 → 촉매 → ..."], ...]   (선택, 0~4줄)
  compare — 비교표 (2~3열, 행 2~8개)
    "columns": ["다운스프링","코일오버"],
    "rows": [["차고 조절","불가 (고정)","가능 (나사식)"], ...]     ← 첫 칸 = 항목명
    "highlight": 1   (선택, 강조할 열 번호 0부터)
    "notes": [...]   (선택)
  steps   — 번호 단계/체크리스트 (2~8개, 세로)
    "items": [{"title":"튜닝승인 신청","desc":"교통안전공단에 ..."}, ...]
    "numbered": true  (false면 체크 표시)

※ 로고는 넣지 않는다 — 블로그 사진과 같은 방식으로 logo_watermark.py 단계에서 _upload에 합성된다.
※ 글자는 칸 폭에 맞춰 자동 축소된다. 그래도 넘치면 문구를 줄일 것(생성 후 반드시 Read로 확인).
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

W = 1600
BG, INK, GREY, RED, PIPE, DARK = "#f6f6f4", "#1d1d1f", "#6b6b6b", "#c8102e", "#9aa0a6", "#2b2b2e"
F_HEAD = r"C:\Windows\Fonts\HMKMRHD.TTF"
F_B = r"C:\Windows\Fonts\malgunbd.ttf"
F_R = r"C:\Windows\Fonts\malgun.ttf"


def font(p, s): return ImageFont.truetype(p, s)


def fit(d, text, path, size, maxw, min_size=16):
    """maxw 안에 들어가도록 폰트 크기를 줄여 반환."""
    while size > min_size and d.textlength(text, font=font(path, size)) > maxw:
        size -= 1
    return font(path, size)


def wrap(d, text, f, maxw):
    """한글 기준 글자 단위 줄바꿈(공백 우선)."""
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            while d.textlength(word, font=f) > maxw:          # 긴 단어 강제 분할
                k = len(word)
                while k > 1 and d.textlength(word[:k], font=f) > maxw: k -= 1
                lines.append(word[:k]); word = word[k:]
            cur = word
    if cur: lines.append(cur)
    return lines


def header(d, spec, y=70):
    d.text((W/2, y), spec["title"], font=fit(d, spec["title"], F_HEAD, 64, W-500), fill=INK, anchor="mm")
    if spec.get("subtitle"):
        d.text((W/2, y+65), spec["subtitle"], font=fit(d, spec["subtitle"], F_R, 30, W-200), fill=GREY, anchor="mm")
    return y + 140


def notes_block(d, notes, y):
    fk, fv = font(F_B, 25), font(F_R, 26)
    kw = max([d.textlength(k, font=fk) for k, _ in notes] + [0]) + 40
    for k, v in notes:
        d.ellipse((90, y-9, 108, y+9), fill=RED)
        d.text((125, y), k, font=fk, fill=INK, anchor="lm")
        vf = fit(d, v, F_R, 26, W - 125 - kw - 80)
        d.text((125 + kw, y), v, font=vf, fill=GREY, anchor="lm")
        y += 66
    return y


def footer(d, spec, H):
    d.text((W-60, H-40), spec.get("footer", "팀퍼비드 · 부산 사상구"), font=font(F_R, 26), fill=GREY, anchor="rm")


def draw_flow(spec):
    items, notes = spec["items"], spec.get("notes", [])
    H = 690 + 66 * len(notes)
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    top = header(d, spec)
    n = len(items); bw = min(230, int((W - 120 - (n-1)*40) / n)); bh = 150
    gap = (W - 120 - n*bw) / max(1, n-1)
    y0 = top + 50
    xs = [60 + i*(bw+gap) for i in range(n)]
    d.rounded_rectangle((xs[0]+bw/2, y0+bh/2-12, xs[-1]+bw/2, y0+bh/2+12), radius=12, fill=PIPE)
    for i, it in enumerate(items):
        x = xs[i]; dark = it.get("dark", False)
        d.rounded_rectangle((x, y0, x+bw, y0+bh), radius=22, fill=DARK if dark else "white", outline=INK if dark else RED, width=5)
        d.text((x+bw/2, y0+58), it["name"], font=fit(d, it["name"], F_B, 34, bw-24), fill="white" if dark else INK, anchor="mm")
        if it.get("sub"):
            d.text((x+bw/2, y0+105), it["sub"], font=fit(d, it["sub"], F_R, 26, bw-20), fill="#cfcfcf" if dark else GREY, anchor="mm")
        if i < n-1:
            ax = x + bw + gap/2
            d.polygon([(ax-14, y0+bh/2-26), (ax+16, y0+bh/2), (ax-14, y0+bh/2+26)], fill=RED)
        if it.get("tag"):
            tf = fit(d, it["tag"], F_B, 25, bw + gap - 30)
            tw = d.textlength(it["tag"], font=tf) + 36; tx = x + bw/2 - tw/2
            d.line((x+bw/2, y0+bh+8, x+bw/2, y0+bh+70), fill=RED, width=4)
            d.rounded_rectangle((tx, y0+bh+70, tx+tw, y0+bh+122), radius=26, fill=RED)
            d.text((x+bw/2, y0+bh+96), it["tag"], font=tf, fill="white", anchor="mm")
    notes_block(d, notes, y0 + bh + 200)
    footer(d, spec, H)
    return im


def draw_compare(spec):
    cols, rows, notes = spec["columns"], spec["rows"], spec.get("notes", [])
    hl = spec.get("highlight")
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lw = 300; cw = (W - 120 - lw) / len(cols)
    fcell = font(F_R, 27)
    heights = []
    for r in rows:
        nl = max(len(wrap(tmp, c, fcell, cw - 48)) for c in r[1:])
        heights.append(max(90, 40 + nl * 38))
    H = 260 + 100 + sum(heights) + 40 + 66 * len(notes) + 90
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    y = header(d, spec) + 40
    x0 = 60
    # 헤더 행
    d.rounded_rectangle((x0, y, W-60, y+100), radius=18, fill=DARK)
    for j, c in enumerate(cols):
        cx = x0 + lw + cw*j + cw/2
        if hl == j:
            d.rounded_rectangle((x0+lw+cw*j+8, y+8, x0+lw+cw*(j+1)-8, y+92), radius=14, fill=RED)
        d.text((cx, y+50), c, font=fit(d, c, F_B, 36, cw-30), fill="white", anchor="mm")
    y += 110
    for i, r in enumerate(rows):
        h = heights[i]
        d.rounded_rectangle((x0, y, W-60, y+h-10), radius=14, fill="white", outline="#e3e3e3", width=2)
        d.text((x0+30, y+(h-10)/2), r[0], font=fit(d, r[0], F_B, 28, lw-50), fill=INK, anchor="lm")
        for j, c in enumerate(r[1:]):
            lines = wrap(d, c, fcell, cw - 48)
            ly = y + (h-10)/2 - (len(lines)-1)*19
            for ln in lines:
                d.text((x0+lw+cw*j+cw/2, ly), ln, font=fcell, fill=RED if hl == j else INK, anchor="mm"); ly += 38
        y += h
    notes_block(d, notes, y + 40)
    footer(d, spec, H)
    return im


def draw_steps(spec):
    items = spec["items"]; numbered = spec.get("numbered", True); notes = spec.get("notes", [])
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    fdesc = font(F_R, 27); maxw = W - 120 - 170 - 40
    hs = [max(120, 70 + 38*len(wrap(tmp, it.get("desc", ""), fdesc, maxw))) for it in items]
    H = 260 + sum(hs) + 20*len(items) + 66*len(notes) + 110
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    y = header(d, spec) + 30
    for i, it in enumerate(items):
        h = hs[i]
        d.rounded_rectangle((60, y, W-60, y+h), radius=20, fill="white", outline="#e3e3e3", width=2)
        cx, cy = 130, y + h/2
        d.ellipse((cx-42, cy-42, cx+42, cy+42), fill=RED)
        if numbered:
            d.text((cx, cy), str(i+1), font=font(F_HEAD, 46), fill="white", anchor="mm")
        else:
            d.line([(cx-18, cy), (cx-4, cy+15), (cx+20, cy-15)], fill="white", width=9, joint="curve")
        tx = 210
        d.text((tx, y+48), it["title"], font=fit(d, it["title"], F_B, 34, maxw), fill=INK, anchor="lm")
        ly = y + 92
        for ln in wrap(d, it.get("desc", ""), fdesc, maxw):
            d.text((tx, ly), ln, font=fdesc, fill=GREY, anchor="lm"); ly += 38
        if numbered and i < len(items)-1:
            d.line((cx, y+h+2, cx, y+h+18), fill=RED, width=5)
        y += h + 20
    notes_block(d, notes, y + 30)
    footer(d, spec, H)
    return im


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    im = {"flow": draw_flow, "compare": draw_compare, "steps": draw_steps}[spec["type"]](spec)
    im.save(sys.argv[2])
    print(sys.argv[2], im.size)
