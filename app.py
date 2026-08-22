import streamlit as st
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Business Metrics App", layout="centered")

BUSINESS_NAME = "Kamala Chicken Stores"


def show_banner():
    st.markdown(
        f"""
        <div style="
            background-color:#79F6CE;
            color:#084F38;
            padding:12px 0;
            text-align:center;
            font-size:24px;
            font-weight:bold;
            border-radius:6px;
            margin-bottom:20px;
        ">
            {BUSINESS_NAME}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# CONNECT TO SUPABASE
# ---------------------------------------------------------------------------
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase()
INPUT_TABLE = "business_input"
OUTPUT_TABLE = "business_metrics"

# ---------------------------------------------------------------------------
# LOGIN GATE (predefined username/password -> role)
# secrets.toml holds a dict like:
# [users]
# alice = { password = "abc123", role = "business" }
# admin1 = { password = "xyz789", role = "admin" }
# ---------------------------------------------------------------------------
def login():
    show_banner()
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
# UPDATE LOGIC — edits an existing input row and recalculates its output row
# ---------------------------------------------------------------------------
def update_entry(input_id: int, new_date, revenue: float, cost: float, units_sold: int):
    supabase.table(INPUT_TABLE).update({
        "entry_date": str(new_date),
        "revenue": revenue,
        "cost": cost,
        "units_sold": units_sold,
    }).eq("id", input_id).execute()

    metrics = calculate_metrics(revenue, cost, units_sold)
    supabase.table(OUTPUT_TABLE).update({
        "entry_date": str(new_date),
        **metrics,
    }).eq("input_id", input_id).execute()

    return metrics


def render_edit_section(rows: list, key_prefix: str):
    """Shows a picker + edit form for a list of input rows. Reused by both
    the business user and admin views."""
    if not rows:
        return

    with st.expander("✏️ Edit an entry"):
        options = {
            f"ID {r['id']} — {r['entry_date']} — revenue {r['revenue']} "
            f"(by {r['submitted_by']})": r
            for r in rows
        }
        choice = st.selectbox(
            "Select entry to edit", list(options.keys()), key=f"{key_prefix}_select"
        )
        row = options[choice]

        with st.form(f"{key_prefix}_edit_form"):
            new_date = st.date_input(
                "Date", value=date.fromisoformat(row["entry_date"]), key=f"{key_prefix}_date"
            )
            new_revenue = st.number_input(
                "Revenue", min_value=0.0, step=100.0, value=float(row["revenue"]),
                key=f"{key_prefix}_revenue",
            )
            new_cost = st.number_input(
                "Cost", min_value=0.0, step=100.0, value=float(row["cost"]),
                key=f"{key_prefix}_cost",
            )
            new_units = st.number_input(
                "Units Sold", min_value=0, step=1, value=int(row["units_sold"]),
                key=f"{key_prefix}_units",
            )
            save = st.form_submit_button("Save changes", use_container_width=True)

        if save:
            # Stash the pending edit and show a confirmation popup instead
            # of saving immediately.
            st.session_state["pending_edit"] = {
                "input_id": row["id"],
                "new_date": new_date,
                "revenue": new_revenue,
                "cost": new_cost,
                "units_sold": new_units,
            }
            st.rerun()

    if "pending_edit" in st.session_state:
        confirm_edit_dialog()


@st.dialog("Confirm Update")
def confirm_edit_dialog():
    data = st.session_state["pending_edit"]
    st.write("Please confirm the updated values:")
    st.write(f"**Date:** {data['new_date']}")
    st.write(f"**Revenue:** {data['revenue']}")
    st.write(f"**Cost:** {data['cost']}")
    st.write(f"**Units Sold:** {data['units_sold']}")

    col1, col2 = st.columns(2)
    if col1.button("Confirm Update", use_container_width=True):
        metrics = update_entry(
            data["input_id"], data["new_date"], data["revenue"],
            data["cost"], data["units_sold"],
        )
        st.session_state.pop("pending_edit", None)
        st.success("Entry updated.")
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_edit", None)
        st.rerun()


# ---------------------------------------------------------------------------
# DELETE LOGIC — removes an entry from both input and output tables
# ---------------------------------------------------------------------------
def delete_entry(input_id: int):
    supabase.table(OUTPUT_TABLE).delete().eq("input_id", input_id).execute()
    supabase.table(INPUT_TABLE).delete().eq("id", input_id).execute()


def render_delete_section(rows: list, key_prefix: str):
    """Admin-only: pick an entry and delete it from both tables."""
    if not rows:
        return

    with st.expander("🗑️ Delete an entry"):
        options = {
            f"ID {r['id']} — {r['entry_date']} — revenue {r['revenue']} "
            f"(by {r['submitted_by']})": r
            for r in rows
        }
        choice = st.selectbox(
            "Select entry to delete", list(options.keys()), key=f"{key_prefix}_delete_select"
        )
        row = options[choice]

        if st.button("Delete this entry", key=f"{key_prefix}_delete_btn", use_container_width=True):
            st.session_state["pending_delete"] = row["id"]
            st.rerun()

    if "pending_delete" in st.session_state:
        confirm_delete_dialog()


@st.dialog("Confirm Deletion")
def confirm_delete_dialog():
    st.write("Sure want to delete this data from both input and output table?")
    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete", use_container_width=True):
        delete_entry(st.session_state["pending_delete"])
        st.session_state.pop("pending_delete", None)
        st.success("Entry deleted from both tables.")
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_delete", None)
        st.rerun()

# ---------------------------------------------------------------------------
# BUSINESS USER VIEW
# ---------------------------------------------------------------------------
@st.dialog("Confirm Submission")
def confirm_submit_dialog():
    data = st.session_state["pending_entry"]
    st.write("Please confirm the entry before saving:")
    st.write(f"**Date:** {data['entry_date']}")
    st.write(f"**Revenue:** {data['revenue']}")
    st.write(f"**Cost:** {data['cost']}")
    st.write(f"**Units Sold:** {data['units_sold']}")

    col1, col2 = st.columns(2)
    if col1.button("Confirm & Submit", use_container_width=True):
        entry_date = data["entry_date"]
        revenue = data["revenue"]
        cost = data["cost"]
        units_sold = data["units_sold"]

        # 1) Save the raw input
        input_row = {
            "entry_date": str(entry_date),
            "submitted_by": st.session_state["username"],
            "revenue": revenue,
            "cost": cost,
            "units_sold": units_sold,
        }
        input_result = supabase.table(INPUT_TABLE).insert(input_row).execute()
        input_id = input_result.data[0]["id"]

        # 2) Calculate metrics from that input
        metrics = calculate_metrics(revenue, cost, units_sold)

        # 3) Save the calculated output, linked back to the input row
        output_row = {
            "entry_date": str(entry_date),
            "submitted_by": st.session_state["username"],
            "input_id": input_id,
            **metrics,
        }
        supabase.table(OUTPUT_TABLE).insert(output_row).execute()

        st.session_state.pop("pending_entry", None)
        st.success("Saved successfully.")
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_entry", None)
        st.rerun()


def business_view():
    show_banner()
    st.title("📝 Business Data Entry")

    tab1, tab2 = st.tabs(["Add Entry", "View My Input Data (Read-only)"])

    # -----------------------------------------------------------------
    # TAB 1: Submit a new entry (existing behavior)
    # -----------------------------------------------------------------
    with tab1:
        with st.form("entry_form", clear_on_submit=True):
            entry_date = st.date_input("Date", value=date.today())
            revenue = st.number_input("Revenue", min_value=0.0, step=100.0)
            cost = st.number_input("Cost", min_value=0.0, step=100.0)
            units_sold = st.number_input("Units Sold", min_value=0, step=1)
            submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
            # Enforce one input entry per date (across all users)
            existing = (
                supabase.table(INPUT_TABLE)
                .select("id")
                .eq("entry_date", str(entry_date))
                .execute()
            )
            if existing.data:
                st.error(
                    f"An entry already exists for {entry_date}. "
                    "Only one input entry is allowed per date. "
                    "Please contact admin if this needs correction."
                )
            else:
                # Stash the pending entry and show a confirmation popup
                # instead of saving immediately.
                st.session_state["pending_entry"] = {
                    "entry_date": entry_date,
                    "revenue": revenue,
                    "cost": cost,
                    "units_sold": units_sold,
                }
                st.rerun()

    if "pending_entry" in st.session_state:
        confirm_submit_dialog()

    # -----------------------------------------------------------------
    # TAB 2: Pick any date, view input data already submitted
    # (scoped to this user's own submissions — change the .eq() below
    # to remove that filter if business users should see everyone's data)
    # -----------------------------------------------------------------
    with tab2:
        view_date = st.date_input("Select date", value=date.today(), key="business_view_date")

        result = (
            supabase.table(INPUT_TABLE)
            .select("*")
            .eq("entry_date", str(view_date))
            .ilike("submitted_by", st.session_state["username"].strip())
            .execute()
        )
        rows = result.data

        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No input data found for this date.")

# ---------------------------------------------------------------------------
# ADMIN VIEW
# ---------------------------------------------------------------------------
def fetch_rows(table_name: str, entry_date: date):
    result = (
        supabase.table(table_name)
        .select("*")
        .eq("entry_date", str(entry_date))
        .execute()
    )
    return result.data


def show_output_totals(rows: list):
    if not rows:
        return
    total_profit = sum(r["profit"] for r in rows)
    avg_margin = sum(r["margin_pct"] for r in rows) / len(rows)
    avg_price = sum(r["avg_price_per_unit"] for r in rows) / len(rows)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Profit", f"{total_profit:,.2f}")
    c2.metric("Avg Margin %", f"{avg_margin:,.2f}%")
    c3.metric("Avg Price/Unit", f"{avg_price:,.2f}")


def admin_view():
    show_banner()
    st.title("📊 Admin Dashboard")

    tab1, tab2 = st.tabs(["Single Date View", "Compare Two Dates"])

    # -----------------------------------------------------------------
    # TAB 1: Single date — input and output shown together
    # -----------------------------------------------------------------
    with tab1:
        selected_date = st.date_input("Select date", value=date.today(), key="single_date")

        input_rows = fetch_rows(INPUT_TABLE, selected_date)
        output_rows = fetch_rows(OUTPUT_TABLE, selected_date)

        st.subheader("Input data")
        if input_rows:
            st.dataframe(input_rows, use_container_width=True)
            render_edit_section(input_rows, key_prefix="admin")
            render_delete_section(input_rows, key_prefix="admin")
        else:
            st.info("No input entries for this date.")

        st.subheader("Output (calculated metrics)")
        if output_rows:
            st.dataframe(output_rows, use_container_width=True)
            show_output_totals(output_rows)
        else:
            st.info("No output entries for this date.")

    # -----------------------------------------------------------------
    # TAB 2: Compare two dates, from either Input or Output table
    # -----------------------------------------------------------------
    with tab2:
        source = st.radio("Data source to compare", ["Input", "Output"], horizontal=True)
        table_name = INPUT_TABLE if source == "Input" else OUTPUT_TABLE

        col_a, col_b = st.columns(2)
        with col_a:
            date_a = st.date_input("Date A", value=date.today(), key="date_a")
        with col_b:
            date_b = st.date_input("Date B", value=date.today(), key="date_b")

        rows_a = fetch_rows(table_name, date_a)
        rows_b = fetch_rows(table_name, date_b)

        result_col_a, result_col_b = st.columns(2)
        with result_col_a:
            st.subheader(f"{source} — {date_a}")
            if rows_a:
                st.dataframe(rows_a, use_container_width=True)
                if source == "Output":
                    show_output_totals(rows_a)
            else:
                st.info("No entries for this date.")
        with result_col_b:
            st.subheader(f"{source} — {date_b}")
            if rows_b:
                st.dataframe(rows_b, use_container_width=True)
                if source == "Output":
                    show_output_totals(rows_b)
            else:
                st.info("No entries for this date.")

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
