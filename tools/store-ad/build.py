import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
RED = (227, 27, 35, 255)
FD = "/usr/share/fonts/opentype/inter/"
BLACK = FD + "InterDisplay-Black.otf"
XB = FD + "InterDisplay-ExtraBold.otf"
SB = FD + "Inter-SemiBold.otf"
os.makedirs("ov", exist_ok=True)

def font(p, s): return ImageFont.truetype(p, s)

def tracked(draw, xy, text, f, fill, track=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + track
    return x

def tw(draw, text, f, track=0):
    return sum(draw.textlength(c, font=f) for c in text) + track * (len(text) - 1)

def title(name, kicker, lines, sub=None, size=150, bottom=1440):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fb = font(BLACK, size); fk = font(XB, 40); fs = font(SB, 50)
    lh = int(size * 0.98)
    block_h = (70 if kicker else 0) + lh * len(lines) + (80 if sub else 0)
    y = bottom - block_h
    x = 84
    # shadow layer
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    yy = y
    if kicker:
        kw = tw(d, kicker, fk, 6) + 44
        d.rounded_rectangle((x, yy, x + kw, yy + 58), 10, fill=RED)
        tracked(d, (x + 22, yy + 6), kicker, fk, (255, 255, 255, 255), 6)
        yy += 80
    for ln in lines:
        tracked(sd, (x + 4, yy + 6), ln, fb, (0, 0, 0, 170), -4)
        tracked(d, (x, yy), ln, fb, (255, 255, 255, 255), -4)
        yy += lh
    if sub:
        yy += 18
        d.rectangle((x, yy + 8, x + 8, yy + 52), fill=RED)
        tracked(sd, (x + 30 + 2, yy + 3), sub, fs, (0, 0, 0, 200), 0)
        tracked(d, (x + 30, yy), sub, fs, (255, 255, 255, 255), 0)
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    out = Image.alpha_composite(sh, img)
    out.save(f"ov/{name}.png")

def grad():
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for yy in range(H):
        a = 0
        if yy > 800: a = int(min(1, (yy - 800) / 700) ** 1.4 * 175)
        if yy < 260: a = max(a, int((1 - yy / 260) * 90))
        for xx in range(W):
            px[xx, yy] = (0, 0, 0, a)
    img.save("ov/grad.png")

grad()
title("t1", "COLLEGE PARK WIRELESS", ["EVERYTHING", "YOUR PHONE", "NEEDS."], size=146)
title("t2", "SHOP THE LATEST", ["PHONES"], sub="iPhone · Samsung & more", size=190)
title("t3", "FOR EVERY MODEL", ["CASES"], size=190)
title("t4", "POWER UP", ["CHARGERS", "CABLES", "POWER BANKS"], size=124)
title("t5", "TEMPERED GLASS", ["SCREEN", "PROTECTORS"], size=132)
title("t6", "WORK & PLAY", ["LAPTOP & PC", "ACCESSORIES"], size=130)
title("t7", "PHONE · TABLET · LAPTOP", ["FAST", "REPAIRS"], sub="Most done in under an hour", size=180)
title("t8", None, ["ALL IN", "ONE STORE."], size=165)

# End card layers
def endcard():
    f1 = font(BLACK, 122); f2 = font(SB, 46); f3 = font(XB, 44); fk = font(XB, 36)
    a = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(a)
    def center(d, y, t, f, fill, tr=0):
        tracked(d, ((W - tw(d, t, f, tr)) / 2, y), t, f, fill, tr)
    # logo mark
    center(d, 690, "SINCE YOUR PHONE NEEDS IT", font(XB, 34), (227, 27, 35, 255), 8) if False else None
    center(d, 790, "COLLEGE PARK", f1, (255, 255, 255, 255), -4)
    center(d, 920, "WIRELESS", f1, (255, 255, 255, 255), -2)
    a.save("ov/e1.png")
    b = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(b)
    d.rectangle((W/2 - 60, 1090, W/2 + 60, 1098), fill=RED)
    center(d, 1130, "777 Bay St · College Park, Toronto", f2, (255, 255, 255, 255))
    center(d, 1200, "Mon–Fri 10–7  ·  Sat–Sun 12–6", f2, (220, 220, 220, 255))
    b.save("ov/e2.png")
    c = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(c)
    t = "VISIT US TODAY"
    kw = tw(d, t, fk, 6) + 60
    d.rounded_rectangle(((W - kw) / 2, 1300, (W + kw) / 2, 1372), 36, fill=RED)
    center(d, 1314, t, fk, (255, 255, 255, 255), 6)
    center(d, 1420, "@collegeparkwirelessrepair", f3, (255, 255, 255, 255))
    center(d, 1480, "collegeparkwireless.ca", f2, (220, 220, 220, 255))
    c.save("ov/e3.png")
endcard()

# Edit decision list: (timeline_start, duration, src_in, zoom_dir, flash)
clips = [
    (0.0, 2.0, 10.4, 1, True),
    (2.0, 1.0, 0.2, 1, True),
    (3.0, 1.0, 4.0, -1, False),
    (4.0, 1.0, 2.1, 1, False),
    (5.0, 1.0, 40.0, 1, True),
    (6.0, 1.0, 19.0, -1, False),
    (7.0, 1.0, 18.0, 1, True),
    (8.0, 1.0, 29.0, -1, False),
    (9.0, 1.0, 31.0, 1, False),
    (10.0, 1.0, 26.7, 1, True),
    (11.0, 1.0, 33.4, -1, False),
    (12.0, 1.0, 52.5, 1, True),
    (13.0, 1.0, 48.0, -1, False),
    (14.0, 2.5, 38.0, 1, True),
    (16.5, 1.5, 21.0, -1, False),
    (18.0, 2.0, 14.0, 1, False),
]
END_T, END_D, END_SRC = 20.0, 5.0, 40.0
titles = [("t1", 0.0, 2.0), ("t2", 2.0, 3.0), ("t3", 5.0, 2.0), ("t4", 7.0, 3.0),
          ("t5", 10.0, 2.0), ("t6", 12.0, 2.0), ("t7", 14.0, 4.0), ("t8", 18.0, 2.0)]

FPS = "30000/1001"
args = ["ffmpeg", "-v", "error", "-y"]
fc = []
idx = 0
vlabels = []
for i, (t0, d, s, z, fl) in enumerate(clips):
    args += ["-ss", str(s), "-t", str(d + 0.1), "-i", "stab.mp4"]
    zexpr = f"(1+0.07*t/{d})" if z > 0 else f"(1.07-0.07*t/{d})"
    f = (f"[{idx}:v]trim=0:{d},setpts=PTS-STARTPTS,fps={FPS},"
         f"scale=w='trunc(1080*{zexpr}/2)*2':h=-2:eval=frame:flags=bicubic,crop=1080:1920,setsar=1")
    if fl: f += ",fade=in:st=0:d=0.13:color=white"
    f += f"[v{i}]"
    fc.append(f); vlabels.append(f"[v{i}]"); idx += 1
# end card bg
args += ["-ss", str(END_SRC), "-t", str(END_D + 0.1), "-i", "stab.mp4"]
fc.append(f"[{idx}:v]trim=0:{END_D},setpts=PTS-STARTPTS,fps={FPS},"
          f"scale=w='trunc(1080*(1.05+0.06*t/{END_D})/2)*2':h=-2:eval=frame,crop=1080:1920,setsar=1,"
          f"gblur=sigma=28,eq=brightness=-0.22:saturation=0.8,fade=in:st=0:d=0.25:color=white[vend]")
vlabels.append("[vend]"); idx += 1
fc.append("".join(vlabels) + f"concat=n={len(vlabels)}:v=1:a=0[base]")
TOTAL = END_T + END_D
# gradient for main section
args += ["-loop", "1", "-t", str(TOTAL), "-i", "ov/grad.png"]
fc.append(f"[{idx}:v]format=rgba,fade=out:st={END_T-0.05}:d=0.05:alpha=1[g]")
fc.append("[base][g]overlay=0:0:format=auto[b0]"); idx += 1
cur = "b0"
def add_ov(png, t0, d, slide=70, fin=0.22, fout=0.15, k=[0]):
    global idx, cur
    args.extend(["-loop", "1", "-t", str(d), "-i", png])
    lab = f"o{idx}"
    fo = f",fade=out:st={d-fout}:d={fout}:alpha=1" if fout else ""
    fc.append(f"[{idx}:v]format=rgba,fade=in:st=0:d={fin}:alpha=1{fo},setpts=PTS-STARTPTS+{t0}/TB[{lab}]")
    nxt = f"b{idx}"
    fc.append(f"[{cur}][{lab}]overlay=x=0:y='{slide}*pow(max(0,1-(t-{t0})/0.3),3)':eof_action=pass:enable='between(t,{t0},{t0+d})'[{nxt}]")
    cur = nxt; idx += 1
for name, t0, d in titles:
    add_ov(f"ov/{name}.png", t0 + 0.03, d - 0.03)
add_ov("ov/e1.png", END_T + 0.15, END_D - 0.15, slide=50, fout=0)
add_ov("ov/e2.png", END_T + 0.55, END_D - 0.55, slide=40, fout=0)
add_ov("ov/e3.png", END_T + 0.95, END_D - 0.95, slide=40, fout=0)
fc.append(f"[{cur}]fade=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[vout]")
args += ["-i", "music.wav"]
aidx = idx
args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{aidx}:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high", "-level", "4.2",
         "-r", FPS, "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", str(TOTAL),
         "-movflags", "+faststart", "CPW_Ad_Vertical.mp4"]
open("filter.txt", "w").write(";\n".join(fc))
subprocess.run(args, check=True)
print("done")
