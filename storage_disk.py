"""Local-disk persistence backend: save each contributed digit (raw +
processed) as PNGs under data/ and append a row to an Excel log with a
review status.

This is the original storage.py implementation, moved here so storage.py
can dispatch between this and the cloud (Google Sheets + Drive) backend.
Public API kept identical.
"""

import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from preprocess import array_to_pil

PIXEL_COLUMNS = [f"pixel{i}" for i in range(28 * 28)]

DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
RAW_DIR = os.path.join(DATA_DIR, "raw")
LOG_PATH = os.path.join(DATA_DIR, "labels.xlsx")

LOG_COLUMNS = ["timestamp_utc", "name", "email", "label", "image_filename", "raw_filename", "status"]
STATUSES = ("pending", "approved", "rejected")


def _safe_slug(text: str) -> str:
    """Turn an email/name into a filesystem-safe slug for filenames."""
    keep = "-_."
    return "".join(c if c.isalnum() or c in keep else "_" for c in text)


def ensure_dirs() -> None:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)


def _log_mtime() -> float:
    """Excel file's last-modified time — used as a cache-busting key so
    _load_log_cached only re-reads the file from disk when it actually
    changed, instead of on every Streamlit rerun."""
    return os.path.getmtime(LOG_PATH) if os.path.exists(LOG_PATH) else 0.0


@st.cache_data(show_spinner=False)
def _load_log_cached(_mtime: float) -> pd.DataFrame:
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame(columns=LOG_COLUMNS)
    df = pd.read_excel(LOG_PATH)
    # backward-compat: older rows may predate raw_filename/status columns,
    # and blank Excel cells for existing rows read back as NaN (float), not ""
    if "raw_filename" not in df.columns:
        df["raw_filename"] = ""
    df["raw_filename"] = df["raw_filename"].fillna("").astype(str)
    if "status" not in df.columns:
        df["status"] = "approved"  # pre-existing submissions are grandfathered in
    df["status"] = df["status"].fillna("approved").astype(str)
    return df


def _load_log() -> pd.DataFrame:
    return _load_log_cached(_log_mtime())


def save_sample(name: str, email: str, label: int, image_array: np.ndarray, raw_rgba: np.ndarray) -> str:
    """Save the 28x28 processed array and the raw canvas as PNGs, and
    append a pending row to the Excel log. Returns the processed filename."""
    ensure_dirs()

    ts = datetime.now(timezone.utc)
    ts_str = ts.strftime("%Y%m%dT%H%M%S%fZ")
    slug = _safe_slug(email)
    filename = f"{slug}_{label}_{ts_str}.png"
    raw_filename = f"{slug}_{label}_{ts_str}_raw.png"

    array_to_pil(image_array).save(os.path.join(IMAGES_DIR, filename))
    Image.fromarray(raw_rgba.astype("uint8"), mode="RGBA").convert("RGB").save(os.path.join(RAW_DIR, raw_filename))

    row = {
        "timestamp_utc": ts.isoformat(),
        "name": name,
        "email": email,
        "label": label,
        "image_filename": filename,
        "raw_filename": raw_filename,
        "status": "pending",
    }

    df = _load_log()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_excel(LOG_PATH, index=False)
    return filename


def load_progress(email: str) -> set[int]:
    """Which digits (0-9) has this learner already submitted, excluding
    rejected ones — a reject clears that digit slot so they can redraw it."""
    df = _load_log()
    if df.empty:
        return set()
    mine = df[(df["email"] == email) & (df["status"] != "rejected")]
    return set(mine["label"].astype(int).tolist())


def resubmit_attempt_number(email: str, label: int) -> int:
    """How many times (including rejected ones) has this learner
    already submitted this digit? Used to give the drawing canvas a
    fresh widget key on redraw, instead of reusing a stale one."""
    df = _load_log()
    if df.empty:
        return 0
    mine = df[(df["email"] == email) & (df["label"] == label)]
    return len(mine)


def load_all() -> pd.DataFrame:
    """Full submissions log, with backward-compatible columns."""
    return _load_log()


def set_status(row_index: int, status: str) -> None:
    """Update the review status of a single submission by its row index."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    df = _load_log()
    df.loc[row_index, "status"] = status
    df.to_excel(LOG_PATH, index=False)


def set_status_for_email(email: str, status: str) -> int:
    """Bulk-update every submission belonging to one learner (e.g.
    reject their whole batch of 10 in one click so they redraw all of
    it). Returns how many rows were changed."""
    return set_status_for_emails([email], status)


def set_status_for_emails(emails: list[str], status: str) -> int:
    """Bulk-update every submission belonging to any of several learners
    in one write (multi-select bulk actions). Returns how many rows
    were changed."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    df = _load_log()
    mask = df["email"].isin(emails)
    df.loc[mask, "status"] = status
    df.to_excel(LOG_PATH, index=False)
    return int(mask.sum())


def load_processed_image(image_filename: str) -> np.ndarray | None:
    """Return the 28x28 processed digit as a uint8 grayscale (L) array,
    or None if it can't be found."""
    path = os.path.join(IMAGES_DIR, str(image_filename))
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path).convert("L"))


def load_raw_image(raw_filename: str) -> np.ndarray | None:
    """Return the raw canvas drawing as an RGBA uint8 array, or None if
    this submission predates raw-canvas saving / the file is missing."""
    if not isinstance(raw_filename, str) or not raw_filename:
        return None
    path = os.path.join(RAW_DIR, raw_filename)
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path).convert("RGBA"))


def build_mnist_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Turn approved rows into an MNIST-style table: one row per digit,
    784 flattened pixel columns (pixel0..pixel783) plus a label column,
    matching the classic MNIST CSV layout used for training."""
    approved = df[df["status"] == "approved"]
    records = []
    for _, row in approved.iterrows():
        arr = load_processed_image(row["image_filename"])
        if arr is None:
            continue
        arr = arr.flatten()
        record = {"label": int(row["label"]), "name": row["name"], "email": row["email"]}
        record.update({col: int(v) for col, v in zip(PIXEL_COLUMNS, arr)})
        records.append(record)

    columns = ["label", "name", "email"] + PIXEL_COLUMNS
    if not records:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(records, columns=columns)
