import streamlit as st
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Business Metrics App", layout="centered")

# ---------------------------------------------------------------------------
# CONNECT TO SUPABASE
# ---------------------------------------------------------------------------
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase()
TABLE_NAME = "business_entries"

# ---------------------------------------------------------------------------
# LOGIN GATE (predefined username/password -> role)
# secrets.toml holds a dict like:
# [users]
# alice = { password = "abc123", role = "business" }
# admin1 = { password = "xyz789", role = "admin" }
# ---------------------------------------------------------------------------
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        users = st.secrets.get("users", {})
        user = users.get(username)
        if user and password == user["password"]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.rerun()
        else:
            st.error("Invalid username or password.")


def logout_button():
    with st.sidebar:
        st.write(f"Logged in as **{st.session_state['username']}** ({st.session_state['role']})")
        if st.button("Log out"):
            for k in ["authenticated", "username", "role"]:
                st.session_state.pop(k, None)
            st.rerun()

# ---------------------------------------------------------------------------
# CALCULATION LOGIC — customize this function for your real business metrics
# ---------------------------------------------------------------------------
def calculate_metrics(revenue: float, cost: float, units_sold: int) -> dict:
    profit = revenue - cost
    margin_pct = (profit / revenue * 100) if revenue else 0
    avg_price_per_unit = (revenue / units_sold) if units_sold else 0
    return {
        "profit": round(profit, 2),
        "margin_pct": round(margin_pct, 2),
        "avg_price_per_unit": round(avg_price_per_unit, 2),
    }

# ---------------------------------------------------------------------------
# BUSINESS USER VIEW
# ---------------------------------------------------------------------------
def business_view():
    st.title("📝 Business Data Entry")

    with st.form("entry_form", clear_on_submit=True):
        entry_date = st.date_input("Date", value=date.today())
        revenue = st.number_input("Revenue", min_value=0.0, step=100.0)
        cost = st.number_input("Cost", min_value=0.0, step=100.0)
        units_sold = st.number_input("Units Sold", min_value=0, step=1)
        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        metrics = calculate_metrics(revenue, cost, units_sold)
        row = {
            "entry_date": str(entry_date),
            "submitted_by": st.session_state["username"],
            "revenue": revenue,
            "cost": cost,
            "units_sold": units_sold,
            **metrics,
        }
        supabase.table(TABLE_NAME).insert(row).execute()
        st.success("Saved successfully.")
        st.json(metrics)

# ---------------------------------------------------------------------------
# ADMIN VIEW
# ---------------------------------------------------------------------------
def admin_view():
    st.title("📊 Admin Dashboard")

    selected_date = st.date_input("Select date to view", value=date.today())

    result = (
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("entry_date", str(selected_date))
        .execute()
    )
    rows = result.data

    if not rows:
        st.info("No entries for this date.")
        return

    st.dataframe(rows, use_container_width=True)

    total_revenue = sum(r["revenue"] for r in rows)
    total_cost = sum(r["cost"] for r in rows)
    total_profit = sum(r["profit"] for r in rows)
    avg_margin = sum(r["margin_pct"] for r in rows) / len(rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"{total_revenue:,.2f}")
    c2.metric("Total Cost", f"{total_cost:,.2f}")
    c3.metric("Total Profit", f"{total_profit:,.2f}")
    c4.metric("Avg Margin %", f"{avg_margin:,.2f}%")

# ---------------------------------------------------------------------------
# MAIN ROUTING
# ---------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    logout_button()
    if st.session_state["role"] == "admin":
        admin_view()
    else:
        business_view()
