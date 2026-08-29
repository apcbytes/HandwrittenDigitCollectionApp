# Session 1 — Auth & App Skeleton

**Goal:** A Streamlit app that requires Google login before showing
any content, and displays the logged-in user's name/email.

**Duration:** ~60-75 min

---

## 1. Vibe-code first (~15 min)

Prompt (say this out loud, type it live, let the AI generate):

> "Create a Streamlit app called app.py that shows a title 'Handwritten
> Digit Collector', requires the user to log in before seeing anything
> else, and shows their name and email in the sidebar after login."

Expect the AI to either invent a fake login form OR (if it knows
Streamlit 1.42+) reach for `st.login()`. Either result is a good
discussion point: **"is this actually checking who you are, or just
asking you to type a name?"**

## 2. Read & break it down (~10 min)

Ask the class:
- What's the difference between a login *form* and login *auth*?
- If this were a form, could I type in someone else's email and
  contribute digits under their name? (Yes — that's the vulnerability
  a form-based approach can't avoid without real identity verification.)
- This is why we need **OAuth**: Google verifies identity, and hands
  our app a token proving it, without our app ever seeing the password.

## 3. Hand-code the core concept (~30 min)

### Step 3a — the login gate

Type this together, explaining each line:

```python
import streamlit as st

def require_login():
    if not st.user.is_logged_in:
        st.title("✍️ Handwritten Digit Collector")
        st.write("Sign up with Google to start contributing handwritten digits.")
        st.button("Log in with Google", on_click=st.login, args=("google",))
        st.stop()   # <-- critical: halts execution here for logged-out users
```

**Teaching point on `st.stop()`:** Streamlit re-runs your *entire*
script top-to-bottom on every interaction. Without `st.stop()`, code
below this function would still execute even for a logged-out user.
This is a common source of bugs for learners new to Streamlit's
execution model — worth pausing on.

### Step 3b — what `st.user` actually is

Explain: after Google's OAuth redirect completes, Streamlit populates
`st.user` with claims from Google's ID token — `st.user.name`,
`st.user.email`, `st.user.is_logged_in`. This is **not** stored by our
app; it's re-verified by Streamlit's OIDC handling on each session.

### Step 3c — sidebar profile + logout

```python
def show_sidebar_profile():
    with st.sidebar:
        st.subheader("Your profile")
        st.write(f"**Name:** {st.user.name}")
        st.write(f"**Email:** {st.user.email}")
        st.button("Log out", on_click=st.logout)
```

### Step 3d — wire it together

```python
def main():
    require_login()
    show_sidebar_profile()
    st.title("✍️ Handwritten Digit Collector")
    st.write(f"Welcome, {st.user.name}! (Canvas coming in Session 2)")

if __name__ == "__main__":
    main()
```

## 4. Reconcile & test (~15 min)

Run it:

```bash
streamlit run app.py
```

**Requires `.streamlit/secrets.toml` to be filled in** (see
`course/SETUP.md`). If a learner's OAuth isn't ready yet, pair them
with someone whose credentials work, or use the fallback below.

### Fallback: no-OAuth stand-in (only if credentials aren't ready)

```python
# TEMPORARY — replace with real st.login() once secrets.toml is ready
class FakeUser:
    is_logged_in = True
    name = "Demo Learner"
    email = "demo@example.com"
st.user = FakeUser()
```

Flag clearly in class that this is a stand-in, not a security pattern
— revisit and remove once real OAuth works.

## Checkpoint

- [ ] `streamlit run app.py` shows a Google login button
- [ ] After logging in, sidebar shows real name + email
- [ ] Logging out returns to the login button
- [ ] Group can explain: what does `st.stop()` do and why is it needed here?
