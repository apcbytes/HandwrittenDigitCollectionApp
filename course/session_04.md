# Session 4 — Storage & Data Flow

**Goal:** Save each processed digit as a PNG and log a labeled row
(name, email, digit label, filename) to an Excel file, with the guided
0→9 collection flow wired end-to-end in `app.py`.

**Duration:** ~60-75 min

---

## 1. Vibe-code first (~15 min)

Prompt:

> "Write a function that saves a 28x28 numpy array as a PNG file and
> appends a row (name, email, label, filename) to an Excel file using
> pandas, creating the file if it doesn't exist."

This usually produces something *close* but with subtle issues worth
inspecting: does it handle the "file doesn't exist yet" case? Does it
create unique filenames (or will the second submission overwrite the
first)? Does it handle unsafe characters in the email (e.g. `@`, `.`)
if used in a filename?

## 2. Read & break it down (~10 min)

Ask the class to stress-test the generated code out loud:
- "What happens if two learners submit at the *exact same second*?"
- "What if my email is `a.b+test@example.com` — is that a safe filename?"
- "What happens on the 2nd, 3rd... submission — does the Excel file grow, or get overwritten?"

## 3. Hand-code the core concept (~30 min)

### Step 3a — safe, unique filenames

```python
import os
from datetime import datetime, timezone

def _safe_slug(text: str) -> str:
    keep = "-_."
    return "".join(c if c.isalnum() or c in keep else "_" for c in text)

def make_filename(email: str, label: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{_safe_slug(email)}_{label}_{ts}.png"
```

**Discuss:** why microsecond-precision timestamp in the filename
instead of just `email_label.png`? (So a learner can redo/re-submit
the same digit without silently overwriting their earlier attempt —
useful if they want to try again for quality.)

### Step 3b — append-or-create pattern for the Excel log

```python
import pandas as pd

LOG_PATH = "data/labels.xlsx"
LOG_COLUMNS = ["timestamp_utc", "name", "email", "label", "image_filename"]

def append_row(row: dict):
    if os.path.exists(LOG_PATH):
        df = pd.read_excel(LOG_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row], columns=LOG_COLUMNS)
    df.to_excel(LOG_PATH, index=False)
```

**Discuss the tradeoff explicitly:** this reads and rewrites the
*entire* Excel file on every single submission. Ask: "is that a
problem?" (Not at classroom scale — tens to low hundreds of rows. At
real MNIST scale — 70,000 rows — this pattern would be far too slow;
you'd want a database or an append-only format like CSV/Parquet
instead.) This is a good moment to talk about **premature
optimization**: correct-and-simple now, revisit if it ever becomes a
bottleneck.

### Step 3c — tracking progress per learner (drives the 0→9 flow)

```python
def load_progress(email: str) -> set[int]:
    if not os.path.exists(LOG_PATH):
        return set()
    df = pd.read_excel(LOG_PATH)
    mine = df[df["email"] == email]
    return set(mine["label"].astype(int).tolist())
```

**Discuss:** this makes the app *stateless* across restarts — a
learner can close the browser and come back, and the app resumes
where they left off by reading the log, not by keeping anything in
memory. Ask: "why is this better than storing progress in
`st.session_state`?" (Session state resets on refresh/restart; the
Excel file is durable.)

### Step 3d — wire the guided sequence into app.py

```python
DIGIT_SEQUENCE = list(range(10))

def next_digit_to_collect(email: str):
    done = load_progress(email)
    for d in DIGIT_SEQUENCE:
        if d not in done:
            return d
    return None  # all done
```

Walk through how this combines with Session 1's login and Session
2/3's canvas+preprocessing to form the full submit handler:

```python
if submit:
    processed = to_mnist_28x28(canvas_result.image_data)
    if processed is None:
        st.warning("Canvas looks empty — please draw the digit first.")
    else:
        filename = save_sample(name, email, target, processed)
        st.success(f"Saved digit '{target}' as {filename}")
        st.rerun()   # refresh so next_digit_to_collect() picks the next digit
```

**Discuss `st.rerun()`:** ties back to Session 1's lesson about
Streamlit's rerun model — after saving, we force a rerun so the
progress bar and "please draw X" prompt update to the next digit.

## 4. Reconcile & test (~15-20 min)

Full end-to-end test as a class:
1. Log in.
2. Draw and submit digit 0 → confirm PNG appears in `data/images/`
   and a row appears in `data/labels.xlsx`.
3. Submit digits 1-9.
4. Confirm the "all 10 collected" success message + balloons appears.
5. Open `data/labels.xlsx` together — confirm every row has correct
   name, email, and label matching what was drawn.
6. Bonus: have two learners run the app against a **shared** `data/`
   folder (copy files between machines, or use a shared drive) and
   discuss what would break (the whole-file rewrite race condition
   from 3b) — sets up a natural "how would you fix this for real
   production use?" discussion.

## Checkpoint

- [ ] Every submission creates one PNG + one Excel row, correctly labeled
- [ ] Progress bar and "next digit" prompt correctly resume after refresh
- [ ] Group can explain the read-modify-write race condition risk in `append_row`
- [ ] Full app runs start-to-finish: login → 10 digits → completion screen
