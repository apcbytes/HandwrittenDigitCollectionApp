"""Cloud persistence backend for Streamlit Community Cloud (ephemeral
filesystem): the submissions log lives in a Google Sheet, the PNGs live
in a Google Drive folder. Both are accessed with a Google service
account whose credentials come from st.secrets.

Public API is identical to storage_disk.py so storage.py can dispatch
between the two. See DEPLOY.md for how to provision the service account,
the sheet, and the Drive folder.

Required secrets (see DEPLOY.md for the full TOML template):

    [storage]
    backend = "cloud"
    gsheet_id = "…"            # the Google Sheet's file ID (from its URL)
    gdrive_folder_id = "…"      # the Drive folder's ID (from its URL)

    [gcp_service_account]
    type = "service_account"
    project_id = "…"
    private_key_id = "…"
    private_key = "-----BEGIN PRIVATE KEY-----\n…\n-----END PRIVATE KEY-----\n"
    client_email = "…@….iam.gserviceaccount.com"
    client_id = "…"
    token_uri = "https://oauth2.googleapis.com/token"
"""

import io
from datetime import datetime, timezone

import gspread
import numpy as np
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build as _build_drive
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from PIL import Image

from preprocess import array_to_pil

PIXEL_COLUMNS = [f"pixel{i}" for i in range(28 * 28)]

LOG_COLUMNS = ["timestamp_utc", "name", "email", "label", "image_filename", "raw_filename", "status"]
STATUSES = ("pending", "approved", "rejected")
WORKSHEET_NAME = "submissions"

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# storage.py re-exports these for pages/1_Admin.py; kept as harmless
# placeholders on the cloud backend (no local dirs are used).
IMAGES_DIR = "data/images"
RAW_DIR = "data/raw"


# --------------------------------------------------------------------------
# Auth / client helpers (cached for the session)
# --------------------------------------------------------------------------
def _creds() -> Credentials:
    info = dict(st.secrets["gcp_service_account"])
    return Credentials.from_service_account_info(info, scopes=_SCOPES)


@st.cache_resource(show_spinner=False)
def _worksheet():
    gc = gspread.authorize(_creds())
    sh = gc.open_by_key(st.secrets["storage"]["gsheet_id"])
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=len(LOG_COLUMNS))
    if ws.row_values(1) != LOG_COLUMNS:
        ws.update([LOG_COLUMNS], "A1")
    return ws


@st.cache_resource(show_spinner=False)
def _drive():
    return _build_drive("drive", "v3", credentials=_creds(), cache_discovery=False)


def _folder_id() -> str:
    return st.secrets["storage"]["gdrive_folder_id"]


# --------------------------------------------------------------------------
# Log (Google Sheet) read/write
# --------------------------------------------------------------------------
def _log_version() -> int:
    """Cheap change token so _load_log_cached only re-pulls the whole
    sheet when the row count actually changed (append/edit both touch it
    for appends; edits are handled by clearing the cache explicitly)."""
    try:
        return len(_worksheet().col_values(1))
    except Exception:
        return 0


@st.cache_data(show_spinner=False)
def _load_log_cached(_version: int) -> pd.DataFrame:
    records = _worksheet().get_all_records(expected_headers=LOG_COLUMNS)
    if not records:
        return pd.DataFrame(columns=LOG_COLUMNS)
    df = pd.DataFrame(records, columns=LOG_COLUMNS)
    df["raw_filename"] = df["raw_filename"].fillna("").astype(str)
    df["status"] = df["status"].replace("", "approved").fillna("approved").astype(str)
    df["label"] = df["label"].astype(int)
    return df


def _load_log() -> pd.DataFrame:
    return _load_log_cached(_log_version())


def _invalidate_log_cache() -> None:
    _load_log_cached.clear()


# --------------------------------------------------------------------------
# Images (Google Drive) read/write
# --------------------------------------------------------------------------
def _upload_png(pil_image: Image.Image, filename: str) -> str:
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    media = MediaIoBaseUpload(buf, mimetype="image/png", resumable=False)
    meta = {"name": filename, "parents": [_folder_id()]}
    f = _drive().files().create(body=meta, media_body=media, fields="id").execute()
    return f["id"]


@st.cache_data(show_spinner=False)
def _download_png_bytes(filename: str) -> bytes | None:
    drive = _drive()
    q = (
        f"name = '{filename}' and '{_folder_id()}' in parents and trashed = false"
    )
    res = drive.files().list(q=q, fields="files(id)", pageSize=1).execute()
    files = res.get("files", [])
    if not files:
        return None
    request = drive.files().get_media(fileId=files[0]["id"])
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def _safe_slug(text: str) -> str:
    keep = "-_."
    return "".join(c if c.isalnum() or c in keep else "_" for c in text)


def ensure_dirs() -> None:  # no-op on cloud; kept for API parity
    pass


def save_sample(name: str, email: str, label: int, image_array: np.ndarray, raw_rgba: np.ndarray) -> str:
    ts = datetime.now(timezone.utc)
    ts_str = ts.strftime("%Y%m%dT%H%M%S%fZ")
    slug = _safe_slug(email)
    filename = f"{slug}_{label}_{ts_str}.png"
    raw_filename = f"{slug}_{label}_{ts_str}_raw.png"

    _upload_png(array_to_pil(image_array), filename)
    raw_pil = Image.fromarray(raw_rgba.astype("uint8"), mode="RGBA").convert("RGB")
    _upload_png(raw_pil, raw_filename)

    _worksheet().append_row(
        [ts.isoformat(), name, email, int(label), filename, raw_filename, "pending"],
        value_input_option="USER_ENTERED",
    )
    _invalidate_log_cache()
    return filename


def load_progress(email: str) -> set[int]:
    df = _load_log()
    if df.empty:
        return set()
    mine = df[(df["email"] == email) & (df["status"] != "rejected")]
    return set(mine["label"].astype(int).tolist())


def resubmit_attempt_number(email: str, label: int) -> int:
    df = _load_log()
    if df.empty:
        return 0
    mine = df[(df["email"] == email) & (df["label"] == label)]
    return len(mine)


def load_all() -> pd.DataFrame:
    return _load_log()


def _rewrite_status_column(df: pd.DataFrame) -> None:
    """Push the whole status column back to the sheet in one batch call.
    Sheet rows are df row i -> spreadsheet row i+2 (1 header row)."""
    status_idx = LOG_COLUMNS.index("status")  # 0-based
    col_letter = chr(ord("A") + status_idx)
    cells = [[s] for s in df["status"].astype(str).tolist()]
    _worksheet().update(cells, f"{col_letter}2:{col_letter}{len(cells) + 1}")
    _invalidate_log_cache()


def set_status(row_index: int, status: str) -> None:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    df = _load_log()
    df.loc[row_index, "status"] = status
    _rewrite_status_column(df)


def set_status_for_email(email: str, status: str) -> int:
    return set_status_for_emails([email], status)


def set_status_for_emails(emails: list[str], status: str) -> int:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    df = _load_log()
    mask = df["email"].isin(emails)
    df.loc[mask, "status"] = status
    _rewrite_status_column(df)
    return int(mask.sum())


def load_processed_image(image_filename: str) -> np.ndarray | None:
    data = _download_png_bytes(str(image_filename))
    if data is None:
        return None
    return np.array(Image.open(io.BytesIO(data)).convert("L"))


def load_raw_image(raw_filename: str) -> np.ndarray | None:
    if not isinstance(raw_filename, str) or not raw_filename:
        return None
    data = _download_png_bytes(raw_filename)
    if data is None:
        return None
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def build_mnist_dataframe(df: pd.DataFrame) -> pd.DataFrame:
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
