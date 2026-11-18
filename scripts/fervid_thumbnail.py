# -*- coding: utf-8 -*-
"""
팀퍼비드 블로그 썸네일 생성기 (800x800, 1:1)
사장님 PSD 「팀퍼비드 블로그 썸네일 1-1 비율 800-800.psd」 레이아웃을 그대로 재현한다.

  ┌──────────────── 800 ────────────────┐
  │ 차량 사진 (y 0~336, 전면 3/4 권장)    │
  │        [FERVID 로고 127,265]          │  ← 로고가 사진/흰 패널 경계에 걸침
  │──────────── 흰 패널 (y 336~) ─────────│
  │      차종명  HY엽서M 53px 검정          │  baseline 483
  │   작업명 1줄 HY헤드라인M 흰글씨+검정10px  │  baseline 604
  │   작업명 2줄                           │  baseline 739
  └──────────────────────────────────────┘

사용:
  python fervid_thumbnail.py <사진> --car "마세라티 콰트로 포르테" --line1 "중통" --line2 "커스텀 배기" --out <저장.jpg>
  옵션:
    --scale 1.0     사진 확대 배율 (1.0 = 가로 800에 맞춤, 1.3 = 30% 확대)
    --cx 0.5        사진 가로 초점 (0~1, 확대 시 어느 부분을 가운데 둘지)
    --cy 0.5        사진 세로 초점 (0~1, 이 지점이 사진 영역(0~336)의 가운데에 오도록 배치)
    --mosaic x0,y0,x1,y1   번호판 등 가릴 영역 (원본 사진 기준 0~1 비율 좌표, 여러 번 사용 가능)
    --preview       결과 저장 후 경로만 출력 (Claude가 Read로 확인)
  ※ --line2 생략 시 작업명 1줄만 크게 가운데 배치.
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(HERE)
LOGO = os.path.join(ROOT, "assets", "thumb_fervid_logo.png")
FONT_TITLE = r"C:\Windows\Fonts\HMKMRHD.TTF"          # HY헤드라인M (HeadlineR-HM)
FONT_CAR = (r"C:\Windows\Fonts\HMFMMUEX.TTC", 1)        # HY엽서M (ExpoM-HM)
FALLBACK = r"C:\Windows\Fonts\malgunbd.ttf"

W = H = 800
PANEL_Y = 336
LOGO_BOX = (127, 265)            # 로고 좌상단 (565x135)
CAR_BASE, CAR_SIZE, CAR_CX = 483, 53, 411
T_SIZE_Y, T_STRETCH = 113, 1.057  # 작업명 글자 높이 기준 px, 가로 늘림 비율(PSD 2.38/2.25)
T_BASE1, T_PITCH, T_CX = 604, 135, 400
T_STROKE = 10
T_MAXW = 760                     # 작업명 한 줄 최대 폭(넘으면 가로 압축)


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(FALLBACK, size)


def pixelate(img, box, block=None):
    x0, y0, x1, y1 = box
    r = img.crop(box)
    w, h = r.size
    b = block or max(8, min(w, h) // 6)
    r = r.resize((max(1, w // b), max(1, h // b)), Image.BILINEAR).resize((w, h), Image.NEAREST)
    img.paste(r, box)


def place_photo(canvas, src, scale, cx, cy):
    w = int(W * scale)
    h = int(src.height * w / src.width)
    ph = src.resize((w, h), Image.LANCZOS)
    x = int(W / 2 - cx * w)
    y = int(PANEL_Y / 2 - cy * h)
    x = min(0, max(W - w, x))                    # 가로 빈틈 방지
    y = min(0, max(PANEL_Y - h, y))              # 사진 영역(0~336) 빈틈 방지
    canvas.paste(ph, (x, y))


def draw_title_line(canvas, text, baseline, fnt):
    """흰 글씨 + 바깥 검정 테두리, 가로 1.057배 늘림 후 중앙 정렬."""
    asc, desc = fnt.getmetrics()
    tw = int(fnt.getlength(text)) + T_STROKE * 2 + 4
    th = asc + desc + T_STROKE * 2 + 4
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((T_STROKE + 2, T_STROKE + 2), text, font=fnt, fill="white",
           stroke_width=T_STROKE, stroke_fill="black")
    nw = int(tw * T_STRETCH)
    if nw > T_MAXW:
        nw = T_MAXW
    layer = layer.resize((nw, th), Image.LANCZOS)
    canvas.alpha_composite(layer, (int(T_CX - nw / 2), int(baseline - asc - T_STROKE - 2)))


def build(a):
    src = ImageOps.exif_transpose(Image.open(a.photo)).convert("RGB")
    for m in a.mosaic or []:
        f = [float(v) for v in m.split(",")]
        box = tuple(int(v * (src.width if i % 2 == 0 else src.height)) for i, v in enumerate(f))
        if box[2] > box[0] and box[3] > box[1]:      # 0,0,0,0 등 빈 영역은 건너뜀(번호판 없는 제품 사진)
            pixelate(src, box)

    canvas = Image.new("RGBA", (W, H), "white")
    place_photo(canvas, src, a.scale, a.cx, a.cy)
    ImageDraw.Draw(canvas).rectangle((0, PANEL_Y, W, H), fill="white")

    logo = Image.open(LOGO).convert("RGBA")
    canvas.alpha_composite(logo, LOGO_BOX)

    d = ImageDraw.Draw(canvas)
    fc = font(FONT_CAR[0], CAR_SIZE, FONT_CAR[1])
    cw = fc.getlength(a.car)
    if cw > 700:
        fc = font(FONT_CAR[0], int(CAR_SIZE * 700 / cw), FONT_CAR[1])
    d.text((CAR_CX, CAR_BASE), a.car, font=fc, fill="black", anchor="ms")

    ft = font(FONT_TITLE, T_SIZE_Y)
    if a.line2:
        draw_title_line(canvas, a.line1, T_BASE1, ft)
        draw_title_line(canvas, a.line2, T_BASE1 + T_PITCH, ft)
    else:
        draw_title_line(canvas, a.line1, T_BASE1 + T_PITCH // 2, ft)

    out = canvas.convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out.save(a.out, quality=95)
    print(a.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--car", required=True)
    ap.add_argument("--line1", required=True)
    ap.add_argument("--line2", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--cx", type=float, default=0.5)
    ap.add_argument("--cy", type=float, default=0.5)
    ap.add_argument("--mosaic", action="append")
    build(ap.parse_args())
