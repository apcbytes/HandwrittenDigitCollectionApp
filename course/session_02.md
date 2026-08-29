# Session 2 — Canvas & Capture

**Goal:** A drawable canvas on the page, and an understanding of what
a "drawing" actually is as data (a pixel array) before we process it.

**Duration:** ~60-75 min

---

## 1. Vibe-code first (~15 min)

Prompt:

> "Add a drawing canvas to my Streamlit app using
> streamlit-drawable-canvas, 280x280 pixels, black pen on white
> background, with a submit button."

Expect a working canvas fairly quickly — this component is popular
enough that most AI assistants know it well. Good, low-friction win.

## 2. Read & break it down (~10 min)

Run it. Draw something. Then ask:

- "We drew a picture. What does the *computer* actually have right
  now — is it a picture file? A list of coordinates? Something else?"
- Look up `canvas_result.image_data` together — reveal it's a NumPy
  array. Print its `.shape` live: `(280, 280, 4)`.
- Ask: "Why 4? What could that 4th number be?" (Answer: RGBA — Red,
  Green, Blue, Alpha/transparency channels.)

This is the pivot moment: **a drawing is just numbers** — this sets up
Session 3 perfectly.

## 3. Hand-code the core concept (~25 min)

### Step 3a — wire the canvas with intention, not just paste

```python
from streamlit_drawable_canvas import st_canvas

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=18,       # thick strokes -> more robust to later downscaling
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key="canvas_demo",
)
```

**Teaching point on `stroke_width=18`:** ask why we don't use a thin
1px pen. (Because we'll scale this down to 28x28 later — a 1px line
would vanish or become a faint dotted mess. Thick strokes survive
downscaling.)

**Teaching point on `key`:** Streamlit widgets need stable keys to
preserve state across reruns. We'll later make this key depend on
which digit we're collecting (`f"canvas_{target}"`), so each digit
prompt gets a *fresh* blank canvas.

### Step 3b — inspect the raw array live

```python
if canvas_result.image_data is not None:
    arr = canvas_result.image_data
    st.write("Shape:", arr.shape)
    st.write("Dtype:", arr.dtype)
    st.write("Value range:", arr.min(), "-", arr.max())
```

Have learners draw, then read these values out loud. Confirm as a
group: white background pixels are near `255` in RGB channels; drawn
strokes are near `0` (black). This distinction — "high value = empty,
low value = ink" — is the **opposite** of what MNIST expects (MNIST:
0 = background, high = digit). Flag this now; Session 3 fixes it with
an inversion step.

### Step 3c — a "clear if empty" guard

```python
def canvas_has_content(image_data) -> bool:
    if image_data is None:
        return False
    # any pixel where alpha > 0 and it's not pure white background
    import numpy as np
    gray = image_data[:, :, :3].mean(axis=2)
    return (gray < 250).any()
```

Ask: "why check `< 250` instead of `< 255`? What could cause
near-white-but-not-quite-255 pixels?" (Anti-aliasing at stroke edges.)

## 4. Reconcile & test (~15 min)

- Draw a digit, submit, confirm the shape/dtype output makes sense.
- Try clicking submit with an empty canvas — confirm the guard catches it.
- Discuss: this raw array is NOT yet what we save. Session 3 turns it
  into a proper 28x28 MNIST-style image.

## Checkpoint

- [ ] Canvas renders and accepts freehand drawing
- [ ] Group can state the shape and meaning of `image_data` from memory
- [ ] Group can explain why background ≠ 0 in the raw canvas data
- [ ] Empty-canvas submission is caught before saving
