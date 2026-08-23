import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from supabase import create_client

IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    return datetime.now(IST)


def today_ist() -> date:
    return now_ist().date()


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
# FORM STRUCTURE — category -> subcategory -> list of (field, label, type)
# type is "number", "kg", "select:Opt1,Opt2,...", or "chicken_size"
# ---------------------------------------------------------------------------
CHICKEN_SIZE_OPTIONS = ["Small", "Medium", "Big"]
CHICKEN_SIZE_TO_NUM = {"Small": 1, "Medium": 2, "Big": 3}
CHICKEN_SIZE_FROM_NUM = {1: "Small", 2: "Medium", 3: "Big"}

FORM_STRUCTURE = {
    "Stock": {
        "Ajker Kena": [
            ("chandan_quantity_kg", "Chandan Quantity (KG)", "kg"),
            ("chandan_price_per_kg", "Chandan Price per KG", "number"),
            ("chandan_payment", "Chandan Payment", "number"),
            ("sabir_quantity_kg", "Sabir Quantity (KG)", "kg"),
            ("sabir_price_per_kg", "Sabir Price per KG", "number"),
            ("sabir_payment", "Sabir Payment", "number"),
            ("snandi_quantity_kg", "SNandi Quantity (KG)", "kg"),
            ("snandi_price_per_kg", "SNandi Price per KG", "number"),
            ("snandi_payment", "SNandi Payment", "number"),
            ("stock_other1_quantity_kg", "Other1 Quantity (KG)", "kg"),
            ("stock_other1_price_per_kg", "Other1 Price per KG", "number"),
            ("stock_other1_payment", "Other1 Payment", "number"),
            ("stock_other2_quantity_kg", "Other2 Quantity (KG)", "kg"),
            ("stock_other2_price_per_kg", "Other2 Price per KG", "number"),
            ("stock_other2_payment", "Other2 Payment", "number"),
            ("ajke_mal_pore_ache_kg", "Ajke Mal Pore Ache (KG)", "kg"),
        ],
    },
    "Sales": {
        "Hindusthan": [
            ("hotel1_sales_kg", "Hotel1 Sales (KG)", "kg"),
            ("hotel1_price_per_kg", "Hotel1 Price per KG", "number"),
            ("hotel1_payment", "Hotel1 Payment", "number"),
        ],
        "Other1": [
            ("hotel2_sales_kg", "Hotel2 Sales (KG)", "kg"),
            ("hotel2_price_per_kg", "Hotel2 Price per KG", "number"),
            ("hotel2_payment", "Hotel2 Payment", "number"),
        ],
        "Other2": [
            ("hotel3_sales_kg", "Hotel3 Sales (KG)", "kg"),
            ("hotel3_price_per_kg", "Hotel3 Price per KG", "number"),
            ("hotel3_payment", "Hotel3 Payment", "number"),
        ],
        "Dokan": [
            ("chicken_size", "Chicken Size", "chicken_size"),
            ("mangso_price_per_kg", "Mangso Price per KG", "number"),
            ("gota_customer_sales_kg", "Gota Customer Sales (KG)", "kg"),
            ("gota_customer_price_per_kg", "Gota Customer Price per KG", "number"),
            ("gota_dokandar_sales_kg", "Gota Dokandar Sales (KG)", "kg"),
            ("gota_dokandar_price_per_kg", "Gota Dokandar Price per KG", "number"),
            ("chhat_sales_kg", "Chhat Sales (KG)", "kg"),
            ("chhat_price_per_kg", "Chhat Price per KG", "number"),
        ],
    },
    "Cashflow": {
        "": [
            ("total_cash_ache", "Total Cash Ache", "number"),
            ("phonepe_balance", "PhonePe Balance", "number"),
            ("phonepe_aseche", "PhonePe Aseche", "number"),
            ("phonepe_payment_hoyeche", "PhonePe Payment Hoyeche", "number"),
            ("ajker_dokane_dhar_diyeche", "Ajker Dokane Dhar Diyeche", "number"),
            ("ajke_dhar_aday_hoyeche", "Ajke Dhar Aday Hoyeche", "number"),
            ("ajker_advance_payment_aseche", "Ajker Advance Payment Aseche", "number"),
            ("ajke_mangso_pore_ache", "Ajke Mangso Pore Ache", "number"),
            ("murgi_mangso_loss", "Murgi Mangso Loss", "number"),
        ],
    },
    "Expense": {
        "": [
            ("emi_box", "EMI Box", "number"),
            ("labour", "Labour", "number"),
            ("desi_murgi", "Desi Murgi", "number"),
            ("murgi_mash", "Murgi Mash", "number"),
            ("susan_labour", "Susan Labour", "number"),
            ("paper", "Paper", "number"),
            ("bazar", "Bazar", "number"),
            ("gari_vara", "Gari Vara", "number"),
            ("gas", "Gas", "number"),
            ("expense_other1", "Other1", "number"),
            ("expense_other2", "Other2", "number"),
            ("expense_other3", "Other3", "number"),
            ("expense_other4", "Other4", "number"),
            ("expense_other5", "Other5", "number"),
        ],
    },
    "Personal Dhar": {
        "": [
            ("vodu", "Vodu", "number"),
            ("atanu", "Atanu", "number"),
            ("personal_other1", "Other1", "number"),
            ("personal_other2", "Other2", "number"),
            ("personal_other3", "Other3", "number"),
            ("personal_other4", "Other4", "number"),
            ("personal_other5", "Other5", "number"),
        ],
    },
}

ALL_FIELD_NAMES = [
    field for cats in FORM_STRUCTURE.values() for fields in cats.values() for field, _, _ in fields
]


def render_category_fields(prefix: str, defaults: dict = None):
    """Renders every category/subcategory field. Must be called inside an
    active st.form(). Returns nothing — read values back via st.session_state
    using the same keys ({prefix}_{field_name}) after the form submits."""
    defaults = defaults or {}
    for category, subcats in FORM_STRUCTURE.items():
        with st.expander(f"📁 {category}", expanded=False):
            for subcat, fields in subcats.items():
                if subcat:
                    st.markdown(f"**{subcat}**")
                for field_name, label, ftype in fields:
                    key = f"{prefix}_{field_name}"
                    if ftype == "kg":
                        default_val = float(defaults.get(field_name, 0) or 0)
                        st.number_input(
                            label, value=default_val, step=0.1, format="%.2f", key=key
                        )
                    elif ftype == "number":
                        default_val = float(defaults.get(field_name, 0) or 0)
                        st.number_input(label, value=default_val, step=1.0, key=key)
                    elif ftype.startswith("select:"):
                        options = ftype.split(":", 1)[1].split(",")
                        default_val = defaults.get(field_name) or options[0]
                        idx = options.index(default_val) if default_val in options else 0
                        st.selectbox(label, options, index=idx, key=key)
                    elif ftype == "chicken_size":
                        # Stored in the DB as numeric (1/2/3); shown in the
                        # UI as a dropdown with the text labels.
                        # Defaults to "Medium" when no prior value exists.
                        default_num = defaults.get(field_name, 2)
                        default_label = CHICKEN_SIZE_FROM_NUM.get(
                            default_num, "Medium"
                        )
                        idx = CHICKEN_SIZE_OPTIONS.index(default_label)
                        st.selectbox(label, CHICKEN_SIZE_OPTIONS, index=idx, key=key)


def collect_field_values(prefix: str) -> dict:
    """Reads back the values of every field for a given prefix from
    session_state after a form submit."""
    values = {}
    for field_name in ALL_FIELD_NAMES:
        raw = st.session_state[f"{prefix}_{field_name}"]
        if field_name == "chicken_size":
            values[field_name] = CHICKEN_SIZE_TO_NUM.get(raw)
        else:
            values[field_name] = raw
    return values

# ---------------------------------------------------------------------------
# CALCULATION LOGIC
# NOTE: these are starting-point aggregates only — confirm the real profit /
# reconciliation formula with the business owner and adjust as needed.
# ---------------------------------------------------------------------------
def calculate_metrics(row: dict) -> dict:
    total_stock_quantity_kg = (
        row["chandan_quantity_kg"] + row["sabir_quantity_kg"] + row["snandi_quantity_kg"]
        + row["stock_other1_quantity_kg"] + row["stock_other2_quantity_kg"]
    )
    total_stock_cost = (
        row["chandan_payment"] + row["sabir_payment"] + row["snandi_payment"]
        + row["stock_other1_payment"] + row["stock_other2_payment"]
    )
    total_sales_quantity_kg = (
        row["hotel1_sales_kg"] + row["hotel2_sales_kg"] + row["hotel3_sales_kg"]
        + row["gota_customer_sales_kg"] + row["gota_dokandar_sales_kg"] + row["chhat_sales_kg"]
    )
    total_sales_revenue = (
        row["hotel1_payment"] + row["hotel2_payment"] + row["hotel3_payment"]
        + row["gota_customer_sales_kg"] * row["gota_customer_price_per_kg"]
        + row["gota_dokandar_sales_kg"] * row["gota_dokandar_price_per_kg"]
        + row["chhat_sales_kg"] * row["chhat_price_per_kg"]
    )
    expense_fields = [
        "emi_box", "labour", "desi_murgi", "murgi_mash", "susan_labour", "paper",
        "bazar", "gari_vara", "gas", "expense_other1", "expense_other2",
        "expense_other3", "expense_other4", "expense_other5",
    ]
    total_expense = sum(row[f] for f in expense_fields)

    personal_fields = [
        "vodu", "atanu", "personal_other1", "personal_other2",
        "personal_other3", "personal_other4", "personal_other5",
    ]
    total_personal_dhar = sum(row[f] for f in personal_fields)

    estimated_profit = total_sales_revenue - total_stock_cost - total_expense

    return {
        "total_stock_quantity_kg": round(total_stock_quantity_kg, 2),
        "total_stock_cost": round(total_stock_cost, 2),
        "total_sales_quantity_kg": round(total_sales_quantity_kg, 2),
        "total_sales_revenue": round(total_sales_revenue, 2),
        "total_expense": round(total_expense, 2),
        "total_personal_dhar": round(total_personal_dhar, 2),
        "estimated_profit": round(estimated_profit, 2),
    }

# ---------------------------------------------------------------------------
# UPDATE LOGIC
# ---------------------------------------------------------------------------
def update_entry(input_id: int, new_date, field_values: dict):
    update_payload = {
        "entry_date": str(new_date),
        "updated_at": now_ist().isoformat(),
        **field_values,
    }
    supabase.table(INPUT_TABLE).update(update_payload).eq("id", input_id).execute()

    metrics = calculate_metrics(field_values)
    supabase.table(OUTPUT_TABLE).update({
        "entry_date": str(new_date),
        "updated_at": now_ist().isoformat(),
        **metrics,
    }).eq("input_id", input_id).execute()

    return metrics


def render_edit_section(rows: list, key_prefix: str):
    if not rows:
        return

    with st.expander("✏️ Edit an entry"):
        options = {
            f"ID {r['id']} — {r['entry_date']} (by {r['submitted_by']})": r
            for r in rows
        }
        choice = st.selectbox(
            "Select entry to edit", list(options.keys()), key=f"{key_prefix}_edit_select"
        )
        row = options[choice]

        with st.form(f"{key_prefix}_edit_form"):
            new_date = st.date_input(
                "Date", value=date.fromisoformat(row["entry_date"]), key=f"{key_prefix}_edit_date"
            )
            render_category_fields(f"{key_prefix}_edit", defaults=row)
            save = st.form_submit_button("Save changes", use_container_width=True)

        if save:
            field_values = collect_field_values(f"{key_prefix}_edit")
            st.session_state["pending_edit"] = {
                "input_id": row["id"],
                "new_date": new_date,
                "field_values": field_values,
            }
            st.rerun()

    if "pending_edit" in st.session_state:
        confirm_edit_dialog()


@st.dialog("Confirm Update")
def confirm_edit_dialog():
    data = st.session_state["pending_edit"]
    st.write(f"Update entry for **{data['new_date']}**?")
    st.caption("This will recalculate and update the linked output metrics too.")

    col1, col2 = st.columns(2)
    if col1.button("Confirm Update", use_container_width=True):
        update_entry(data["input_id"], data["new_date"], data["field_values"])
        st.session_state.pop("pending_edit", None)
        st.success("Entry updated.")
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_edit", None)
        st.rerun()

# ---------------------------------------------------------------------------
# DELETE LOGIC
# ---------------------------------------------------------------------------
def delete_entry(input_id: int):
    supabase.table(OUTPUT_TABLE).delete().eq("input_id", input_id).execute()
    supabase.table(INPUT_TABLE).delete().eq("id", input_id).execute()


def render_delete_section(rows: list, key_prefix: str):
    if not rows:
        return

    with st.expander("🗑️ Delete an entry"):
        options = {
            f"ID {r['id']} — {r['entry_date']} (by {r['submitted_by']})": r
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
    st.write(f"Save entry for **{data['entry_date']}**?")
    st.caption("This will be stored in the Input table and metrics calculated into the Output table.")

    col1, col2 = st.columns(2)
    if col1.button("Confirm & Submit", use_container_width=True):
        entry_date = data["entry_date"]
        field_values = data["field_values"]

        input_row = {
            "entry_date": str(entry_date),
            "submitted_by": st.session_state["username"],
            "created_at": now_ist().isoformat(),
            **field_values,
        }
        input_result = supabase.table(INPUT_TABLE).insert(input_row).execute()
        input_id = input_result.data[0]["id"]

        metrics = calculate_metrics(field_values)
        output_row = {
            "entry_date": str(entry_date),
            "submitted_by": st.session_state["username"],
            "input_id": input_id,
            "created_at": now_ist().isoformat(),
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

    with tab1:
        with st.form("add_entry_form"):
            entry_date = st.date_input("Date", value=today_ist(), key="add_entry_date")
            render_category_fields("add")
            submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
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
                field_values = collect_field_values("add")
                st.session_state["pending_entry"] = {
                    "entry_date": entry_date,
                    "field_values": field_values,
                }
                st.rerun()

    if "pending_entry" in st.session_state:
        confirm_submit_dialog()

    with tab2:
        view_date = st.date_input("Select date", value=today_ist(), key="business_view_date")

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
    total_stock_cost = sum(r["total_stock_cost"] for r in rows)
    total_sales_revenue = sum(r["total_sales_revenue"] for r in rows)
    total_expense = sum(r["total_expense"] for r in rows)
    total_profit = sum(r["estimated_profit"] for r in rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Stock Cost", f"{total_stock_cost:,.2f}")
    c2.metric("Total Sales Revenue", f"{total_sales_revenue:,.2f}")
    c3.metric("Total Expense", f"{total_expense:,.2f}")
    c4.metric("Estimated Profit", f"{total_profit:,.2f}")


def admin_view():
    show_banner()
    st.title("📊 Admin Dashboard")

    tab1, tab2 = st.tabs(["Single Date View", "Compare Two Dates"])

    with tab1:
        selected_date = st.date_input("Select date", value=today_ist(), key="single_date")

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

    with tab2:
        source = st.radio("Data source to compare", ["Input", "Output"], horizontal=True)
        table_name = INPUT_TABLE if source == "Input" else OUTPUT_TABLE

        col_a, col_b = st.columns(2)
        with col_a:
            date_a = st.date_input("Date A", value=today_ist(), key="date_a")
        with col_b:
            date_b = st.date_input("Date B", value=today_ist(), key="date_b")

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
