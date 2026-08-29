"""Shared visual theme for HDCA's Streamlit pages: a light, modern
palette plus a custom top nav bar, injected as CSS/HTML. Kept separate
so app.py and admin.py stay visually consistent without duplicating
the stylesheet."""

import streamlit as st

CSS = """
<style>
:root {
  --hdca-bg: #F7F8FC;
  --hdca-panel: #FFFFFF;
  --hdca-card: #FFFFFF;
  --hdca-glass: rgba(255,255,255,.55);
  --hdca-glass-alt: rgba(232,236,247,.55);
  --hdca-glass-line: rgba(255,255,255,.6);
  --hdca-line: #E4E8F2;
  --hdca-signal: #0E9C8F;
  --hdca-signal-2: #3457B2;
  --hdca-warm: #B5710A;
  --hdca-pos: #0E9C8F;
  --hdca-neg: #D1435A;
  --hdca-text: #1B2233;
  --hdca-muted: #616B84;
}

/* Hide Streamlit's native chrome: the header bar, the colored
   decoration stripe beneath it, the auto-generated multipage sidebar
   (User/Admin links live in our own top nav instead), and the footer. */
header[data-testid="stHeader"] { display: none; }
div[data-testid="stDecoration"] { display: none; }
section[data-testid="stSidebar"] { display: none; }
div[data-testid="collapsedControl"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
  background:
    radial-gradient(1100px 560px at 12% -8%, rgba(14,156,143,.10), transparent 60%),
    radial-gradient(900px 520px at 90% 8%, rgba(52,87,178,.10), transparent 55%),
    var(--hdca-bg);
  color: var(--hdca-text);
}

/* Streamlit adds top padding assuming its own header is present;
   compensate since we hid it and use our own nav bar's height instead.
   The content column is centered in the viewport via auto margins,
   so on a wide monitor the drifting-digits background layer shows
   through evenly on both sides instead of leaving a dead void. */
div[data-testid="stAppViewContainer"] > .main .block-container {
  padding-top: 5.5rem; /* clears the fixed top nav bar */
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

/* ---------- animated background: drifting digit particles ---------- */
.hdca-bgfx {
  position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none;
}
.hdca-bgfx span {
  position: absolute; top: -80px;
  font-family: 'Space Grotesk', 'JetBrains Mono', monospace; font-weight: 700;
  background: linear-gradient(180deg, var(--hdca-signal), var(--hdca-signal-2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
  opacity: 0; animation: hdca-drift linear infinite;
}
@keyframes hdca-drift {
  0%   { transform: translateY(0) rotate(-6deg) scale(0.9); opacity: 0; }
  8%   { opacity: 0.16; }
  50%  { transform: translateY(55vh) rotate(8deg) scale(1.05); opacity: 0.12; }
  92%  { opacity: 0.16; }
  100% { transform: translateY(112vh) rotate(-4deg) scale(0.95); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .hdca-bgfx span { animation: none; opacity: 0.08; }
}
/* everything else renders above the background layer */
div[data-testid="stAppViewContainer"], .hdca-nav { position: relative; z-index: 1; }

/* ---------- responsive: phones ---------- */
@media (max-width: 640px) {
  div[data-testid="stAppViewContainer"] > .main .block-container {
    padding-left: .75rem; padding-right: .75rem; padding-top: 6.5rem;
  }
  .hdca-nav-inner { max-width: 100%; padding: 10px 14px; flex-wrap: wrap; gap: 8px; }
  .hdca-nav-brand { font-size: 15px; }
  .hdca-nav-links { order: 3; width: 100%; justify-content: center; }
  .hdca-nav-pill { font-size: 12.5px; padding: 6px 11px; }
  .hdca-nav-user { order: 2; }
  .hdca-nav-name { display: none; } /* avatar only on narrow screens */
  .hdca-hero-title { font-size: 1.6rem; }
  .hdca-card { padding: 16px 16px; }
  div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] { min-width: 42%; }
  .hdca-bgfx { display: none; } /* keep phones focused and battery-friendly */
}

/* ---------- responsive: laptop / tablet mid-range ---------- */
@media (min-width: 641px) and (max-width: 1100px) {
  div[data-testid="stAppViewContainer"] > .main .block-container { max-width: 92%; }
}

body, .stApp, p, span, label, div { color: var(--hdca-text); }

/* Buttons set their own text color (white on gradient primary buttons,
   dark on white secondary buttons) — the blanket rule above would
   otherwise force every button's inner label back to dark text. */
div[data-testid="stButton"] > button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] *,
div[data-testid="stDownloadButton"] > button[kind="primary"] *,
div[data-testid="stDownloadButton"] > button[kind="primaryFormSubmit"] * {
  color: #FFFFFF !important;
}
div[data-testid="stButton"] > button[kind="secondary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="secondary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="secondaryFormSubmit"] *,
div[data-testid="stDownloadButton"] > button[kind="secondary"] *,
div[data-testid="stDownloadButton"] > button[kind="secondaryFormSubmit"] * {
  color: var(--hdca-text) !important;
}

h1, h2, h3 { font-family: 'Space Grotesk', 'Inter', sans-serif !important; letter-spacing: -.01em; color: var(--hdca-text) !important; }
.hdca-eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .28em;
  text-transform: uppercase; color: var(--hdca-signal); margin-bottom: 6px;
}
.hdca-hero-title {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2.2rem;
  background: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
  margin-bottom: .3rem;
}

.hdca-card {
  background: var(--hdca-glass);
  backdrop-filter: blur(14px) saturate(140%);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
  border: 1px solid var(--hdca-glass-line); border-radius: 16px; padding: 22px 24px; margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(20,30,60,.03), 0 8px 24px rgba(20,30,60,.06);
}
/* theme.card() uses Streamlit's own bordered container (st.container(border=True))
   so every child widget genuinely nests inside one real DOM node, instead of
   the old markdown-open/markdown-close pair that rendered as an empty floating
   card with no content inside it. Re-skin Streamlit's default grey border with
   a frosted-glass look: translucent fill + backdrop blur, so the drifting
   background particles/gradient show through softly instead of a flat white card.

   NOTE: this Streamlit build has NO "stVerticalBlockBorderWrapper" testid —
   confirmed by inspecting the live DOM. A bordered container is just the
   ordinary "stVerticalBlock" testid (shared with every other block, bordered
   or not) whose direct parent carries "stLayoutWrapper" — that parent only
   wraps actual st.container(...) calls, so it's the reliable way to select
   only real cards without also catching every plain layout block. */
div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
  background: var(--hdca-glass) !important;
  backdrop-filter: blur(14px) saturate(140%);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
  border: 1px solid var(--hdca-glass-line) !important;
  border-radius: 16px !important;
  box-shadow: 0 1px 2px rgba(20,30,60,.03), 0 8px 24px rgba(20,30,60,.06);
  margin-bottom: 12px;
}

/* Bulk-actions per-learner rows: a hidden marker div rendered right
   before each learner's card is used to alternate its glass tint,
   since Streamlit gives theme.card() no class hook of its own. The
   marker sits in the immediately-preceding element container, so the
   adjacent-sibling selector reaches the real card wrapper right after it. */
.hdca-bulk-row-marker { display: none; }
div[data-testid="stElementContainer"]:has(> .hdca-bulk-row-marker.hdca-row-odd) + div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
  background: var(--hdca-glass-alt) !important;
  border-left: 3px solid var(--hdca-signal) !important;
}
div[data-testid="stElementContainer"]:has(> .hdca-bulk-row-marker.hdca-row-even) + div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
  border-left: 3px solid var(--hdca-signal-2) !important;
}

.hdca-chip {
  display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 11.5px;
  padding: 3px 10px; border-radius: 20px; border: 1px solid var(--hdca-line);
  color: var(--hdca-muted); margin-right: 6px;
}
.hdca-chip.status-pending { color: var(--hdca-warm); border-color: rgba(181,113,10,.35); background: rgba(181,113,10,.06); }
.hdca-chip.status-approved { color: var(--hdca-pos); border-color: rgba(14,156,143,.35); background: rgba(14,156,143,.06); }
.hdca-chip.status-rejected { color: var(--hdca-neg); border-color: rgba(209,67,90,.35); background: rgba(209,67,90,.06); }

div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
div[data-testid="stDownloadButton"] > button[kind="primary"],
div[data-testid="stDownloadButton"] > button[kind="primaryFormSubmit"] {
  background: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2)) !important;
  color: #FFFFFF !important; border: none !important; font-weight: 700;
}
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
div[data-testid="stDownloadButton"] > button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] > button[kind="primaryFormSubmit"]:hover {
  box-shadow: 0 8px 22px rgba(14,156,143,.24); transform: translateY(-1px);
}
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stFormSubmitButton"] > button[kind="secondary"],
div[data-testid="stFormSubmitButton"] > button[kind="secondaryFormSubmit"],
div[data-testid="stDownloadButton"] > button[kind="secondary"],
div[data-testid="stDownloadButton"] > button[kind="secondaryFormSubmit"] {
  background: #FFFFFF !important; border: 1px solid var(--hdca-line) !important; color: var(--hdca-text) !important;
}

/* Buttons rendered together via st.columns should read as one row —
   equal height/width regardless of label length or column count. */
div[data-testid="stButton"] > button {
  width: 100%;
  min-height: 40px;
}

/* st.multiselect's selected-item pills default to Streamlit's native
   red; re-skin them (and the dropdown menu on open) to the theme. */
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background-color: var(--hdca-signal-2) !important;
  border-color: var(--hdca-signal-2) !important;
  color: #FFFFFF !important;
}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
}
div[data-testid="stMultiSelect"] > div > div {
  border-color: var(--hdca-line) !important;
}
div[data-testid="stMultiSelect"] > div > div:focus-within {
  border-color: var(--hdca-signal) !important;
  box-shadow: 0 0 0 1px var(--hdca-signal) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"],
ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
  background-color: rgba(14,156,143,.10) !important;
}

/* ---------- modal dialogs (st.dialog) ---------- */
div[data-testid="stDialog"] div[role="dialog"] {
  background: var(--hdca-panel); border-radius: 16px;
}
div[data-testid="stDialog"] h1, div[data-testid="stDialog"] h2, div[data-testid="stDialog"] h3 {
  font-family: 'Space Grotesk', sans-serif !important;
}

/* Streamlit's real progress bar markup (confirmed from the shipped
   ProgressBar.*.js source, not guessed): stProgress > ... >
   div[data-testid="stProgressBarTrack"] > div (fill — always 100%
   width, revealed via an inline translateX transform, not a width
   change). Target the stable testid directly instead of guessing
   nesting depth, which is what produced the doubled/flat-grey bar. */
div[data-testid="stProgress"] { background: transparent; margin: 4px 0 18px; }
div[data-testid="stProgressBarTrack"] {
  background-color: var(--hdca-line) !important;
  border-radius: 20px !important;
  overflow: hidden;
  height: 10px !important;
}
div[data-testid="stProgressBarTrack"] > div {
  background-color: transparent !important;
  background-image: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2)) !important;
  border-radius: 20px;
  height: 100%;
}

canvas { border-radius: 12px; border: 1px solid var(--hdca-line); max-width: 100%; }
div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] canvas { display: block; margin: 0 auto; }

.hdca-mono { font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: var(--hdca-muted); }

.hdca-disclaimer {
  background: rgba(52,87,178,.05); border: 1px solid var(--hdca-line);
  border-left: 3px solid var(--hdca-signal-2); border-radius: 0 12px 12px 0;
  padding: 14px 18px; font-size: 13.5px; color: var(--hdca-muted); margin: 18px 0;
}
.hdca-disclaimer b { color: var(--hdca-text); }

/* ---------- top nav bar ----------
   Full-bleed bar spanning the entire viewport width, independent of
   Streamlit's centered block-container; its inner row is capped and
   centered to line up with the page content below it. */
.hdca-nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 999;
  background: var(--hdca-panel); border-bottom: 1px solid var(--hdca-line);
}
.hdca-nav-inner {
  display: flex; align-items: center; justify-content: space-between;
  max-width: 900px; margin: 0 auto; padding: 14px 26px;
}
.hdca-nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 17px; color: var(--hdca-text);
}
.hdca-nav-brand .dot {
  width: 12px; height: 12px; border-radius: 50%;
  background: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2));
}
.hdca-nav-links { display: flex; align-items: center; gap: 8px; }
.hdca-nav-pill, .hdca-nav-pill:link, .hdca-nav-pill:visited, .hdca-nav-pill:hover, .hdca-nav-pill:active {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Inter', sans-serif; font-size: 13.5px; font-weight: 600;
  padding: 7px 14px; border-radius: 20px; text-decoration: none !important;
  border: 1px solid var(--hdca-line); color: var(--hdca-muted);
}
.hdca-nav-pill.active, .hdca-nav-pill.active:link, .hdca-nav-pill.active:visited {
  background: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2));
  color: #FFFFFF !important; border-color: transparent;
}
.hdca-nav-user { display: flex; align-items: center; gap: 8px; }
.hdca-avatar {
  width: 30px; height: 30px; border-radius: 50%; object-fit: cover;
  border: 1.5px solid var(--hdca-line);
}
.hdca-avatar-fallback {
  width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(90deg, var(--hdca-signal), var(--hdca-signal-2));
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 13px;
}
.hdca-nav-name { font-size: 13.5px; font-weight: 600; color: var(--hdca-text); }
</style>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
"""

HERO_SVG = """
<svg viewBox="0 0 340 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A hand writing a digit on paper, next to a small grid representing the processed 28 by 28 output" style="width:100%;max-width:340px;height:auto">
  <defs>
    <linearGradient id="hdcaGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0E9C8F"/>
      <stop offset="100%" stop-color="#3457B2"/>
    </linearGradient>
  </defs>
  <rect x="14" y="18" width="150" height="140" rx="10" fill="#FFFFFF" stroke="#E4E8F2" stroke-width="2"/>
  <path d="M70 55 C90 45, 110 45, 120 65 C130 88, 95 95, 85 110 C78 120, 100 122, 118 112"
        fill="none" stroke="url(#hdcaGrad)" stroke-width="7" stroke-linecap="round"/>
  <path d="M148 118 l26 26 M172 116 l-24 28" stroke="#B5710A" stroke-width="7" stroke-linecap="round"/>
  <g transform="translate(198,42)">
    <rect width="128" height="128" rx="10" fill="#FFFFFF" stroke="#E4E8F2" stroke-width="2"/>
    <g fill="none" stroke="#E4E8F2" stroke-width="1">
      <line x1="16" y1="0" x2="16" y2="128"/><line x1="32" y1="0" x2="32" y2="128"/>
      <line x1="48" y1="0" x2="48" y2="128"/><line x1="64" y1="0" x2="64" y2="128"/>
      <line x1="80" y1="0" x2="80" y2="128"/><line x1="96" y1="0" x2="96" y2="128"/>
      <line x1="112" y1="0" x2="112" y2="128"/>
      <line x1="0" y1="16" x2="128" y2="16"/><line x1="0" y1="32" x2="128" y2="32"/>
      <line x1="0" y1="48" x2="128" y2="48"/><line x1="0" y1="64" x2="128" y2="64"/>
      <line x1="0" y1="80" x2="128" y2="80"/><line x1="0" y1="96" x2="128" y2="96"/>
      <line x1="0" y1="112" x2="128" y2="112"/>
    </g>
    <path d="M40 28 C58 22, 76 24, 82 40 C88 58, 62 62, 54 74 C48 84, 68 86, 88 76"
          fill="none" stroke="url(#hdcaGrad)" stroke-width="9" stroke-linecap="round"/>
  </g>
  <path d="M172 92 q10 -6 20 0" fill="none" stroke="#0E9C8F" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
  <path d="M172 100 q10 -4 20 2" fill="none" stroke="#3457B2" stroke-width="3" stroke-linecap="round" opacity="0.5"/>
</svg>
"""

ADMIN_SVG = """
<svg viewBox="0 0 340 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A shield with a checkmark reviewing a stack of digit cards, one approved and one rejected" style="width:100%;max-width:340px;height:auto">
  <defs>
    <linearGradient id="hdcaGradAdmin" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0E9C8F"/>
      <stop offset="100%" stop-color="#3457B2"/>
    </linearGradient>
  </defs>
  <g transform="translate(18,20)">
    <path d="M60 0 L114 18 V64 C114 100 88 122 60 132 C32 122 6 100 6 64 V18 Z"
          fill="#FFFFFF" stroke="url(#hdcaGradAdmin)" stroke-width="4"/>
    <path d="M36 66 L52 82 L86 44" fill="none" stroke="url(#hdcaGradAdmin)" stroke-width="8"
          stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="60" cy="66" r="52" fill="url(#hdcaGradAdmin)" opacity="0.08"/>
  </g>
  <g transform="translate(158,26)">
    <rect width="80" height="94" rx="10" fill="#FFFFFF" stroke="#E4E8F2" stroke-width="2"/>
    <rect x="10" y="12" width="60" height="8" rx="3" fill="#E4E8F2"/>
    <rect x="10" y="26" width="40" height="8" rx="3" fill="#E4E8F2"/>
    <path d="M18 58 l10 10 l24 -26" fill="none" stroke="#0E9C8F" stroke-width="6"
          stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="40" cy="80" r="3" fill="#0E9C8F"/>
  </g>
  <g transform="translate(250,60)">
    <rect width="80" height="94" rx="10" fill="#FFFFFF" stroke="#E4E8F2" stroke-width="2"/>
    <rect x="10" y="12" width="60" height="8" rx="3" fill="#E4E8F2"/>
    <rect x="10" y="26" width="40" height="8" rx="3" fill="#E4E8F2"/>
    <path d="M22 58 l24 24 M46 58 l-24 24" stroke="#D1435A" stroke-width="6" stroke-linecap="round"/>
  </g>
</svg>
"""

DONE_SVG = """
<svg viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A checkmark next to a completed grid of ten digits" style="width:100%;max-width:220px;height:auto;display:block;margin:0 auto">
  <defs>
    <linearGradient id="hdcaGradDone" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0E9C8F"/>
      <stop offset="100%" stop-color="#3457B2"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="62" r="52" fill="url(#hdcaGradDone)" opacity="0.12"/>
  <circle cx="100" cy="62" r="38" fill="none" stroke="url(#hdcaGradDone)" stroke-width="5"/>
  <path d="M82 62 l13 13 l24 -28" fill="none" stroke="url(#hdcaGradDone)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="100" y="128" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-weight="700" font-size="15" fill="#1B2233">All 10 digits collected</text>
</svg>
"""


def inject(wide: bool = False):
    """Inject the shared stylesheet. Pass wide=True on pages (like
    Admin) that need more horizontal room for tables and image rows —
    content still centers with equal margins on both sides."""
    st.markdown(CSS, unsafe_allow_html=True)
    if wide:
        # Content can be wider (tables, image rows need the room), but
        # the nav bar itself is intentionally NOT widened here — it
        # stays a fixed 900px on every page so it never visibly shifts
        # width when navigating between the learner app and Admin.
        st.markdown(
            """<style>
            div[data-testid="stAppViewContainer"] > .main .block-container { max-width: 1200px; }
            </style>""",
            unsafe_allow_html=True,
        )


def card():
    """A real Streamlit bordered container themed as an .hdca-card.
    Unlike the old card_open()/card_close() pair — which emitted two
    independent st.markdown() HTML fragments that the browser
    auto-closed on their own, rendering an empty floating card with
    none of the intended content actually inside it — this wraps every
    child widget inside one real DOM node (Streamlit's own bordered
    container), which the CSS in `inject()` themes globally. Use as
    `with theme.card():`."""
    return st.container(border=True)


def status_chip(status: str) -> str:
    return f'<span class="hdca-chip status-{status}">{status}</span>'


def hero_illustration():
    st.markdown(HERO_SVG, unsafe_allow_html=True)


def admin_illustration():
    st.markdown(ADMIN_SVG, unsafe_allow_html=True)


def completion_illustration():
    st.markdown(DONE_SVG, unsafe_allow_html=True)


def disclaimer():
    st.markdown(
        """<div class="hdca-disclaimer">
        <b>About this activity:</b> You're contributing to a Deep Learning
        Modelling exercise, building an MNIST-style handwritten digit
        dataset as part of a live training session.<br><br>
        <b>Data use:</b> Your name, email, and drawn digits are stored
        locally for this class only and used solely for academic and
        training purposes — building and evaluating a digit-recognition
        model together. Your data is not shared, sold, or used for any
        purpose outside this learning activity.
        </div>""",
        unsafe_allow_html=True,
    )


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def top_nav(active: str, user_name: str | None = None, user_picture: str | None = None, logged_in: bool = False):
    """Custom horizontal nav bar with User/Admin pills and, when a
    learner is logged in, their Google avatar + name on the right."""
    if logged_in and user_name:
        initials = _initials(user_name)
        if user_picture:
            # Google's avatar URL can occasionally fail to load (expired
            # token, network policy, etc.) — onerror swaps in the
            # initials fallback instead of a broken-image icon.
            avatar_html = (
                f'<img class="hdca-avatar" src="{user_picture}" alt="{user_name}" '
                f"onerror=\"this.outerHTML='<div class=&quot;hdca-avatar-fallback&quot;>{initials}</div>'\">"
            )
        else:
            avatar_html = f'<div class="hdca-avatar-fallback">{initials}</div>'
        user_html = f'<div class="hdca-nav-user">{avatar_html}<span class="hdca-nav-name">{user_name}</span></div>'
    else:
        user_html = ""

    user_pill_class = "hdca-nav-pill active" if active == "user" else "hdca-nav-pill"
    admin_pill_class = "hdca-nav-pill active" if active == "admin" else "hdca-nav-pill"

    st.markdown(
        f"""
        <div class="hdca-nav">
          <div class="hdca-nav-inner">
            <div class="hdca-nav-brand"><span class="dot"></span>HDCA</div>
            <div class="hdca-nav-links">
              <a class="{user_pill_class}" href="/" target="_self">✍️ User</a>
              <a class="{admin_pill_class}" href="/Admin" target="_self">⚙️ Admin</a>
            </div>
            {user_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_DIGIT_PARTICLES = [
    (3, "4%", 52, "0s", "24s"), (7, "12%", 68, "4s", "29s"), (2, "20%", 44, "9s", "21s"),
    (9, "29%", 74, "1s", "33s"), (5, "38%", 56, "6s", "26s"), (1, "47%", 64, "11s", "30s"),
    (6, "56%", 46, "3s", "23s"), (4, "65%", 72, "8s", "31s"), (0, "74%", 50, "5s", "25s"),
    (8, "82%", 66, "10s", "28s"), (3, "90%", 42, "2s", "22s"), (7, "97%", 58, "7s", "27s"),
]


def background_particles():
    """A fixed-position layer of slowly drifting, low-opacity digit
    characters — fills empty space on wide screens without competing
    with foreground content. Hidden on phones (see the CSS media query)."""
    spans = "".join(
        f'<span style="left:{left};font-size:{size}px;'
        f'animation-duration:{dur};animation-delay:{delay}">{digit}</span>'
        for digit, left, size, delay, dur in _DIGIT_PARTICLES
    )
    st.markdown(f'<div class="hdca-bgfx" aria-hidden="true">{spans}</div>', unsafe_allow_html=True)
