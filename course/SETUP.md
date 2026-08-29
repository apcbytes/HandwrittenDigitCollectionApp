# Pre-Class Setup (do this BEFORE Session 1)

This must happen before learners arrive, since Google OAuth credentials
take a few minutes to provision and can't be rushed live.

## 1. Python environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Google OAuth credentials (needed for Session 1)

Streamlit's native `st.login()` needs a Google OAuth Client ID.

1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new project (or reuse one).
3. Click **Create Credentials > OAuth client ID**.
   - Application type: **Web application**
   - Authorized redirect URI: `http://localhost:8501/oauth2callback`
4. Copy the generated **Client ID** and **Client Secret**.
5. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   and paste in your client_id/client_secret. Generate a random
   `cookie_secret` (any long random string, e.g. `python -c "import secrets; print(secrets.token_hex(32))"`).

**Classroom option:** if setting up individual Google Cloud OAuth apps
per learner is too much overhead, you (the instructor) can:
- Provision ONE shared OAuth client for the class, with each learner's
  `localhost:8501` redirect added (OAuth allows multiple redirect URIs), OR
- Use the "Simple form" fallback for Session 1 only (see `course/session_01.md`)
  and upgrade to real OAuth once credentials are ready.

## 3. Verify the app runs

```bash
streamlit run app.py
```

You should see a Google login button. Don't worry if it errors before
secrets.toml is filled in — that's expected until step 2 is done.

## 4. Folder structure learners will build

```
HandwrittenDigitCollectionApp/
├── app.py              # main Streamlit app (UI + flow control)
├── preprocess.py        # MNIST-style image preprocessing pipeline
├── storage.py            # save image + append Excel row
├── requirements.txt
├── .streamlit/
│   └── secrets.toml      # Google OAuth credentials (gitignored)
├── data/
│   ├── images/            # saved 28x28 PNGs
│   └── labels.xlsx        # one row per contributed digit
└── course/                # this training guide
```
