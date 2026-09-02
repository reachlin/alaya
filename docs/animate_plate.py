"""Turn the static general-arrangement plate into a looping GIF.

The only thing that moves is the causal circuit: 種子生現行 rising on the left,
現行熏種子 descending on the right. That is not decoration — it is the one part
of the drawing that a still image cannot say. 恆轉如瀑流, "continuously turning
like a waterfall": the store looks continuous while nothing in it stays.

    python docs/animate_plate.py <plate.png> [out.gif]

The gold runs are found by colour rather than by hard-coded coordinates, so the
plate can be re-rendered at another size and this still lands on them.
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

GOLD = (230, 178, 92)          # --gold, as drawn in the plate
VERM = (228, 121, 90)          # --verm
SHEET = (11, 46, 79)           # the cyanotype ground, for antialias blends
PULSE = (255, 226, 160)        # the travelling head, a little hotter than the line
FRAMES = 36
MS = 55                        # ~2 s a loop
PULSES_PER_RUN = 2             # two heads per run reads as flow, not as one dot


def find_runs(img: Image.Image, rgb=GOLD, tol=60, min_len=60):
    """Locate the vertical gold arrows by colour."""
    a = np.asarray(img.convert("RGB")).astype(int)
    mask = np.abs(a - np.array(rgb)).sum(2) < tol
    ys, xs = np.nonzero(mask)
    runs = []
    for x, count in sorted(collections.Counter(xs).items()):
        if count < min_len:
            continue
        col = ys[xs == x]
        runs.append((x, int(col.min()), int(col.max())))
    return runs


def glow(draw: ImageDraw.ImageDraw, x: float, y: float):
    """A soft head: three passes, widest and faintest first."""
    for radius, alpha in ((7, 55), (4.5, 130), (2.4, 255)):
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     fill=(*PULSE, alpha))


def build(base: Image.Image, runs) -> list[Image.Image]:
    frames = []
    for f in range(FRAMES):
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for i, (x, top, bottom) in enumerate(runs):
            rising = i % 2 == 0          # left run carries 種子生現行 upward
            for p in range(PULSES_PER_RUN):
                t = ((f / FRAMES) + p / PULSES_PER_RUN) % 1.0
                y = bottom - t * (bottom - top) if rising else top + t * (bottom - top)
                glow(draw, x, y)
        frames.append(Image.alpha_composite(base.convert("RGBA"), overlay))
    return frames


def build_palette(base: Image.Image) -> Image.Image:
    """A palette with the two accents reserved.

    An adaptive quantiser optimises for how many pixels a colour covers, and the
    gold and vermilion runs are a few hundred pixels each on a field of blue. Left
    to itself it merged them into one entry — gold came out as vermilion, which
    silently destroyed the only distinction the legend rests on. So the accents and
    their antialias blends are reserved first, and the adaptive pass gets whatever
    is left over for the ground.
    """
    reserved: list[tuple[int, int, int]] = []
    for colour in (GOLD, PULSE, VERM):
        reserved.append(colour)
        for k in (0.75, 0.5, 0.25):     # blends toward the ground, for edges
            reserved.append(tuple(round(c * k + g * (1 - k)) for c, g in zip(colour, SHEET)))

    spare = 256 - len(reserved)
    adaptive = base.convert("RGB").quantize(colors=spare, method=Image.MEDIANCUT)
    ground = adaptive.getpalette()[: spare * 3]

    flat = [v for colour in reserved for v in colour] + ground
    flat += [0] * (768 - len(flat))
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat)
    return pal


def save_gif(frames: list[Image.Image], out: Path):
    """One shared palette across every frame, so the loop does not shimmer."""
    palette = build_palette(frames[0])
    quantised = [f.convert("RGB").quantize(palette=palette, dither=Image.NONE)
                 for f in frames]
    # disposal=1 keeps the previous frame, so Pillow writes only the rectangle
    # that actually changed — here, the few dozen pixels the heads move through.
    quantised[0].save(
        out, save_all=True, append_images=quantised[1:],
        duration=MS, loop=0, optimize=True, disposal=1,
    )


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/img/alaya-general-arrangement.png")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else src.with_suffix(".gif"))
    base = Image.open(src)
    runs = find_runs(base)
    if len(runs) < 2:
        raise SystemExit(f"expected two gold runs, found {len(runs)}: {runs}")
    print(f"gold runs: {runs}")
    save_gif(build(base, runs), out)
    print(f"{out}  {out.stat().st_size / 1024:.0f} KB  {FRAMES} frames  {base.size[0]}×{base.size[1]}")


if __name__ == "__main__":
    main()
