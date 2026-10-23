import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import motion as _m
from motion import *

_FONT_PATH = _m._FONT_PATH
SUB_DIRS = _m.SUB_DIRS

def grad_img(w, h, c1, c2, diag=True):
    gx = np.linspace(0, 1, w)[None, :]
    gy = np.linspace(0, 1, h)[:, None]
    k = (gx * 0.6 + gy * 0.4) if diag else (gy + gx * 0)
    arr = np.array(c1)[None, None, :] * (1 - k[:, :, None]) + np.array(c2)[None, None, :] * k[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

def grad_rr(ti, x0, y0, x1, y1, r, c1, c2, diag=True, outline=None, ow=3):
    w, h = int((x1 - x0) * S), int((y1 - y0) * S)
    if w < 2 or h < 2:
        return
    g = grad_img(w, h, c1, c2, diag)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(r * S), fill=255)
    ti.paste(g, (int(x0 * S), int(y0 * S)), m)
    if outline:
        ImageDraw.Draw(ti).rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, outline=outline, width=int(ow * S))

def gloss(ti, pts, alpha=46):
    ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255, alpha))
    ti.alpha_composite(ov)

def obj_tarjeta(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 120, 224, 680, 576, 34, (18, 34, 84), (70, 128, 214), outline=(150, 190, 255), ow=3)
    gloss(ti, [(120, 224), (420, 224), (300, 576), (120, 576)], 36)
    grad_rr(ti, 170, 330, 250, 392, 10, (255, 226, 120), (206, 140, 20), diag=True)
    for yy in (345, 361, 377):
        td.line([(170 * S, yy * S), (250 * S, yy * S)], fill=(150, 100, 10), width=int(1.5 * S))
    td.line([(210 * S, 330 * S), (210 * S, 392 * S)], fill=(150, 100, 10), width=int(1.5 * S))
    for k in range(3):
        r = 22 + 16 * k
        td.arc([(600 - r) * S, (320 - r) * S, (600 + r) * S, (320 + r) * S], -50, 50, fill=(235, 245, 255), width=int(4 * S))
    td.text((170 * S, 480 * S), (chr(8226) * 4 + '  ') * 3 + '4821', font=pfont(34, False), fill=(225, 235, 255), anchor='lm')

def obj_telefono(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 250, 110, 550, 690, 48, (30, 36, 54), (10, 14, 26), outline=(110, 124, 150), ow=4)
    grad_rr(ti, 264, 126, 536, 674, 36, (10, 30, 70), (14, 88, 100))
    td.rounded_rectangle([350 * S, 138 * S, 450 * S, 160 * S], radius=11 * S, fill=(6, 10, 20))
    td.text((400 * S, 260 * S), '3,40 ' + chr(8364), font=pfont(54, True), fill=WHITE, anchor='mm')
    td.text((400 * S, 312 * S), 'Importe', font=pfont(26, False), fill=(170, 200, 230), anchor='mm')
    pulse = 1 + 0.06 * math.sin(t * 5)
    r = 74 * pulse
    td.ellipse([(400 - r) * S, (460 - r) * S, (400 + r) * S, (460 + r) * S], fill=GREEN)
    td.line([(366 * S, 462 * S), (392 * S, 490 * S), (440 * S, 430 * S)], fill=WHITE, width=int(14 * S), joint='curve')
    td.text((400 * S, 590 * S), 'Aprobada', font=pfont(34, True), fill=(120, 240, 170), anchor='mm')
    gloss(ti, [(250, 110), (400, 110), (300, 690), (250, 690)], 22)

def obj_reloj(ti, t):
    td = ImageDraw.Draw(ti)
    td.ellipse([170 * S, 170 * S, 630 * S, 630 * S], fill=(14, 26, 56), outline=GOLD, width=int(14 * S))
    for k in range(12):
        a = k * math.pi / 6
        r0, r1 = (180, 205) if k % 3 else (170, 205)
        td.line([((400 + math.sin(a) * r0) * S, (400 - math.cos(a) * r0) * S), ((400 + math.sin(a) * r1) * S, (400 - math.cos(a) * r1) * S)], fill=WHITE, width=int((6 if k % 3 == 0 else 3) * S))
    am = t * 2.2
    ah = am / 12
    td.line([(400 * S, 400 * S), ((400 + math.sin(am) * 170) * S, (400 - math.cos(am) * 170) * S)], fill=GOLD, width=int(8 * S))
    td.line([(400 * S, 400 * S), ((400 + math.sin(ah) * 110) * S, (400 - math.cos(ah) * 110) * S)], fill=WHITE, width=int(12 * S))
    td.ellipse([386 * S, 386 * S, 414 * S, 414 * S], fill=GOLD)
    gloss(ti, [(190, 220), (400, 190), (330, 420), (200, 420)], 30)

def obj_candado(ti, t):
    td = ImageDraw.Draw(ti)
    td.arc([270 * S, 150 * S, 530 * S, 430 * S], 180, 360, fill=(190, 200, 215), width=int(34 * S))
    td.line([(270 * S, 290 * S), (270 * S, 400 * S)], fill=(190, 200, 215), width=int(34 * S))
    td.line([(530 * S, 290 * S), (530 * S, 400 * S)], fill=(190, 200, 215), width=int(34 * S))
    grad_rr(ti, 220, 380, 580, 640, 36, (255, 220, 100), (200, 130, 20), outline=(255, 240, 170), ow=3)
    td.ellipse([368 * S, 456 * S, 432 * S, 520 * S], fill=(90, 50, 5))
    td.polygon([(390 * S, 505 * S), (410 * S, 505 * S), (418 * S, 580 * S), (382 * S, 580 * S)], fill=(90, 50, 5))
    gloss(ti, [(220, 380), (400, 380), (330, 640), (220, 640)], 40)

def obj_lupa(ti, t):
    td = ImageDraw.Draw(ti)
    td.line([(500 * S, 500 * S), (640 * S, 640 * S)], fill=(60, 70, 96), width=int(54 * S))
    td.ellipse([190 * S, 170 * S, 510 * S, 490 * S], fill=(40, 110, 190), outline=GOLD, width=int(24 * S))
    gloss(ti, [(230, 230), (380, 200), (260, 360)], 70)

def obj_banco(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 150, 560, 650, 610, 8, (230, 236, 250), (150, 160, 190), diag=False)
    grad_rr(ti, 180, 520, 620, 560, 6, (236, 240, 252), (170, 178, 205), diag=False)
    for k in range(4):
        x = 215 + k * 112
        grad_rr(ti, x, 330, x + 58, 520, 6, (250, 252, 255), (160, 170, 200), diag=False)
    td.polygon([(140 * S, 330 * S), (400 * S, 190 * S), (660 * S, 330 * S)], fill=(214, 220, 240))
    td.polygon([(190 * S, 320 * S), (400 * S, 215 * S), (610 * S, 320 * S)], fill=(236, 240, 252))
    td.ellipse([376 * S, 262 * S, 424 * S, 310 * S], fill=GOLD)

def obj_persona(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 220, 430, 580, 700, 120, (120, 150, 210), (60, 80, 150), diag=False)
    td.ellipse([310 * S, 180 * S, 490 * S, 360 * S], fill=(150, 176, 226))
    gloss(ti, [(320, 200), (400, 190), (340, 330)], 40)

def obj_bombilla(ti, t):
    td = ImageDraw.Draw(ti)
    glow = 0.5 + 0.5 * math.sin(t * 4)
    g = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([140 * S, 100 * S, 660 * S, 620 * S], fill=(255, 220, 90, int(40 + 50 * glow)))
    ti.alpha_composite(g)
    td.ellipse([240 * S, 170 * S, 560 * S, 490 * S], fill=(255, 226, 110), outline=(255, 244, 190), width=int(6 * S))
    grad_rr(ti, 320, 480, 480, 560, 14, (190, 196, 210), (110, 116, 136), diag=False)
    grad_rr(ti, 336, 566, 464, 610, 14, (160, 166, 186), (96, 100, 120), diag=False)
    gloss(ti, [(270, 220), (360, 190), (300, 340)], 80)

def obj_cruz(ti, t):
    td = ImageDraw.Draw(ti)
    for k in range(16):
        a = k * math.pi / 8 + t * 0.3
        r0, r1 = 150, 340 + 40 * math.sin(t * 2 + k)
        td.line([((400 + math.cos(a) * r0) * S, (400 + math.sin(a) * r0) * S), ((400 + math.cos(a) * r1) * S, (400 + math.sin(a) * r1) * S)], fill=(255, 226, 150), width=int(5 * S))
    grad_rr(ti, 368, 200, 432, 620, 14, (255, 236, 160), (222, 160, 40), diag=False)
    grad_rr(ti, 250, 300, 550, 364, 14, (255, 236, 160), (222, 160, 40), diag=False)

def obj_billete(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 130, 250, 670, 550, 22, (40, 170, 100), (14, 100, 66), outline=(170, 255, 200), ow=3)
    td.rounded_rectangle([160 * S, 280 * S, 640 * S, 520 * S], radius=14 * S, outline=(190, 255, 215), width=int(3 * S))
    td.ellipse([320 * S, 290 * S, 480 * S, 510 * S], fill=(20, 120, 78), outline=(190, 255, 215), width=int(4 * S))
    td.text((400 * S, 400 * S), '$', font=pfont(110, True), fill=(220, 255, 232), anchor='mm')
    gloss(ti, [(130, 250), (360, 250), (260, 550), (130, 550)], 34)

def obj_moneda(ti, t):
    sq = abs(math.cos(t * 1.4)) * 0.35 + 0.65
    td = ImageDraw.Draw(ti)
    rx, ry = 190 * sq, 190
    td.ellipse([(400 - rx) * S, (400 - ry) * S, (400 + rx) * S, (400 + ry) * S], fill=GOLD_D)
    td.ellipse([(400 - rx * 0.88) * S, (400 - ry * 0.88) * S, (400 + rx * 0.88) * S, (400 + ry * 0.88) * S], fill=GOLD)
    td.ellipse([(400 - rx * 0.66) * S, (400 - ry * 0.66) * S, (400 + rx * 0.66) * S, (400 + ry * 0.66) * S], outline=GOLD_L, width=int(6 * S))
    if sq > 0.55:
        td.text((400 * S, 404 * S), '$', font=pfont(190 * sq, True), fill=GOLD_D, anchor='mm')

_TILE = {}
ESTATICOS = ('tarjeta', 'lupa', 'banco', 'persona', 'candado', 'billete')
OBJETOS = {'tarjeta': obj_tarjeta, 'telefono': obj_telefono, 'reloj': obj_reloj, 'candado': obj_candado, 'lupa': obj_lupa,
           'banco': obj_banco, 'persona': obj_persona, 'bombilla': obj_bombilla, 'cruz': obj_cruz, 'billete': obj_billete,
           'moneda': obj_moneda}

def n_objeto(d, t, sc):
    p = sc['p']
    lay = d._image
    cx, cy = float(p.get('x', 360)), float(p.get('y', 480))
    kind = p.get('objeto', 'tarjeta')
    t0 = cue(sc, p.get('cue'), 0.05)
    a = prog(t, t0, t0 + 0.5)
    if p.get('campo', True):
        for k in range(3):
            ph = (t * 0.7 + k / 3.0) % 1.0
            r = 200 + 260 * ph
            circle(d, cx, cy, r, outline=mix(GOLD, BG2, ph), width=5 * (1 - ph) + 1)
    if a > 0:
        if kind in ESTATICOS and kind in _TILE:
            ti = _TILE[kind]
        else:
            ti = Image.new('RGBA', (800 * S, 800 * S), (0, 0, 0, 0))
            OBJETOS[kind](ti, t)
            bb = ti.getchannel('A').getbbox()
            if bb:
                ti = ti.crop(bb)
            if kind in ESTATICOS:
                _TILE[kind] = ti
        ang = float(p.get('angulo', 0)) + math.sin(t * 1.6) * 3.0
        k = float(p.get('escala', 0.8)) * (0.55 + 0.45 * e_back(a))
        sz = (max(2, int(ti.size[0] * k)), max(2, int(ti.size[1] * k)))
        ti = ti.resize(sz, Image.BILINEAR)
        if abs(ang) > 0.05:
            ti = ti.rotate(ang, resample=Image.BILINEAR, expand=True)
        bob = math.sin(t * 2.2) * 8
        lay.paste(ti, (int(cx * S - ti.size[0] / 2), int((cy + bob) * S - ti.size[1] / 2)), ti)
    for i, lb in enumerate(p.get('etiquetas') or []):
        tl = cue(sc, lb.get('cue'), evenly(sc, i, len(p['etiquetas']), 0.2, 0.7))
        aa = prog(t, tl, tl + 0.35)
        if aa <= 0:
            continue
        lx, ly = cx + float(lb.get('dx', 200)), cy + float(lb.get('dy', -200))
        tx = lb['texto']
        wpx = d.textlength(tx, font=pfont(30, True)) / S + 36
        d.line([P(cx + (lx - cx) * 0.25, cy + (ly - cy) * 0.25), P(lx, ly)], fill=GOLD, width=int(3 * S))
        circle(d, cx + (lx - cx) * 0.25, cy + (ly - cy) * 0.25, 6, fill=GOLD)
        k = e_back(aa)
        rrect(d, lx - wpx / 2 * k, ly - 28 * k, lx + wpx / 2 * k, ly + 28 * k, 12, fill=(14, 28, 60), outline=GOLD, width=3)
        if k > 0.7:
            d.text((lx * S, ly * S), tx, font=pfont(30, True), fill=WHITE, anchor='mm')
    ct = p.get('contador')
    if ct:
        tc = cue(sc, ct.get('cue'), 0.3 * sc['dur'])
        v = lerp(float(ct.get('desde', 0)), float(ct['valor']), e_out(prog(t, tc, tc + 1.4)))
        s2 = fmt(v, int(ct.get('decimales', 0)), ct.get('prefijo', ''), ct.get('sufijo', ''))
        txt(d, 360, float(ct.get('y', 800)), s2, fit(d, s2, 120, 620), col(ct.get('color', 'oro')), stroke=7)
    ru = p.get('cota')
    if ru:
        tr = cue(sc, ru.get('cue'), 0.4 * sc['dur'])
        ar = prog(t, tr, tr + 0.6)
        if ar > 0:
            y = float(ru.get('y', 790))
            x0, x1 = 120, 120 + (600 - 120) * e_out(ar)
            d.line([P(120, y), P(x1, y)], fill=WHITE, width=int(4 * S))
            for xx in (120, x1):
                d.line([P(xx, y - 16), P(xx, y + 16)], fill=WHITE, width=int(4 * S))
            if ar > 0.8:
                txt(d, 360, y + 40, ru['texto'], 36, GOLD, stroke=4)

def e_objeto(sc):
    p = sc['p']
    ev = [(cue(sc, p.get('cue'), 0.05), 'pop')]
    n = len(p.get('etiquetas') or [])
    for i, lb in enumerate(p.get('etiquetas') or []):
        ev.append((cue(sc, lb.get('cue'), evenly(sc, i, n, 0.2, 0.7)), 'pop'))
    if p.get('contador'):
        ev.append((cue(sc, p['contador'].get('cue'), 0.3 * sc['dur']) + 1.4, 'ching'))
    return ev

def phrases_de(words):
    out, i = [], 0
    while i < len(words):
        n, ln = 1, len(words[i][0])
        while n < 6 and i + n < len(words) and not re.search('[.?!:;,]$', words[i + n - 1][0]):
            ln2 = ln + 1 + len(words[i + n][0])
            if ln2 > 36:
                break
            ln = ln2
            n += 1
        out.append((i, n))
        i += n
    return out

_PF = {}

def pfont(sz, bold):
    k = (int(round(sz * S)), bold)
    if k not in _PF:
        import glob
        nm = 'Poppins-Bold.ttf' if bold else 'Poppins-Medium.ttf'
        path = None
        for dd in SUB_DIRS + ['/usr/share/fonts/truetype/google-fonts']:
            for q in glob.glob(os.path.join(dd, '**', nm), recursive=True):
                path = q
                break
            if path:
                break
        path = path or _FONT_PATH
        _PF[k] = ImageFont.truetype(path, k[0]) if path else ImageFont.load_default()
    return _PF[k]

BLUE_SEL = (64, 132, 255)

def draw_subs2(d, t, words, frases):
    idx = None
    for i, (w, a, b) in enumerate(words):
        if a <= t:
            idx = i
        else:
            break
    if idx is None or t > words[idx][2] + 0.45:
        return
    for (gs, gn) in frases:
        if gs <= idx < gs + gn:
            g0, n = gs, gn
            break
    toks = [re.sub('[' + chr(34) + ']', '', w[0]) for w in words[g0:g0 + n]]
    fs = 50
    sp = 16 * S
    maxw = CW * 0.86
    while True:
        fb, fm = pfont(fs, True), pfont(fs, False)
        ws = [d.textlength(x, font=fb) for x in toks]
        if sum(ws) + sp * (len(ws) - 1) <= maxw or fs < 36:
            break
        fs -= 2
    lines, cur, cw = [], [], 0.0
    tot = sum(ws) + sp * (len(ws) - 1)
    for j, x in enumerate(toks):
        if cur and (cw + sp + ws[j] > tot * 0.58 + 40 * S) and len(lines) == 0:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append(j)
        cw += (sp if len(cur) > 1 else 0) + ws[j]
    lines.append(cur)
    lh = fs * 1.34
    y = 0.178 * H
    for ln in lines:
        lw = sum(ws[j] for j in ln) + sp * (len(ln) - 1)
        x = (CW - lw) / 2
        for j in ln:
            gi = g0 + j
            active = gi == idx
            spoken = gi <= idx
            f = fb if spoken else fm
            col_t = WHITE if spoken else (128, 134, 150)
            if active:
                pad = 9 * S
                x0, x1 = x - pad, x + ws[j] + pad
                y0, y1 = (y - fs * 0.62) * S - 2 * S, (y + fs * 0.62) * S
                d.rectangle([x0, y0, x1, y1], fill=(24, 48, 110), outline=BLUE_SEL, width=int(2.2 * S))
                for (hx, hy) in ((x0, y0), (x1, y1)):
                    d.ellipse([hx - 7 * S, hy - 7 * S, hx + 7 * S, hy + 7 * S], fill=(16, 28, 64), outline=BLUE_SEL, width=int(2.5 * S))
            d.text((x + 2 * S, y * S + 3 * S), toks[j], font=f, fill=(0, 0, 0), anchor='lm')
            d.text((x, y * S), toks[j], font=f, fill=col_t, anchor='lm')
            x += ws[j] + sp
        y += lh

_NOISE = np.random.RandomState(3).randint(-5, 6, size=(6, H, W, 1)).astype(np.int16)
_gy, _gx = np.mgrid[0:H, 0:W]
_r2 = np.sqrt(((_gx - W / 2) / (W * 0.5)) ** 2 + ((_gy - H / 2) / (H * 0.5)) ** 2)
_vig = np.clip(1.0 - 0.55 * np.clip(_r2 - 0.55, 0, 1) ** 1.5, 0.35, 1.0)[:, :, None]
BG_S1 = Image.fromarray(np.clip(np.asarray(BG.resize((W, H), Image.LANCZOS)).astype(np.float32) * _vig, 0, 255).astype(np.uint8))

def frame(t, scenes, words, total, grupos=None, linea=''):
    from PIL import ImageChops, ImageFilter
    base = BG_S1.copy()
    d = ImageDraw.Draw(base)
    for (px, py, sp, sz) in PART:
        y = (py - t * sp * 0.05) % 1.0
        x = px + math.sin(t * sp + px * 9) * 0.01
        d.ellipse([x * W - sz, y * H - sz, x * W + sz, y * H + sz], fill=(34, 112, 124))
    sc = scenes[-1]
    for s in scenes:
        if s['start'] <= t < s['start'] + s['dur']:
            sc = s
            break
    lt = t - sc['start']
    layer = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    PLANTILLAS[sc['plantilla']][0](dl, lt, sc)
    intro = e_out(prog(lt, 0.0, 0.25))
    scale = 0.94 * (1.0 + 0.05 * prog(lt, 0.0, sc['dur'])) * (1.07 - 0.07 * intro)
    sz = (max(2, int(W * scale)), max(2, int(H * scale)))
    lay = layer.resize(sz, Image.LANCZOS)
    full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    full.paste(lay, (int(W / 2 - 360 * scale), int(790 - 520 * scale)))
    al = full.getchannel('A').point(lambda v: int(v * (0.25 + 0.75 * intro)))
    full.putalpha(al)
    sh = al.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
    sh = sh.point(lambda v: int(v * 0.55))
    base.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 12), sh)
    base.paste(full, (0, 0), full)
    small = full.convert('RGB').resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    bloom = small.resize((W, H), Image.BILINEAR).point(lambda v: int(v * 0.6))
    base = ImageChops.screen(base, bloom)
    th = int(0.30 * CH)
    tile = Image.new('RGBA', (CW, th), (0, 0, 0, 0))
    draw_subs2(ImageDraw.Draw(tile), t, words, grupos or phrases_de(words))
    tile = tile.resize((W, th // S), Image.LANCZOS)
    base.paste(tile, (0, 0), tile)
    arr = np.asarray(base).astype(np.int16) + _NOISE[int(t * 30) % 6]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

PLANTILLAS['objeto'] = (n_objeto, e_objeto)
