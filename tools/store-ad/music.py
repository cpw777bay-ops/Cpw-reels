import numpy as np
from scipy.io import wavfile
SR = 48000
BPM = 120
BEAT = 60 / BPM
DUR = 25.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    L[i:i+len(s)] += s * np.sqrt(0.5 * (1 - pan)) * 1.414
    R[i:i+len(s)] += s * np.sqrt(0.5 * (1 + pan)) * 1.414

def env(n, a=0.005, d=0.2, curve=1.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d) ** curve
    return e

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.22)
    s += 0.3 * rng.standard_normal(n) * np.exp(-t / 0.004)
    return np.tanh(s * 1.8) * 0.9

def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    e = np.zeros(n)
    for o in (0, 0.01, 0.02):
        e += np.where(t >= o, np.exp(-(t - o) / 0.012), 0)
    e += np.exp(-t / 0.09) * 0.6
    from scipy.signal import butter, lfilter
    b, a = butter(2, [900 / (SR/2), 6000 / (SR/2)], 'band')
    return lfilter(b, a, nz * e) * 0.9

def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    from scipy.signal import butter, lfilter
    b, a = butter(2, 7000 / (SR/2), 'high')
    return lfilter(b, a, rng.standard_normal(n)) * np.exp(-t / (0.08 if open_ else 0.015)) * 0.35

def saw(f, n, detune=(0,), sr=SR):
    t = np.arange(n) / sr
    out = np.zeros(n)
    for d in detune:
        ff = f * 2 ** (d / 1200)
        ph = (t * ff + rng.random()) % 1.0
        out += 2 * ph - 1
    return out / len(detune)

def lowpass(x, fc):
    from scipy.signal import butter, lfilter
    b, a = butter(2, min(fc, SR/2 - 100) / (SR/2), 'low')
    return lfilter(b, a, x)

def note(m): return 440 * 2 ** ((m - 69) / 12)

# Chord progression Am - F - C - G (one bar each, 2s)
prog = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [67, 72, 76]), (55, [67, 71, 74])]

def impact(t, g=1.0):
    n = int(2.5 * SR); tt = np.arange(n) / SR
    f = 30 + 60 * np.exp(-tt / 0.15)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.7)
    nz = lowpass(rng.standard_normal(n), 3000) * np.exp(-tt / 0.5) * 0.5
    add(np.tanh((boom + nz) * 1.5) * 0.9, t, g)

def riser(t0, t1, g=0.5):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        fc = 400 + 9000 * (i / n) ** 2
        out[i:i+blk] = lowpass(x[i:i+blk], fc)
    out *= (tt / tt[-1]) ** 2
    add(out * g, t0, 1.0)

def whoosh(t, g=0.35):
    n = int(0.4 * SR); tt = np.arange(n) / SR
    x = lowpass(rng.standard_normal(n), 5000)
    e = np.sin(np.pi * tt / tt[-1]) ** 2
    add(x * e * g, t - 0.2, 1.0)

MAIN_END = 20.0
# Drums
t = 0.0
while t < MAIN_END - 1e-6:
    b = round(t / BEAT)
    add(kick(), t, 0.95)
    if b % 2 == 1: add(clap(), t, 0.55)
    add(hat(), t + BEAT/2, 0.6, 0.3)
    add(hat(), t + BEAT/4, 0.25, -0.3); add(hat(), t + 3*BEAT/4, 0.25, -0.3)
    if b % 4 == 3: add(hat(True), t + BEAT/2, 0.4, 0.2)
    t += BEAT
# drum fill / snare roll before end card
for k in range(8):
    tt = 19.0 + k * BEAT / 4
    add(clap(), tt, 0.25 + 0.05 * k)

# Bass: 8th notes on root, sidechain pump
bar = 2.0
for i in range(int(MAIN_END / bar)):
    root, chord = prog[i % 4]
    for k in range(8):
        tt = i * bar + k * BEAT / 2
        n = int(BEAT / 2 * SR * 0.9)
        f = note(root - 12 + (12 if k % 2 else 0))
        s = lowpass(saw(f, n, (-6, 6)), 900) * env(n, 0.003, 0.18)
        s += np.sin(2*np.pi*note(root-12)*np.arange(n)/SR) * env(n, 0.003, 0.2) * 0.6
        add(np.tanh(s * 1.5) * 0.42, tt)
    # Supersaw chord stabs (offbeat 8ths) and pad
    for k in range(4):
        tt = i * bar + k * BEAT + BEAT / 2
        n = int(0.22 * SR)
        s = sum(saw(note(m), n, (-12, -4, 4, 12)) for m in chord)
        s = lowpass(s, 4500) * env(n, 0.004, 0.09)
        add(s * 0.09, tt, 1, -0.4); add(s * 0.09, tt + 0.012, 1, 0.4)
    n = int(bar * SR)
    pad = sum(saw(note(m - 12), n, (-10, 10)) for m in chord)
    pad = lowpass(pad, 1400) * np.minimum(1, np.arange(n) / (0.3*SR))
    add(pad * 0.035, i * bar, 1, -0.2); add(pad * 0.035, i * bar + 0.02, 1, 0.2)
    # lead arp
    arp = [chord[0]+12, chord[1]+12, chord[2]+12, chord[1]+12]
    for k in range(16):
        tt = i * bar + k * BEAT / 4
        n = int(BEAT/4 * SR)
        s = lowpass(saw(note(arp[k % 4]), n, (-5, 5)), 3500) * env(n, 0.002, 0.06)
        add(s * 0.05, tt, 1, 0.5 if k % 2 else -0.5)

# Sidechain pump on everything but drums: simpler — compute pump envelope and apply to whole mix lightly after
pump = np.ones(N)
for b in range(int(MAIN_END / BEAT)):
    i = int(b * BEAT * SR); n = int(BEAT * SR)
    tt = np.arange(n) / SR
    pump[i:i+n] = np.minimum(pump[i:i+n], 0.55 + 0.45 * (1 - np.exp(-tt / 0.08)))
# drums mixed separately? Keep it simple: apply mild pump to whole mix (kick transient survives due to attack)
L *= pump ** 0.5; R *= pump ** 0.5

# FX
impact(0.0, 0.8)
for tc in [2, 5, 7, 10, 12, 14, 18]:
    whoosh(tc, 0.3)
riser(16.0, 20.0, 0.35)
impact(20.0, 1.0)

# End card: pad + soft pulse, fade out
i0 = int(20.0 * SR); n = N - i0
for root, chord in [prog[0]]:
    s = sum(saw(note(m - 12), n, (-12, 0, 12)) for m in chord + [root])
    s = lowpass(s, 1800) * np.exp(-np.arange(n) / SR / 2.2)
    L[i0:] += s * 0.05; R[i0:] += s * 0.05
for k in range(8):
    t = 20.0 + k * BEAT
    add(kick(), t, 0.35 * (1 - k / 8))
    add(hat(), t + BEAT / 2, 0.25 * (1 - k / 8))

# simple reverb (noise IR)
from scipy.signal import fftconvolve
ir_n = int(1.2 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.35)
ir = lowpass(ir, 6000); ir /= np.sqrt(np.sum(ir**2))
wetL = fftconvolve(L, ir)[:N]; wetR = fftconvolve(R, np.roll(ir, 300))[:N]
L = L + 0.12 * wetL; R = R + 0.12 * wetR

fade = np.ones(N); fn = int(1.5 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 2
mix = np.stack([L * fade, R * fade], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * 0.89
wavfile.write("music_raw.wav", SR, mix.astype(np.float32))
print('ok')
