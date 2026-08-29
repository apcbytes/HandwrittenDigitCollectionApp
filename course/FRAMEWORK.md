# HDCA Live-Build Framework — Instructor Overview

**App:** Handwritten Digit Collector App (HDCA) — Streamlit app where
learners sign in with Google, then draw digits 0-9 which get
preprocessed MNIST-style (cropped, scaled, centered by mass into
28x28) and saved as PNG + logged to Excel with name/email/label.

## Teaching philosophy: vibe-code the skeleton, hand-code the concepts

Every session follows the same rhythm:

1. **Vibe-code first (~10-15 min).** Prompt an AI assistant live to
   generate a rough version of the session's feature. This shows
   learners the "fast path" and gives everyone a working baseline fast
   — momentum matters in a live class.
2. **Read & break it down (~10 min).** As a group, read the generated
   code line by line. Ask "what would happen if we removed this line?"
   Identify the 2-3 lines doing the *real* conceptual work.
3. **Hand-code the core concept (~20-30 min).** Close the AI tool.
   Type the core logic together from scratch, explaining the *why*
   at each step (this is where preprocess.py's centering math, the
   OAuth flow, etc. live). This is the part that actually teaches.
4. **Reconcile & test (~10-15 min).** Compare the hand-coded version
   to the vibe-coded draft. Run it. Fix bugs together live — this is
   valuable, don't pre-fix everything.

## Session map

| # | Title | Vibe-coded | Hand-coded (the teaching core) |
|---|-------|-----------|-------------------------------|
| 1 | Auth & Skeleton | Streamlit app shell, page layout | Google OAuth flow, session state, why login gates matter |
| 2 | Canvas & Capture | Canvas component wiring | RGBA array structure, what a "drawing" is as data |
| 3 | Preprocessing Pipeline | — (this session IS hand-coded) | Bounding-box crop, aspect-preserving scale, center-of-mass shift — the actual MNIST recipe |
| 4 | Storage & Data Flow | Excel append logic | File naming, idempotency, why atomic writes matter, data schema design |
| 5 (optional) | Extension: Train a Model | Model training script | Loading the dataset back, train/test split, a simple classifier — closing the loop |

Each session has its own file: `session_01.md` ... `session_05.md`.

## Ground rules for the live room

- **Everyone commits their own OAuth secrets locally** — never share
  `secrets.toml` on a shared screen while a real client_secret is visible.
- **Run `streamlit run app.py` after every session** — a session isn't
  done until the app runs end-to-end with the new feature.
- Keep a **"parking lot"** on the whiteboard for tangents (e.g. "what
  about touchscreens?", "what if two people have the same email?") —
  acknowledge, defer, keep momentum.
- Session 3 (preprocessing) is the conceptual heart of the course —
  don't compress it if you're running short on time elsewhere.

## What "done" looks like after Session 4

A learner can: log in with their Google account, get prompted to draw
digit 0, draw it, hit submit, see a 28x28 preview, and watch the
progress bar advance. After all 10 digits, `data/labels.xlsx` has 10
rows for their email, and `data/images/` has 10 correctly-labeled PNGs.
