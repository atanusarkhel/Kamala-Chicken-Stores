# Kamala Chicken Stores — Business Metrics App

A simple internal web app for daily business data entry and reporting.
Business users log daily category-wise data (Stock, Sales, Cashflow,
Expense, Personal Dhar); the app calculates daily profit/loss from it;
admins can review, edit, delete, and audit that data by date or by month.

Built with **Streamlit** (frontend + backend logic) and **Supabase**
(Postgres database), deployed free on **Streamlit Community Cloud**.

---

## Access

- Username/password login gate (predefined in the app's secrets — no
  self-signup).
- Two roles: **Business User** and **Admin**, each with a different view
  after login.

---

## Business User Page

### Add Entry
Daily data is organized into 6 collapsible categories:

| Category | Required? | Subcategories / fields |
|---|---|---|
| **Stock** | Mandatory | Ajker Kena — Chandan, Sabir, SNandi, Other1, Other2 (quantity, price/kg, payment), plus leftover stock (KG) |
| **Hotel Sales** | Mandatory | Hindusthan, Other1, Other2 — sales (KG), price/kg, payment per hotel |
| **Dokan Sales** | Mandatory | Chicken size (Small/Medium/Big), Mangso price/kg, Gota Customer & Gota Dokandar (sales, price), Chhat (sales, price) |
| **Cashflow** | Mandatory | Cash in hand, PhonePe balance/in/out, dhar given/recovered, advance payments, leftover meat, loss |
| **Expense** | Mandatory | EMI, Labour, Desi Murgi, Murgi Mash, Susan Labour, Paper, Bazar, Gari Vara, Gas, + 5 free-text "Other" slots |
| **Personal Dhar** | Optional | Vodu, Atanu, + 5 free-text "Other" slots |

Categories marked **\*** are mandatory; the rest (Personal Dhar) are
optional. A **✅** on a category header means data is already saved for
the selected date; **🚩** means it's still pending.

- **One submit button per category** — each category is saved
  independently, so a business user can fill in Stock now and come back
  for Sales later.
- **Confirmation popup** before every save, showing the values about to
  be stored.
- **Locked after submission** — once a category is saved for a date, its
  fields become read-only for business users (prevents accidental
  double-entry or edits). Only an admin can change it after that.
- **Quantity (KG) fields** accept decimals (e.g. `3.50`), entered in
  0.1 steps.
- **Chicken Size** is a dropdown (Small/Medium/Big) but stored in the
  database as a number (1/2/3) — defaults to Medium.
- A couple of fields have sensible defaults pre-filled on a blank form:
  Chhat Price per KG (140), EMI Box (2500).

### Calculate button
A large, highlighted **CALCULATE** button sits below all 6 categories.

- If any **mandatory** category is still missing data for that date, it
  refuses to calculate and tells you exactly which categories are
  missing.
- Personal Dhar is optional and never blocks calculation.
- Once all mandatory categories are filled, it computes the combined
  output (stock cost, sales revenue, expense, profit/loss) and saves it.
- The result is shown directly below the button in large text —
  **green** for profit, **red** for loss — and persists on the page for
  that date even without re-clicking Calculate.

### Monthly Input Overview
A calendar-style table for any month, showing per day:
- ✅/🚩 for each of the 6 categories and for the combined Output.
- Who entered the data and when (IST), once the day's output has been
  calculated.
- A running count of "Complete days" vs "Incomplete days" for the month.

---

## Admin Page

### Single Date View
All 6 categories shown for a chosen date, each always editable
(never locked for admins):

- **Save** — inserts new data or updates existing data for that
  category/date, then automatically recalculates the combined output.
- **Delete** — removes that category's data, with a confirmation popup.
  - Deleting a **mandatory** category's data also deletes the day's
    combined output entirely, since it's no longer valid — the business
    user has to resubmit and press Calculate again to regenerate it.
  - Deleting the optional Personal Dhar category just recalculates in
    place.
- Category headers show ✅/🚩 status and the mandatory-category
  asterisk (**\***), same as the business page.
- The combined **Output (calculated metrics)** section below shows the
  day's totals: stock cost, sales revenue, expense, and profit/loss.

### Compare Two Dates
Pick any one data source (any of the 6 categories, or the combined
Output/Metrics) and two dates — the two days' data are shown side by
side for quick comparison.

### Monthly Input Overview
Same monthly completion table described above, available to admins too.

---

## Data & timestamps

- Each category has its own database table, linked by `entry_date`
  (one row per date per category).
- A combined `business_metrics` table holds the calculated daily
  profit/loss output, recomputed automatically whenever any category's
  data changes.
- All "entered at" timestamps are recorded and displayed in **IST**
  (Asia/Kolkata), regardless of the server's own timezone.

---

## Tech stack

- **Frontend/backend:** [Streamlit](https://streamlit.io) (Python)
- **Database:** [Supabase](https://supabase.com) (hosted Postgres)
- **Hosting:** Streamlit Community Cloud (free)

## Setup

See [`BEGINNER_SETUP_GUIDE.md`](./BEGINNER_SETUP_GUIDE.md) for a full
step-by-step walkthrough (Supabase project setup, GitHub upload,
Streamlit Cloud deployment, and secrets configuration), and
[`schema.sql`](./schema.sql) for the current database schema.
