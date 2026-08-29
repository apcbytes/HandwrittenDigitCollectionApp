"""Storage dispatcher.

Selects a persistence backend at import time and re-exports its public
API unchanged, so app.py and pages/1_Admin.py never need to know which
one is active:

  * storage_disk  — PNGs under data/ + an Excel log. Default. Good for
    local development, but Streamlit Community Cloud's filesystem is
    ephemeral (wiped on every restart / redeploy), so it must NOT be
    used there.

  * storage_cloud — submissions log in a Google Sheet, PNGs in a Google
    Drive folder, via a service account. Use this on Streamlit
    Community Cloud. See DEPLOY.md.

Backend choice, in priority order:
  1. env var  HDCA_STORAGE_BACKEND = "disk" | "cloud"
  2. secrets   [storage] backend = "disk" | "cloud"
  3. default: "disk"

Public API (identical across backends):
  save_sample, load_progress, resubmit_attempt_number, load_all,
  set_status, set_status_for_email, set_status_for_emails,
  build_mnist_dataframe, load_processed_image, load_raw_image,
  ensure_dirs, STATUSES, PIXEL_COLUMNS, LOG_COLUMNS, IMAGES_DIR, RAW_DIR
"""

import os


def _select_backend() -> str:
    choice = os.environ.get("HDCA_STORAGE_BACKEND")
    if not choice:
        try:
            import streamlit as st

            choice = st.secrets.get("storage", {}).get("backend")
        except Exception:
            choice = None
    return (choice or "disk").strip().lower()


BACKEND = _select_backend()

if BACKEND == "cloud":
    from storage_cloud import (  # noqa: F401
        LOG_COLUMNS,
        PIXEL_COLUMNS,
        STATUSES,
        IMAGES_DIR,
        RAW_DIR,
        build_mnist_dataframe,
        ensure_dirs,
        load_all,
        load_processed_image,
        load_progress,
        load_raw_image,
        resubmit_attempt_number,
        save_sample,
        set_status,
        set_status_for_email,
        set_status_for_emails,
    )
else:
    from storage_disk import (  # noqa: F401
        LOG_COLUMNS,
        PIXEL_COLUMNS,
        STATUSES,
        IMAGES_DIR,
        RAW_DIR,
        build_mnist_dataframe,
        ensure_dirs,
        load_all,
        load_processed_image,
        load_progress,
        load_raw_image,
        resubmit_attempt_number,
        save_sample,
        set_status,
        set_status_for_email,
        set_status_for_emails,
    )
