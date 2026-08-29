"""Matplotlib-based pixel-grid rendering for the admin review UI: each
stage of the pipeline shown as a labeled grid, matching how MNIST
arrays are conventionally visualized. 0 = black (background), 255 =
white (ink)."""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

MAX_INCHES = 5.0


@st.cache_data(show_spinner=False)
def render_pixel_grid(arr: np.ndarray, title: str = "") -> bytes:
    """Render a 2D uint8 array as a grayscale heatmap with axis ticks,
    a light cell grid, and a colorbar showing the 0-255 intensity
    scale. Returns PNG bytes. Capped at MAX_INCHES x MAX_INCHES.
    Cached: the same (raw pixels, title) pair is re-rendered through
    matplotlib only once, instead of on every Streamlit rerun."""
    h, w = arr.shape

    side = min(MAX_INCHES, max(2.4, max(h, w) / 9))
    fig, ax = plt.subplots(figsize=(side + 0.6, side), dpi=130)

    im = ax.imshow(arr, cmap="gray", vmin=0, vmax=255, interpolation="nearest")

    ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
    ax.grid(which="minor", color="#888888", linewidth=0.3, alpha=0.4)
    ax.set_xticks(np.arange(0, w, max(1, w // 7)))
    ax.set_yticks(np.arange(0, h, max(1, h // 7)))
    ax.tick_params(labelsize=7, length=2)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("pixel intensity (0=black, 255=white)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6.5)

    if title:
        ax.set_title(title, fontsize=9)

    fig.tight_layout(pad=0.4)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
