# Deploy to Streamlit Cloud

Adapted for the Urban Company Graduation Project. Respect `docs/constraints.md`.

## 1) Push to GitHub
1. Ensure secrets are not committed (`.env`, `.streamlit/secrets.toml`, personal data).
2. Commit and push the repo to GitHub.

```powershell
git add .
git commit -m "UC graduation project: MVP, discovery engine, deck"
git push origin main
```

## 2) Create app on share.streamlit.io
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app**.
3. Select repo/branch.
4. **Main file path:** `app.py`
5. **Advanced settings > Python version:** 3.11 (if available) or compatible.
6. **Requirements file:** use `requirements-cloud.txt` (or set it in advanced settings if supported; otherwise keep `requirements.txt` cloud-safe).

## 3) Secrets
In Streamlit Cloud app settings > Secrets, add:

```toml
GEMINI_API_KEY = "your_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```

Notes:
- App works without Gemini key (deterministic offline fallback).
- Never commit keys to GitHub.

## 4) Wake up / ephemeral disk note
Streamlit Community Cloud may sleep the app when inactive. First load after sleep can take a minute.

**Ephemeral disk:** files written at runtime may be lost on restart/redeploy. Do not rely on runtime files for submission. Use **download buttons** in the app for deliverables (`discovery_results.json`, `evidence_log.md`, `evidence_log.pdf`, `NL_UrbanCompany.pdf`, checklist JSON). Commit final submission artefacts you need to preserve, as long as they contain no PII/secrets.

## 5) Post-deploy checks
- Root URL opens MVP (default page).
- Sidebar footer shows: "Public prototype · No bookings · No account access · Public information only".
- Discovery Engine runs on bundled sample.
- Evidence Log and Deck download buttons work.
- No secrets/PII visible.
- `python -m scripts.qa_check` passes locally before deploy.
