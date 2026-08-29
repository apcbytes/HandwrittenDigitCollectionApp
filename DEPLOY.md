# Deploying HDCA to Streamlit Community Cloud

Streamlit Community Cloud runs the app on a container with an **ephemeral
filesystem** — anything written under `data/` is lost on every restart,
sleep/wake, or redeploy. So the disk backend in `storage_disk.py` is for
local development only. In the cloud the app uses `storage_cloud.py`,
which keeps:

* the **submissions log** in a **Google Sheet**, and
* the **PNG images** (processed 28×28 + raw canvas) in a **Google Drive
  folder**,

both accessed through a **Google service account**.

Backend selection (in `storage.py`):

1. env var `HDCA_STORAGE_BACKEND` = `disk` | `cloud`
2. else `[storage] backend` in secrets
3. else `disk`

---

## A. Create the GitHub repo and push

Run these locally, from the project root. (`data/` and
`.streamlit/secrets.toml` are already git-ignored — good, never commit
them.)

```bash
cd /path/to/HandwrittenDigitCollectionApp

git init
git add .
git commit -m "HDCA: initial commit with cloud storage backend"

git branch -M main

# create the repo on GitHub first (github.com/new), then:
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If you use the GitHub CLI:

```bash
gh repo create <your-repo> --private --source=. --remote=origin --push
```

Verify `.streamlit/secrets.toml` and `data/` are **not** in the pushed
tree:

```bash
git ls-files | grep -E "secrets.toml|^data/"   # should print nothing
```

---

## B. Google Cloud Console

You need two things in the same project: an **OAuth client** (already
used for learner Google login, now also allow the `*.streamlit.app`
URL) and a **service account** (new — for Sheets + Drive).

### B1. Pick / create the project

<https://console.cloud.google.com/> → project picker → reuse the project
that already holds your OAuth client, or create one.

### B2. Update the OAuth client redirect URI (learner login)

Your Streamlit Cloud URL is fixed once you name the app, e.g.
`https://hdca-yourname.streamlit.app`. Decide the name now (step C1).

1. **APIs & Services → Credentials** → click your existing **OAuth 2.0
   Client ID** (Web application).
2. Under **Authorized redirect URIs**, keep the local one and **add**:
   ```
   https://<your-app-name>.streamlit.app/oauth2callback
   ```
3. Under **Authorized JavaScript origins** (if present), add:
   ```
   https://<your-app-name>.streamlit.app
   ```
4. Save. Changes can take a few minutes to propagate.
5. On the **OAuth consent screen**: while in "Testing" mode, add every
   learner's Google address under **Test users** (or click **Publish
   app** for unrestricted sign-in).

### B3. Enable the APIs

**APIs & Services → Enable APIs and services** → enable both:

* **Google Sheets API**
* **Google Drive API**

### B4. Create the service account

1. **APIs & Services → Credentials → Create credentials → Service
   account**.
2. Name it e.g. `hdca-storage`. Skip the optional role grants (it only
   needs access to the one sheet and folder you share with it, not
   project-wide roles). Click **Done**.
3. Open the new service account → **Keys → Add key → Create new key →
   JSON**. A `*.json` file downloads. **Treat it like a password.**
4. Note the service-account email, it looks like
   `hdca-storage@<project-id>.iam.gserviceaccount.com`.

### B5. Create the Google Sheet and share it

1. Create a blank sheet at <https://sheets.new>. Name it e.g.
   `HDCA Submissions`. Leave the tab empty — the app creates a
   `submissions` worksheet with headers on first write.
2. **Share** (top-right) → paste the **service-account email** → give it
   **Editor** → untick "Notify people" → **Share**.
3. From the sheet URL grab the **file ID**:
   `https://docs.google.com/spreadsheets/d/`**`THIS_LONG_ID`**`/edit`

### B6. Create the Drive folder and share it

1. In <https://drive.google.com/> create a folder, e.g. `HDCA Images`.
2. Right-click → **Share** → add the **service-account email** as
   **Editor** → **Share**.
3. Open the folder; grab the **folder ID** from the URL:
   `https://drive.google.com/drive/folders/`**`THIS_FOLDER_ID`**

> Note: files the service account creates are owned by the service
> account and count against *its* (small) Drive quota, but they live in
> your shared folder and you can always read/download them. For a class
> project this is fine. To have them count against your own Drive
> instead, create them with a shared drive, or see "Better options".

---

## C. Streamlit Community Cloud

### C1. Connect the repo

1. <https://share.streamlit.io/> → sign in with GitHub → **Create app**
   → **Deploy a public app from GitHub**.
2. Repository: `<your-username>/<your-repo>`, Branch: `main`, Main file
   path: `app.py`.
3. Click **Advanced settings** → set **Python version** to 3.11 (or
   3.12).
4. Set the **App URL** to `<your-app-name>` — this must match the
   `.streamlit.app` domain you put in the OAuth redirect URI (B2). If
   you change it later, update B2 too.

### C2. Set the secrets

Still in **Advanced settings → Secrets** (or later: app menu → Settings
→ Secrets), paste this TOML and fill every value:

```toml
[auth]
redirect_uri = "https://<your-app-name>.streamlit.app/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_STRING"

[auth.google]
client_id = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[admin]
username = "admin"
password = "CHANGE_ME_BEFORE_CLASS"

[storage]
backend = "cloud"
gsheet_id = "THE_GOOGLE_SHEET_FILE_ID_FROM_B5"
gdrive_folder_id = "THE_DRIVE_FOLDER_ID_FROM_B6"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "from-the-json-key"
private_key = "-----BEGIN PRIVATE KEY-----\nLINE1...\nLINEN...\n-----END PRIVATE KEY-----\n"
client_email = "hdca-storage@your-project-id.iam.gserviceaccount.com"
client_id = "from-the-json-key"
token_uri = "https://oauth2.googleapis.com/token"
```

Filling `[gcp_service_account]` from the downloaded JSON:

* Copy each field across by name.
* `private_key` must stay a **single line** with literal `\n` escapes —
  copy it exactly as it appears in the JSON file (it already has the
  `\n`s). Keep the surrounding double quotes.
* `auth_uri`, `auth_provider_x509_cert_url`, `client_x509_cert_url` from
  the JSON are optional here and can be omitted.

Generate `cookie_secret` locally with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### C3. Deploy

Click **Deploy**. First build installs `requirements.txt` (a few
minutes). Watch the logs for import errors.

---

## D. Post-deploy checks

1. **App loads** at `https://<your-app-name>.streamlit.app` with the
   "Log in with Google" button (no stack trace).
2. **Google login** works and redirects back to the app. If you get
   `redirect_uri_mismatch`, the URI in B2 doesn't exactly match
   `[auth].redirect_uri` in C2 (scheme, host, `/oauth2callback`, no
   trailing slash).
3. **Submit a digit.** Then check:
   * the Google Sheet now has a `submissions` tab with a header row and
     your row (`status = pending`);
   * the Drive folder has two new PNGs (`..._<digit>_<ts>.png` and
     `..._raw.png`).
   If writes fail with `403` / `PERMISSION_DENIED`, re-share the sheet
   **and** the folder with the service-account email as Editor (B5/B6),
   and confirm both APIs are enabled (B3).
4. **Admin page** `/Admin` — log in with the `[admin]` credentials, open
   **Review queue**, confirm the submission renders all three pipeline
   stages (raw, cropped, final). Approve it.
5. Back on the learner page, progress advances past that digit.
6. **MNIST export** tab → the approved digit appears; CSV and Excel
   downloads work.
7. **Restart the app** (app menu → Reboot). After it comes back, the
   submission is still there — proving persistence survives the
   ephemeral filesystem.
8. **Local dev still works**: with `.streamlit/secrets.toml` set to
   `[storage] backend = "disk"` (or unset), `streamlit run app.py`
   writes to `data/` as before.

---

## Better options (when to graduate)

The Sheets + Drive setup is deliberately the lowest-friction path for a
class project: no card on file, no infra, reuses the Google account
you already have. Move on when:

| Situation | Better option | Tradeoffs |
|---|---|---|
| Sheet is slow / flaky past ~a few thousand rows, or you hit Google API rate limits (60 read + 60 write / min / user) during a busy class | **Postgres** (Supabase / Neon free tier) for the log | Real DB: transactions, concurrent writes, fast queries. Needs a connection string secret and swapping `_worksheet()` calls for SQL. Free tiers sleep / have storage caps. |
| Many images, or you want them counting against real object storage rather than a service-account's Drive quota | **Cloudflare R2** or **AWS S3** for the PNGs (`boto3`, S3-compatible) | Proper blob store, cheap, presigned URLs. R2 has no egress fees. Adds an account + bucket + access-key secret. |
| App keeps cold-starting, or you want it always-on, background jobs, or a persistent local disk | **Fly.io** or **Render** with a **mounted volume** | You control the container; a volume gives you back a real filesystem so the *original* `storage_disk.py` works unchanged. Costs a few $/mo; you manage deploys, and a single volume doesn't scale past one instance. |
| Production-ish: multiple reviewers, backups, auditing | **Postgres + R2** together, on Fly/Render | Clean separation (rows vs blobs), scalable, backed up. Most setup effort; overkill for a one-off class. |

For this course, stay on Sheets + Drive. Revisit only if you actually
hit one of the rows above.
