import io

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import theme
from preprocess import preprocess_with_stages
from storage import (
    build_mnist_dataframe,
    load_all,
    load_processed_image,
    load_raw_image,
    set_status,
    set_status_for_email,
    set_status_for_emails,
)
from visualize import render_pixel_grid

st.set_page_config(page_title="HDCA Admin", page_icon="⚙️", layout="centered")
theme.inject(wide=True)
theme.background_particles()


@st.dialog("⚙️ Admin login")
def _admin_login_dialog():
    st.caption("Separate from the learner Google login — this is the reviewer/admin gate.")
    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

    if submitted:
        expected_user = st.secrets.get("admin", {}).get("username", "admin")
        expected_pass = st.secrets.get("admin", {}).get("password", "admin123")
        if username == expected_user and password == expected_pass:
            st.session_state["admin_authed"] = True
            st.rerun()
        else:
            st.error("Incorrect username or password.")


def require_admin_login():
    if st.session_state.get("admin_authed"):
        return

    theme.top_nav(active="admin", logged_in=False)

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="hdca-eyebrow">HDCA · Admin</div>', unsafe_allow_html=True)
        st.markdown('<div class="hdca-hero-title">Review Console</div>', unsafe_allow_html=True)
        st.write("Sign in to review submissions, walk through each preprocessing stage, approve or reject, and export the class dataset.")
        if st.button("Log in as admin", type="primary"):
            _admin_login_dialog()
    with right:
        theme.admin_illustration()

    st.stop()


def render_submission(idx: int, row: pd.Series, key_prefix: str = ""):
    """key_prefix must be unique per calling tab: st.tabs() renders every
    tab's content in the same script run (only hides inactive ones via
    CSS), so the same row rendered in two tabs needs distinct widget keys."""
    with theme.card():
        st.markdown(
            f"**{row['name']}** &nbsp;·&nbsp; `{row['email']}` &nbsp;·&nbsp; "
            f"label = **{row['label']}** &nbsp;·&nbsp; {theme.status_chip(row['status'])}",
            unsafe_allow_html=True,
        )
        st.caption(str(row.get("timestamp_utc", "")))

        raw_rgba = load_raw_image(row.get("raw_filename"))
        stages_available = raw_rgba is not None
        final_arr = load_processed_image(row["image_filename"])
        if final_arr is None:
            st.error("Processed image for this submission could not be loaded.")
            return

        st.markdown(
            '<div class="hdca-mono">RAW → CROPPED TO INK → FINAL 28×28 (RE-CENTERED)</div>',
            unsafe_allow_html=True,
        )

        step_cols = st.columns(3)

        if stages_available:
            raw_gray = np.array(Image.fromarray(raw_rgba).convert("L"))
            stages = preprocess_with_stages(raw_rgba)

            with step_cols[0]:
                st.image(render_pixel_grid(raw_gray, title=f"Raw · {raw_gray.shape[1]}×{raw_gray.shape[0]}px"), use_container_width=True)
            with step_cols[1]:
                cropped = stages["cropped"]
                st.image(render_pixel_grid(cropped, title=f"Cropped to ink · {cropped.shape[1]}×{cropped.shape[0]}px"), use_container_width=True)
            with step_cols[2]:
                st.image(render_pixel_grid(final_arr, title="Final · 28×28 (re-centered)"), use_container_width=True)
        else:
            st.info(
                "This submission was saved before HDCA started keeping the raw canvas drawing, "
                "so only the final 28×28 result is available — the Raw and Cropped stages can't "
                "be reconstructed. Every new submission now saves all three stages.",
                icon="ℹ️",
            )
            st.image(render_pixel_grid(final_arr, title="Final · 28×28 (re-centered)"), width=340)

        status = row["status"]

        if status == "pending":
            b1, b2, _ = st.columns([1, 1, 3])
            with b1:
                if st.button("✅ Approve", key=f"{key_prefix}approve_{idx}", type="primary"):
                    set_status(idx, "approved")
                    st.rerun()
            with b2:
                if st.button("❌ Reject", key=f"{key_prefix}reject_{idx}"):
                    set_status(idx, "rejected")
                    st.rerun()

        elif status == "approved":
            b1, _ = st.columns([1, 3])
            with b1:
                if st.button("↩️ Reject & ask to resubmit", key=f"{key_prefix}unapprove_{idx}"):
                    set_status(idx, "rejected")
                    st.rerun()
            st.caption(f"Rejecting this frees up digit **{row['label']}** so {row['name']} can redraw it.")

        elif status == "rejected":
            b1, _ = st.columns([1, 3])
            with b1:
                if st.button("✅ Re-approve", key=f"{key_prefix}reapprove_{idx}", type="primary"):
                    set_status(idx, "approved")
                    st.rerun()
            st.caption(f"{row['name']} can now redraw digit **{row['label']}** — it no longer counts toward their progress.")


def render_review_queue(df: pd.DataFrame):
    pending = df[df["status"] == "pending"].sort_values("timestamp_utc")
    st.markdown('<div class="hdca-eyebrow">Pending review</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hdca-hero-title" style="font-size:1.6rem">{len(pending)} submission(s) waiting</div>',
        unsafe_allow_html=True,
    )

    if pending.empty:
        st.info("Nothing pending — every submission has been reviewed.")
        return

    for idx, row in pending.iterrows():
        render_submission(idx, row, key_prefix="rq_")


def render_all_submissions(df: pd.DataFrame):
    st.markdown('<div class="hdca-eyebrow">Every submission</div>', unsafe_allow_html=True)
    st.caption("Reviewed and pending, one below the other — raw drawing through final 28×28.")

    if df.empty:
        st.info("No submissions yet.")
        return

    for idx, row in df.sort_values("timestamp_utc", ascending=False).iterrows():
        render_submission(idx, row, key_prefix="all_")


def render_profile_table(df: pd.DataFrame):
    st.markdown('<div class="hdca-eyebrow">All submissions by profile</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No submissions yet.")
        return

    summary = (
        df.groupby(["name", "email"])
        .agg(
            total=("label", "count"),
            pending=("status", lambda s: (s == "pending").sum()),
            approved=("status", lambda s: (s == "approved").sum()),
            rejected=("status", lambda s: (s == "rejected").sum()),
            digits_covered=("label", lambda s: len(set(s))),
        )
        .reset_index()
        .sort_values("total", ascending=False)
    )

    with theme.card():
        st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown('<div class="hdca-eyebrow">Bulk actions</div>', unsafe_allow_html=True)
    st.caption("Apply one status to every submission from one or more learners at once — each needs a confirm click to avoid accidents.")

    # ---- Multi-select: apply one action to several chosen learners ----
    label_by_email = {prow["email"]: f"{prow['name']} ({prow['email']})" for _, prow in summary.iterrows()}
    all_emails = list(label_by_email.keys())

    with theme.card():
        st.markdown("**Select learners**")

        select_all = st.checkbox("Select all learners", key="bulk_select_all")
        # Checking "select all" pre-fills the multiselect's default; the
        # widget key is bumped so Streamlit treats it as a fresh widget
        # instead of keeping a stale prior selection.
        ms_key = "bulk_multiselect_emails_all" if select_all else "bulk_multiselect_emails_manual"

        narrow_col, _ = st.columns([1, 1.4])
        with narrow_col:
            selected_emails = st.multiselect(
                "Learners",
                options=all_emails,
                default=all_emails if select_all else [],
                format_func=lambda e: label_by_email[e],
                label_visibility="collapsed",
                key=ms_key,
                disabled=select_all,
                placeholder="Search learners…",
            )
        if select_all:
            selected_emails = all_emails
            st.caption(f"All {len(all_emails)} learner(s) selected.")

        if selected_emails:
            ms_cols = st.columns(3)
            ms_actions = [
                ("approved", "✅ Approve selected", "primary", "Approved"),
                ("rejected", "❌ Reject selected", "secondary", "Rejected"),
                ("pending", "↺ Reset selected to pending", "secondary", "Reset"),
            ]
            for (action, label, btn_type, verb), col in zip(ms_actions, ms_cols):
                confirm_key = f"confirm_bulk_ms_{action}"
                with col:
                    if not st.session_state.get(confirm_key):
                        if st.button(label, key=f"bulk_ms_{action}", type=btn_type, use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        if st.button("⚠️ Confirm", key=f"bulk_ms_{action}_confirm", type="primary", use_container_width=True):
                            n = set_status_for_emails(selected_emails, action)
                            st.session_state[confirm_key] = False
                            st.toast(f"{verb} {n} submission(s) across {len(selected_emails)} learner(s).", icon="✅")
                            st.rerun()
                        if st.button("Cancel", key=f"bulk_ms_{action}_cancel", use_container_width=True):
                            st.session_state[confirm_key] = False
                            st.rerun()
        else:
            st.caption("Pick one or more learners above to enable bulk actions on the selection.")

    # ---- Per-learner: only the actions that make sense for their
    # current state. A learner uniformly in one status only needs an
    # undo back to pending; a learner still pending or in a mixed state
    # gets the approve/reject choices instead. Each learner gets its own
    # card (not one shared card) so rows stand out individually, with
    # alternating tint via the .hdca-row-odd/-even marker class below.
    for row_i, (_, prow) in enumerate(summary.iterrows()):
        pname, pemail = prow["name"], prow["email"]
        total, n_pending, n_approved, n_rejected = (
            int(prow["total"]), int(prow["pending"]), int(prow["approved"]), int(prow["rejected"])
        )

        if n_approved == total:
            overall_chip = theme.status_chip("approved")
            actions = [("pending", "↺ Reset to pending (undo)", "secondary", "Reset")]
        elif n_rejected == total:
            overall_chip = theme.status_chip("rejected")
            actions = [("pending", "↺ Reset to pending (undo)", "secondary", "Reset")]
        else:
            overall_chip = theme.status_chip("pending" if n_pending == total else "rejected")
            actions = [
                ("approved", "✅ Approve all", "primary", "Approved"),
                ("rejected", "❌ Reject all", "secondary", "Rejected"),
            ]
            if n_pending != total:
                # mixed state (some approved/rejected already) — a
                # plain reset back to pending is still meaningful here
                actions.append(("pending", "↺ Reset to pending", "secondary", "Reset"))

        row_class = "hdca-row-odd" if row_i % 2 else "hdca-row-even"
        st.markdown(f'<div class="hdca-bulk-row-marker {row_class}"></div>', unsafe_allow_html=True)
        with theme.card():
            st.markdown(
                f"**{pname}** &nbsp;·&nbsp; `{pemail}` &nbsp;·&nbsp; {overall_chip} &nbsp;·&nbsp; "
                f"{total} submitted ({n_approved} approved, {n_pending} pending, {n_rejected} rejected)",
                unsafe_allow_html=True,
            )

            # Always lay out 3 columns (even when fewer actions apply) so
            # a single-button row keeps the same column width as a
            # 3-button row, instead of stretching to fill the whole card.
            cols = st.columns(3)
            for (action, label, btn_type, verb), col in zip(actions, cols):
                confirm_key = f"confirm_bulk_{action}_{pemail}"
                with col:
                    if not st.session_state.get(confirm_key):
                        if st.button(label, key=f"bulk_{action}_{pemail}", type=btn_type, use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        if st.button("⚠️ Confirm", key=f"bulk_{action}_confirm_{pemail}", type="primary", use_container_width=True):
                            n = set_status_for_email(pemail, action)
                            st.session_state[confirm_key] = False
                            # st.success() here would be wiped out by the
                            # immediate rerun below before it's ever seen —
                            # st.toast persists across a rerun, so use that
                            # for feedback instead.
                            st.toast(f"{verb} all {n} submission(s) for {pname}.", icon="✅")
                            st.rerun()
                        if st.button("Cancel", key=f"bulk_{action}_cancel_{pemail}", use_container_width=True):
                            st.session_state[confirm_key] = False
                            st.rerun()

    st.markdown('<div class="hdca-eyebrow">Full submission log</div>', unsafe_allow_html=True)
    with theme.card():
        display_cols = ["timestamp_utc", "name", "email", "label", "status", "image_filename"]
        st.dataframe(df[display_cols].sort_values("timestamp_utc", ascending=False), use_container_width=True, hide_index=True)


def render_export(df: pd.DataFrame):
    st.markdown('<div class="hdca-eyebrow">MNIST-style export</div>', unsafe_allow_html=True)
    approved_count = (df["status"] == "approved").sum()
    st.markdown(
        f'<div class="hdca-hero-title" style="font-size:1.6rem">{approved_count} approved digit(s) ready</div>',
        unsafe_allow_html=True,
    )
    st.caption("One row per digit: label + 784 flattened pixel columns (pixel0…pixel783) — same layout as the classic MNIST CSV.")

    with theme.card():
        if approved_count == 0:
            st.info("Approve some submissions in the review queue first.")
            return

        mnist_df = build_mnist_dataframe(df)
        st.dataframe(mnist_df.head(20), use_container_width=True, height=260)
        st.caption(f"Showing first 20 of {len(mnist_df)} rows · {mnist_df.shape[1]} columns")

        csv_bytes = mnist_df.to_csv(index=False).encode("utf-8")

        excel_buffer = io.BytesIO()
        mnist_df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_bytes = excel_buffer.getvalue()

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download CSV",
                data=csv_bytes,
                file_name="hdca_mnist_dataset.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
        with dl2:
            st.download_button(
                "⬇️ Download Excel",
                data=excel_bytes,
                file_name="hdca_mnist_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )


def main():
    require_admin_login()
    theme.top_nav(active="admin", logged_in=False)

    title_col, logout_col = st.columns([4, 1])
    with title_col:
        st.markdown('<div class="hdca-eyebrow">HDCA · Admin</div>', unsafe_allow_html=True)
        st.markdown('<div class="hdca-hero-title">Review Console</div>', unsafe_allow_html=True)
    with logout_col:
        st.write("")
        if st.button("Log out", type="secondary", use_container_width=True):
            st.session_state["admin_authed"] = False
            st.rerun()

    df = load_all()

    # A plain selector (not st.tabs) so only the active section's content
    # is ever built each run — st.tabs renders every tab's content on every
    # rerun (just hides the inactive ones with CSS), which was re-running
    # matplotlib for every submission's images on every click, in every tab.
    section = st.radio(
        "Section",
        ["🔍 Review queue", "📚 All submissions", "📊 By profile", "⬇️ MNIST export"],
        horizontal=True,
        label_visibility="collapsed",
        key="admin_section",
    )

    if section == "🔍 Review queue":
        render_review_queue(df)
    elif section == "📚 All submissions":
        render_all_submissions(df)
    elif section == "📊 By profile":
        render_profile_table(df)
    else:
        render_export(df)


if __name__ == "__main__":
    main()
