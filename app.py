import streamlit as st
from streamlit_drawable_canvas import st_canvas

import theme
from preprocess import to_mnist_28x28
from storage import save_sample, load_progress, resubmit_attempt_number

st.set_page_config(page_title="Handwritten Digit Collector", page_icon="✍️", layout="centered")
theme.inject()
theme.background_particles()

DIGIT_SEQUENCE = list(range(10))  # 0..9


def require_login():
    """Google login gate using Streamlit's native OIDC support.
    Needs [auth] / [auth.google] config in .streamlit/secrets.toml (see course/SETUP.md)."""
    if not st.user.is_logged_in:
        theme.top_nav(active="user", logged_in=False)

        left, right = st.columns([1.3, 1])
        with left:
            st.markdown('<div class="hdca-eyebrow">HDCA · Live Build</div>', unsafe_allow_html=True)
            st.markdown('<div class="hdca-hero-title">Handwritten Digit Collector</div>', unsafe_allow_html=True)
            st.write("Sign up with Google to start contributing handwritten digits — from 0 through 9.")
            st.button("Log in with Google", on_click=st.login, args=("google",), type="primary")
        with right:
            theme.hero_illustration()

        theme.disclaimer()
        st.stop()


def next_digit_to_collect(email: str) -> int | None:
    done = load_progress(email)
    for d in DIGIT_SEQUENCE:
        if d not in done:
            return d
    return None  # all 10 collected


def main():
    require_login()

    name = st.user.name
    email = st.user.email
    picture = getattr(st.user, "picture", None)

    theme.top_nav(active="user", user_name=name, user_picture=picture, logged_in=True)

    done = load_progress(email)
    target = next_digit_to_collect(email)

    title_col, logout_col = st.columns([4, 1])
    with title_col:
        st.markdown('<div class="hdca-eyebrow">HDCA · Live Build</div>', unsafe_allow_html=True)
        st.markdown('<div class="hdca-hero-title">Handwritten Digit Collector</div>', unsafe_allow_html=True)
    with logout_col:
        st.write("")
        if st.button("Log out", type="secondary", use_container_width=True):
            st.logout()

    # st.progress(text=...) draws its caption tightly stacked on the bar
    # with no reliable CSS hook to add spacing, so the label is rendered
    # separately, in normal document flow, above a bare progress bar.
    st.caption(f"{len(done)}/10 digits contributed")
    st.progress(len(done) / 10)

    if target is None:
        with theme.card():
            theme.completion_illustration()
            st.markdown(
                "<p style='text-align:center;color:var(--hdca-muted);margin-top:8px'>"
                "Thank you for contributing! Your submissions are now waiting for admin review."
                "</p>",
                unsafe_allow_html=True,
            )
        return

    attempt = resubmit_attempt_number(email, target)

    with theme.card():
        st.subheader(f"Please draw the digit: **{target}**")
        if attempt > 0:
            st.caption("This digit was sent back by review — please redraw it.")
        st.caption("Draw large and centered — it will be auto-cropped, scaled, and centered to 28×28.")

        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 1)",
            stroke_width=18,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=280,
            width=280,
            drawing_mode="freedraw",
            key=f"canvas_{target}_{attempt}",
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            submit = st.button("Submit digit", type="primary", use_container_width=True)
        with col2:
            st.caption("Nothing is saved until you click Submit.")

    if submit:
        if canvas_result.image_data is None:
            st.warning("Please draw something first.")
            return

        processed = to_mnist_28x28(canvas_result.image_data)
        if processed is None:
            st.warning("Canvas looks empty — please draw the digit first.")
            return

        filename = save_sample(name, email, target, processed, canvas_result.image_data)

        st.success(f"Saved digit '{target}' — pending admin review.")
        preview_col, _ = st.columns(2)
        with preview_col:
            st.image(processed, caption="28×28 preprocessed preview", width=140)

        st.rerun()


if __name__ == "__main__":
    main()
