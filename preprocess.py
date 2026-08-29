"""
Digit preprocessing: raw canvas strokes -> MNIST-style 28x28 image.

MNIST's own preprocessing recipe (this mirrors it):
  1. Take the drawn strokes on a (larger) canvas.
  2. Find the bounding box of the ink (crop away empty margins).
  3. Scale the cropped digit so its longest side fits in a 20x20 box,
     preserving aspect ratio (MNIST uses 20x20 inside a 28x28 frame).
  4. Paste the scaled digit onto a blank 28x28 canvas.
  5. Shift the digit so its *center of mass* (not just bounding-box
     center) lands on the center of the 28x28 frame. This is the detail
     most from-scratch demos skip, and it's why MNIST digits look so
     uniformly centered.
"""

import numpy as np
from PIL import Image
from scipy import ndimage

CANVAS_SIZE = 28
INNER_BOX = 20  # digit is scaled to fit this box, matching MNIST


def rgba_canvas_to_grayscale(rgba_array: np.ndarray) -> np.ndarray:
    """streamlit-drawable-canvas gives an RGBA array (white bg, colored
    strokes). Convert to single-channel grayscale where higher = more ink,
    matching MNIST's convention (digit is bright, background is 0)."""
    img = Image.fromarray(rgba_array.astype("uint8"), mode="RGBA")
    # Composite onto white background first (in case of transparency)
    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(background, img).convert("L")
    gray = np.array(composited).astype(np.float32)
    # Invert: canvas is white=255 background, dark strokes. MNIST wants
    # background=0, digit=bright.
    ink = 255.0 - gray
    return ink


def crop_to_bounding_box(ink: np.ndarray, threshold: float = 10.0) -> np.ndarray | None:
    """Crop the image to the bounding box of pixels above `threshold`.
    Returns None if the canvas is empty (nothing drawn)."""
    mask = ink > threshold
    if not mask.any():
        return None
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return ink[rmin:rmax + 1, cmin:cmax + 1]


def scale_to_inner_box(cropped: np.ndarray, inner: int = INNER_BOX) -> np.ndarray:
    """Resize (preserving aspect ratio) so the longer side == inner px."""
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


def paste_centered_by_mass(scaled: np.ndarray, canvas_size: int = CANVAS_SIZE) -> np.ndarray:
    """Paste `scaled` onto a blank canvas, shifted so the digit's center
    of mass sits at the canvas center (MNIST's exact approach)."""
    canvas = np.zeros((canvas_size, canvas_size), dtype=np.float32)
    h, w = scaled.shape
    top = (canvas_size - h) // 2
    left = (canvas_size - w) // 2
    canvas[top:top + h, left:left + w] = scaled

    cy, cx = ndimage.center_of_mass(canvas)
    if np.isnan(cy) or np.isnan(cx):
        return canvas  # shouldn't happen (we already checked non-empty)

    shift_y = round(canvas_size / 2 - cy)
    shift_x = round(canvas_size / 2 - cx)
    shifted = ndimage.shift(canvas, shift=(shift_y, shift_x), mode="constant", cval=0.0)
    return shifted


def preprocess_with_stages(rgba_array: np.ndarray) -> dict | None:
    """Same pipeline as to_mnist_28x28, but returns every intermediate
    array too — used by the admin review UI to show each step.
    Returns None if the canvas was empty."""
    ink = rgba_canvas_to_grayscale(rgba_array)
    cropped = crop_to_bounding_box(ink)
    if cropped is None:
        return None
    scaled = scale_to_inner_box(cropped)
    centered = paste_centered_by_mass(scaled)
    final = np.clip(centered, 0, 255).astype(np.uint8)
    return {
        "ink": np.clip(ink, 0, 255).astype(np.uint8),
        "cropped": np.clip(cropped, 0, 255).astype(np.uint8),
        "scaled": np.clip(scaled, 0, 255).astype(np.uint8),
        "final": final,
    }


def to_mnist_28x28(rgba_array: np.ndarray) -> np.ndarray | None:
    """Full pipeline: raw canvas RGBA -> 28x28 uint8 array (0-255,
    background=0, digit=bright), centered by mass. Returns None if the
    canvas was empty."""
    ink = rgba_canvas_to_grayscale(rgba_array)
    cropped = crop_to_bounding_box(ink)
    if cropped is None:
        return None
    scaled = scale_to_inner_box(cropped)
    centered = paste_centered_by_mass(scaled)
    result = np.clip(centered, 0, 255).astype(np.uint8)
    return result


def array_to_pil(arr_28x28: np.ndarray) -> Image.Image:
    """Convert a 28x28 uint8 array to a PIL Image for saving/display."""
    return Image.fromarray(arr_28x28, mode="L")
