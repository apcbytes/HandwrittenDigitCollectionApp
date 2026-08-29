# Session 3 — The Preprocessing Pipeline (the conceptual heart of HDCA)

**Goal:** Turn a raw canvas drawing into a proper MNIST-style 28x28
image: cropped to the digit, scaled to fit, and centered by mass —
matching the actual preprocessing MNIST itself used.

**Duration:** ~75-90 min (don't compress this one)

**Note:** this session is intentionally almost entirely hand-coded.
Vibe-coding tends to produce a plausible-looking but subtly wrong
version (e.g. centering by bounding box instead of center of mass, or
skipping the inversion step) — which is itself a great teaching
moment if you want it. See the optional "vibe-code trap" exercise at
the end.

---

## 0. Set the stage (~5 min)

Ask: "MNIST digits all look strangely uniform — same size, roughly
centered. Real handwriting isn't like that. Someone had to process
70,000 raw drawings into that uniform 28x28 format. What steps do you
think that involved?"

Let the class guess. Write guesses on the board. You're aiming to
arrive at: crop, scale, center. Then reveal the real MNIST recipe uses
*center of mass*, not just bounding-box center — this surprises people
and is worth building suspense around.

## 1. Step through each transformation, hand-coded

Build `preprocess.py` function by function. For each one, run it on a
real drawing and **look at the intermediate result** (print shapes,
show images) before moving to the next step.

### Step 1a — grayscale + invert

```python
import numpy as np
from PIL import Image

def rgba_canvas_to_grayscale(rgba_array: np.ndarray) -> np.ndarray:
    img = Image.fromarray(rgba_array.astype("uint8"), mode="RGBA")
    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(background, img).convert("L")
    gray = np.array(composited).astype(np.float32)
    ink = 255.0 - gray   # invert: background becomes 0, ink becomes bright
    return ink
```

**Discuss:** Why composite onto a white background first? (The canvas
alpha channel could have transparency; compositing guarantees a
consistent white background before we grayscale.) Why invert? (Session
2 established raw canvas = white bg/black ink; MNIST convention is the
opposite. This line is the fix.)

### Step 1b — crop to bounding box

```python
def crop_to_bounding_box(ink: np.ndarray, threshold: float = 10.0):
    mask = ink > threshold
    if not mask.any():
        return None   # nothing drawn
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return ink[rmin:rmax + 1, cmin:cmax + 1]
```

**Discuss:** Walk through `np.any(mask, axis=1)` by hand on a tiny
example (e.g. a 5x5 grid drawn on the whiteboard) — this is the line
learners are least likely to intuit. `axis=1` collapses each row to
"did this row have any ink?" — that's how we find the top/bottom edges.

**Why threshold=10, not 0?** Anti-aliasing again — a few near-zero
noise pixels shouldn't count as "ink."

### Step 1c — scale to fit a 20x20 inner box, preserving aspect ratio

```python
def scale_to_inner_box(cropped: np.ndarray, inner: int = 20):
    h, w = cropped.shape
    if h > w:
        new_h = inner
        new_w = max(1, round(w * (inner / h)))
    else:
        new_w = inner
        new_h = max(1, round(h * (inner / w)))
    img = Image.fromarray(cropped.astype("uint8"))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    return np.array(resized).astype(np.float32)
```

**Discuss:** Why scale to 20x20, not 28x28 directly? This is a direct
MNIST convention — leaving a margin means the digit doesn't touch the
frame edges, closer to natural handwriting. Why preserve aspect ratio
instead of squashing to 20x20? (A "1" squashed to a square would look
wrong — a thin tall digit should stay thin and tall.)

### Step 1d — paste onto 28x28, centered by MASS not bounding box

This is the payoff moment.

```python
from scipy import ndimage

def paste_centered_by_mass(scaled: np.ndarray, canvas_size: int = 28):
    canvas = np.zeros((canvas_size, canvas_size), dtype=np.float32)
    h, w = scaled.shape
    top = (canvas_size - h) // 2
    left = (canvas_size - w) // 2
    canvas[top:top + h, left:left + w] = scaled   # bounding-box centered (first pass)

    cy, cx = ndimage.center_of_mass(canvas)         # find the "weight" center
    shift_y = round(canvas_size / 2 - cy)
    shift_x = round(canvas_size / 2 - cx)
    shifted = ndimage.shift(canvas, shift=(shift_y, shift_x), mode="constant", cval=0.0)
    return shifted
```

**Live demo the difference:** draw a digit like "7" where the ink is
concentrated in the upper-right (the horizontal stroke) — bounding-box
centering and mass centering will disagree visibly. Print both
`cy, cx` (before shift) vs `(13.5, 13.5)` (target) to show the offset
being corrected.

**Analogy that lands well:** "If you centered a see-saw by its
physical *ends* instead of where the weight actually balances, one
side would tip. Center of mass is where the digit 'balances.'"

## 2. Assemble the full pipeline (~10 min)

```python
def to_mnist_28x28(rgba_array: np.ndarray):
    ink = rgba_canvas_to_grayscale(rgba_array)
    cropped = crop_to_bounding_box(ink)
    if cropped is None:
        return None
    scaled = scale_to_inner_box(cropped)
    centered = paste_centered_by_mass(scaled)
    return np.clip(centered, 0, 255).astype(np.uint8)
```

## 3. Test against real MNIST intuition (~15 min)

Have each learner draw a few digits and eyeball the 28x28 preview.
Ask: "does this look like it belongs in the MNIST dataset?" Compare
side-by-side with real MNIST sample images if you have internet access
(many small MNIST sample PNGs are available in common ML tutorials).

## Optional: the "vibe-code trap" exercise (~15 min, if time allows)

Now prompt an AI assistant:

> "Write a function to center a digit in a 28x28 image."

Compare its output to what you hand-coded. Very likely it centers by
bounding box only (skips center-of-mass), or skips the aspect-ratio
preservation. Ask the class to spot the difference and explain *why*
it matters — this reinforces that vibe-coding gets you *something*
fast, but the details that make it *correct* often need human review.

## Checkpoint

- [ ] `preprocess.py` implements all 4 steps and `to_mnist_28x28()`
- [ ] Group can explain, without notes, what each of the 4 steps does
- [ ] Group can explain why center-of-mass beats bounding-box centering
- [ ] A hand-drawn digit produces a recognizable, roughly-centered 28x28 result
