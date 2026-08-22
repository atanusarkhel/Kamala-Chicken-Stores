# Business Metrics App — Setup Guide

A minimal Streamlit app: business users submit data, calculations run in the
backend, results are stored in a Supabase (Postgres) table, and admins pick
a date to view all entries plus aggregate metrics for that date. Both roles
sit behind a username/password gate.

## 1. Create the free Supabase project (your database)
1. Go to https://supabase.com → sign up free → "New project".
2. Once created, go to **SQL Editor** → paste the contents of `schema.sql` → Run.
3. Go to **Project Settings → API** → copy the **Project URL** and the
   **anon public key** (or service_role key if you want admin-level DB access).

## 2. Configure secrets
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
2. Fill in your Supabase URL/key.
3. Add your predefined usernames/passwords under `[users]`, each with
   `role = "business"` or `role = "admin"`.
4. **Do not commit `secrets.toml` to a public repo** — it holds real credentials.

## 3. Run locally (optional, to test)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open the local URL it prints, log in with a username from your secrets file.

## 4. Deploy for free, globally accessible
1. Push this folder to a GitHub repo (exclude `secrets.toml` — add it to `.gitignore`).
2. Go to https://share.streamlit.io → sign in with GitHub → "New app".
3. Point it at your repo and `app.py`.
4. In the app's **Settings → Secrets**, paste the full contents of your
   local `secrets.toml` (Supabase URL/key + users).
5. Deploy. You'll get a public URL like `https://your-app.streamlit.app`
   reachable from anywhere.

## Customizing the calculation
Edit the `calculate_metrics()` function in `app.py`. Currently it computes
profit, margin %, and average price per unit from revenue/cost/units sold —
swap in your real business formulas and matching input fields, and update
`schema.sql` to match the columns you need.

## Adding/removing users
Just edit the `[users]` table in secrets (locally and in Streamlit Cloud's
Secrets panel) — no code changes needed.
