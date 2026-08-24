import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from supabase import create_client

st.set_page_config(page_title="Business Metrics App", layout="centered")

BUSINESS_NAME = "Kamala Chicken Stores"
IST = ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    return datetime.now(IST)


def today_ist() -> date:
    return now_ist().date()


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
# FLASH MESSAGES — persist a success/error message across a st.rerun() so
# it actually shows up to the user (a message set right before rerun()
# would otherwise be wiped before it's ever displayed).
# ---------------------------------------------------------------------------
def set_flash(kind: str, message: str):
    st.session_state["flash"] = {"kind": kind, "message": message}


def show_flash():
    flash = st.session_state.pop("flash", None)
    if flash:
        if flash["kind"] == "success":
            st.success(f"✅ {flash['message']}")
        else:
            st.error(f"❌ {flash['message']}")


def inject_calculate_button_style():
    st.markdown(
        """
        <style>
        button[kind="primary"] {
            font-size: 22px !important;
            font-weight: 800 !important;
            padding: 16px 0 !important;
            background-color: #FFC107 !important;
            color: #000000 !important;
            border: 2px solid #FF8F00 !important;
            border-radius: 10px !important;
        }
        button[kind="primary"]:hover {
            background-color: #FFB300 !important;
            border-color: #E65100 !important;
        }
        </style>
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
OUTPUT_TABLE = "business_metrics"

# ---------------------------------------------------------------------------
# LOGIN GATE
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
# CATEGORY DEFINITIONS — one table per category
# type is "number", "kg", "select:Opt1,Opt2,...", or "chicken_size"
# ---------------------------------------------------------------------------
# Default values shown on a blank (not-yet-submitted) form. Only applies
# when no existing data is found for the date — actual saved values always
# take priority.
DEFAULT_FIELD_VALUES = {
    "chhat_price_per_kg": 140.0,
    "emi_box": 2500.0,
}

CHICKEN_SIZE_OPTIONS = ["Small", "Medium", "Big"]
CHICKEN_SIZE_TO_NUM = {"Small": 1, "Medium": 2, "Big": 3}
CHICKEN_SIZE_FROM_NUM = {1: "Small", 2: "Medium", 3: "Big"}

CATEGORIES = {
    "stock": {
        "table": "business_stock",
        "label": "Stock",
        "subcats": {
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
    },
    "hotel_sales": {
        "table": "business_hotel_sales",
        "label": "Hotel Sales",
        "subcats": {
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
        },
    },
    "dokan_sales": {
        "table": "business_dokan_sales",
        "label": "Dokan Sales",
        "subcats": {
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
    },
    "cashflow": {
        "table": "business_cashflow",
        "label": "Cashflow",
        "subcats": {
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
    },
    "expense": {
        "table": "business_expense",
        "label": "Expense",
        "subcats": {
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
    },
    "personal_dhar": {
        "table": "business_personal_dhar",
        "label": "Personal Dhar",
        "subcats": {
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
    },
}


def category_field_names(cat: dict) -> list:
    return [f for fields in cat["subcats"].values() for f, _, _ in fields]


def render_single_field(field_name, label, ftype, key, defaults, disabled):
    fallback = DEFAULT_FIELD_VALUES.get(field_name, 0)
    if ftype == "kg":
        default_val = float(defaults.get(field_name, fallback) or fallback)
        st.number_input(label, value=default_val, step=0.1, format="%.2f", key=key, disabled=disabled)
    elif ftype == "number":
        default_val = float(defaults.get(field_name, fallback) or fallback)
        st.number_input(label, value=default_val, step=1.0, key=key, disabled=disabled)
    elif ftype == "chicken_size":
        default_num = defaults.get(field_name, 2)
        default_label = CHICKEN_SIZE_FROM_NUM.get(default_num, "Medium")
        idx = CHICKEN_SIZE_OPTIONS.index(default_label)
        st.selectbox(label, CHICKEN_SIZE_OPTIONS, index=idx, key=key, disabled=disabled)
    elif ftype.startswith("select:"):
        options = ftype.split(":", 1)[1].split(",")
        default_val = defaults.get(field_name) or options[0]
        idx = options.index(default_val) if default_val in options else 0
        st.selectbox(label, options, index=idx, key=key, disabled=disabled)


def collect_category_values(cat_key: str, cat: dict) -> dict:
    values = {}
    for field_name, _, ftype in [f for fields in cat["subcats"].values() for f in fields]:
        raw = st.session_state[f"{cat_key}_{field_name}"]
        if ftype == "chicken_size":
            values[field_name] = CHICKEN_SIZE_TO_NUM.get(raw)
        else:
            values[field_name] = raw
    return values


def fetch_category_row(table_name: str, entry_date: date):
    result = (
        supabase.table(table_name)
        .select("*")
        .eq("entry_date", str(entry_date))
        .execute()
    )
    return result.data[0] if result.data else None


def fetch_dates_in_range(table_name: str, start_date: date, end_date: date) -> set:
    result = (
        supabase.table(table_name)
        .select("entry_date")
        .gte("entry_date", str(start_date))
        .lte("entry_date", str(end_date))
        .execute()
    )
    return {r["entry_date"] for r in result.data}


def format_timestamps_ist(rows: list) -> list:
    """Supabase/PostgREST always returns timestamptz values as UTC in JSON,
    regardless of what timezone was used when the value was written. The
    stored instant is correct either way — this just re-renders
    created_at/updated_at in IST for display within this app."""
    formatted = []
    for row in rows:
        new_row = dict(row)
        for field in ("created_at", "updated_at"):
            val = new_row.get(field)
            if val:
                try:
                    dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
                    new_row[field] = dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
                except (ValueError, TypeError):
                    pass
        formatted.append(new_row)
    return formatted

# ---------------------------------------------------------------------------
# CALCULATION LOGIC
# NOTE: starting-point aggregates only — confirm the real profit /
# reconciliation formula with the business owner and adjust as needed.
# ---------------------------------------------------------------------------
def calculate_metrics(row: dict) -> dict:
    g = lambda k: row.get(k, 0) or 0

    total_stock_quantity_kg = (
        g("chandan_quantity_kg") + g("sabir_quantity_kg") + g("snandi_quantity_kg")
        + g("stock_other1_quantity_kg") + g("stock_other2_quantity_kg")
    )
    total_stock_cost = (
        g("chandan_payment") + g("sabir_payment") + g("snandi_payment")
        + g("stock_other1_payment") + g("stock_other2_payment")
    )
    total_sales_quantity_kg = (
        g("hotel1_sales_kg") + g("hotel2_sales_kg") + g("hotel3_sales_kg")
        + g("gota_customer_sales_kg") + g("gota_dokandar_sales_kg") + g("chhat_sales_kg")
    )
    total_sales_revenue = (
        g("hotel1_payment") + g("hotel2_payment") + g("hotel3_payment")
        + g("gota_customer_sales_kg") * g("gota_customer_price_per_kg")
        + g("gota_dokandar_sales_kg") * g("gota_dokandar_price_per_kg")
        + g("chhat_sales_kg") * g("chhat_price_per_kg")
    )
    expense_fields = [
        "emi_box", "labour", "desi_murgi", "murgi_mash", "susan_labour", "paper",
        "bazar", "gari_vara", "gas", "expense_other1", "expense_other2",
        "expense_other3", "expense_other4", "expense_other5",
    ]
    total_expense = sum(g(f) for f in expense_fields)

    personal_fields = [
        "vodu", "atanu", "personal_other1", "personal_other2",
        "personal_other3", "personal_other4", "personal_other5",
    ]
    total_personal_dhar = sum(g(f) for f in personal_fields)

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


def recompute_metrics(entry_date: date, submitted_by: str):
    """Pulls whatever data exists across all category tables for this date
    and recalculates/upserts the combined output row."""
    combined = {}
    for cat in CATEGORIES.values():
        row = fetch_category_row(cat["table"], entry_date) or {}
        for field_name in category_field_names(cat):
            combined[field_name] = row.get(field_name, 0)

    metrics = calculate_metrics(combined)
    existing = fetch_category_row(OUTPUT_TABLE, entry_date)
    payload = {
        "entry_date": str(entry_date),
        "submitted_by": submitted_by,
        "updated_at": now_ist().isoformat(),
        **metrics,
    }
    if existing:
        supabase.table(OUTPUT_TABLE).update(payload).eq("entry_date", str(entry_date)).execute()
    else:
        payload["created_at"] = now_ist().isoformat()
        supabase.table(OUTPUT_TABLE).insert(payload).execute()

# ---------------------------------------------------------------------------
# BUSINESS USER: per-category submit section (locks after first submit)
# ---------------------------------------------------------------------------
@st.dialog("Confirm Submission")
def confirm_category_submit_dialog():
    pending = st.session_state["pending_category_submit"]
    cat = CATEGORIES[pending["cat_key"]]
    st.write(f"Save **{cat['label']}** data for **{pending['entry_date']}**?")
    st.caption("Once saved, these fields will be locked and cannot be edited by business users.")

    col1, col2 = st.columns(2)
    if col1.button("Confirm & Submit", use_container_width=True):
        row = {
            "entry_date": str(pending["entry_date"]),
            "submitted_by": st.session_state["username"],
            "created_at": now_ist().isoformat(),
            **pending["values"],
        }
        try:
            supabase.table(cat["table"]).insert(row).execute()
            set_flash("success", f"{cat['label']} data successfully saved.")
        except Exception as e:
            set_flash("error", f"Failed to save {cat['label']} data: {e}")
        st.session_state.pop("pending_category_submit", None)
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_category_submit", None)
        st.rerun()


def render_category_submit_section(cat_key: str, entry_date: date):
    cat = CATEGORIES[cat_key]
    existing = fetch_category_row(cat["table"], entry_date)
    locked = existing is not None

    label_prefix = "✅" if locked else "📁"

    if not locked:
        st.markdown(
            f"""
            <div style="
                display:inline-block;
                background-color:#FF4B4B;
                color:white;
                padding:5px 12px;
                border-radius:6px;
                font-size:13px;
                font-weight:700;
                margin-bottom:4px;
            ">
                ⚠️ {cat['label']} — data not yet submitted
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander(f"{label_prefix} {cat['label']}", expanded=False):
        if locked:
            st.info(f"Data for {entry_date} is already submitted and locked.")
        for subcat, fields in cat["subcats"].items():
            if subcat:
                st.markdown(f"**{subcat}**")
            for field_name, label, ftype in fields:
                key = f"{cat_key}_{field_name}"
                render_single_field(field_name, label, ftype, key, existing or {}, locked)

        if st.button(
            f"Submit {cat['label']}", key=f"{cat_key}_submit_btn",
            disabled=locked, use_container_width=True,
        ):
            values = collect_category_values(cat_key, cat)
            st.session_state["pending_category_submit"] = {
                "cat_key": cat_key, "entry_date": entry_date, "values": values,
            }
            st.rerun()

    if st.session_state.get("pending_category_submit", {}).get("cat_key") == cat_key:
        confirm_category_submit_dialog()


MANDATORY_CATEGORIES = [k for k in CATEGORIES if k != "personal_dhar"]


def render_calculate_section(entry_date: date):
    st.markdown("---")

    if st.button("🧮 CALCULATE", key="calculate_btn", use_container_width=True, type="primary"):
        missing = []
        for cat_key in MANDATORY_CATEGORIES:
            cat = CATEGORIES[cat_key]
            if not fetch_category_row(cat["table"], entry_date):
                missing.append(cat["label"])

        if missing:
            set_flash(
                "error",
                "Please submit data for the following mandatory categories "
                f"before calculating: {', '.join(missing)}.",
            )
        else:
            try:
                recompute_metrics(entry_date, st.session_state["username"])
                set_flash("success", "Metrics calculated successfully.")
            except Exception as e:
                set_flash("error", f"Failed to calculate metrics: {e}")
        st.rerun()

    output_row = fetch_category_row(OUTPUT_TABLE, entry_date)
    if output_row:
        profit = output_row["estimated_profit"]
        is_profit = profit >= 0
        bg = "#D8F3DC" if is_profit else "#F8D7DA"
        fg = "#0B6E4F" if is_profit else "#B00020"
        label = "Profit" if is_profit else "Loss"
        st.markdown(
            f"""
            <div style="
                background-color:{bg};
                color:{fg};
                padding:22px;
                text-align:center;
                font-size:34px;
                font-weight:800;
                border-radius:10px;
                margin-top:16px;
            ">
                {label}: ₹{abs(profit):,.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )


def business_view():
    show_banner()
    show_flash()
    inject_calculate_button_style()
    st.title("📝 Business Data Entry")

    tab1, tab2 = st.tabs(["Add Entry", "View My Input Data (Read-only)"])

    with tab1:
        entry_date = st.date_input("Date", value=today_ist(), key="shared_entry_date")
        for cat_key in CATEGORIES:
            render_category_submit_section(cat_key, entry_date)

        render_calculate_section(entry_date)

    with tab2:
        view_date = st.date_input("Select date", value=today_ist(), key="business_view_date")
        username = st.session_state["username"].strip()

        any_data = False
        for cat_key, cat in CATEGORIES.items():
            row = fetch_category_row(cat["table"], view_date)
            if row and row.get("submitted_by", "").strip().lower() == username.lower():
                any_data = True
                st.subheader(cat["label"])
                st.dataframe(format_timestamps_ist([row]), use_container_width=True)

        if not any_data:
            st.info("No input data found for this date.")

# ---------------------------------------------------------------------------
# ADMIN: per-category save (always editable) + delete + combined output
# ---------------------------------------------------------------------------
def render_admin_category_section(cat_key: str, entry_date: date):
    cat = CATEGORIES[cat_key]
    existing = fetch_category_row(cat["table"], entry_date)

    label_prefix = "✅" if existing else "🚩"
    with st.expander(f"{label_prefix} {cat['label']}", expanded=False):
        for subcat, fields in cat["subcats"].items():
            if subcat:
                st.markdown(f"**{subcat}**")
            for field_name, label, ftype in fields:
                key = f"admin_{cat_key}_{field_name}"
                render_single_field(field_name, label, ftype, key, existing or {}, disabled=False)

        col1, col2 = st.columns(2)
        with col1:
            save_clicked = st.button(
                f"Save {cat['label']}", key=f"admin_{cat_key}_save_btn", use_container_width=True
            )
        with col2:
            delete_clicked = False
            if existing:
                delete_clicked = st.button(
                    f"Delete {cat['label']} data", key=f"admin_{cat_key}_delete_btn",
                    use_container_width=True,
                )

        if save_clicked:
            values = collect_category_values(f"admin_{cat_key}", cat)
            st.session_state["pending_admin_save"] = {
                "cat_key": cat_key, "entry_date": entry_date, "values": values,
                "is_update": existing is not None,
            }
            st.rerun()

        if delete_clicked:
            st.session_state["pending_admin_delete"] = {"cat_key": cat_key, "entry_date": entry_date}
            st.rerun()

    if st.session_state.get("pending_admin_save", {}).get("cat_key") == cat_key:
        confirm_admin_save_dialog()
    if st.session_state.get("pending_admin_delete", {}).get("cat_key") == cat_key:
        confirm_admin_delete_dialog()


@st.dialog("Confirm Save")
def confirm_admin_save_dialog():
    pending = st.session_state["pending_admin_save"]
    cat = CATEGORIES[pending["cat_key"]]
    action = "Update" if pending["is_update"] else "Add"
    st.write(f"{action} **{cat['label']}** data for **{pending['entry_date']}**?")
    st.caption("This will recalculate the combined output metrics for this date.")

    col1, col2 = st.columns(2)
    if col1.button("Confirm", use_container_width=True):
        table_name = cat["table"]
        entry_date = pending["entry_date"]
        values = pending["values"]
        try:
            if pending["is_update"]:
                payload = {"updated_at": now_ist().isoformat(), **values}
                supabase.table(table_name).update(payload).eq("entry_date", str(entry_date)).execute()
            else:
                payload = {
                    "entry_date": str(entry_date),
                    "submitted_by": st.session_state["username"],
                    "created_at": now_ist().isoformat(),
                    **values,
                }
                supabase.table(table_name).insert(payload).execute()

            recompute_metrics(entry_date, st.session_state["username"])
            set_flash("success", f"{cat['label']} data successfully saved.")
        except Exception as e:
            set_flash("error", f"Failed to save {cat['label']} data: {e}")
        st.session_state.pop("pending_admin_save", None)
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_admin_save", None)
        st.rerun()


@st.dialog("Confirm Deletion")
def confirm_admin_delete_dialog():
    pending = st.session_state["pending_admin_delete"]
    cat_key = pending["cat_key"]
    cat = CATEGORIES[cat_key]
    is_mandatory = cat_key in MANDATORY_CATEGORIES

    if is_mandatory:
        st.write(
            f"Sure want to delete the **{cat['label']}** data for "
            f"**{pending['entry_date']}**? Since this is a mandatory category, "
            f"the aggregated output metrics for this date will also be "
            f"**removed** — the business user will need to resubmit "
            f"{cat['label']} and press Calculate again to regenerate it."
        )
    else:
        st.write(
            f"Sure want to delete the **{cat['label']}** data for "
            f"**{pending['entry_date']}**? The combined output metrics for "
            f"this date will also be recalculated."
        )

    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete", use_container_width=True):
        try:
            supabase.table(cat["table"]).delete().eq("entry_date", str(pending["entry_date"])).execute()
            if is_mandatory:
                supabase.table(OUTPUT_TABLE).delete().eq("entry_date", str(pending["entry_date"])).execute()
                set_flash(
                    "success",
                    f"{cat['label']} data deleted. Aggregated output metrics for "
                    f"this date were removed and will need to be recalculated.",
                )
            else:
                recompute_metrics(pending["entry_date"], st.session_state["username"])
                set_flash("success", f"{cat['label']} data deleted.")
        except Exception as e:
            set_flash("error", f"Failed to delete {cat['label']} data: {e}")
        st.session_state.pop("pending_admin_delete", None)
        st.rerun()
    if col2.button("Cancel", use_container_width=True):
        st.session_state.pop("pending_admin_delete", None)
        st.rerun()


def show_output_totals(row: dict):
    if not row:
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Stock Cost", f"{row['total_stock_cost']:,.2f}")
    c2.metric("Total Sales Revenue", f"{row['total_sales_revenue']:,.2f}")
    c3.metric("Total Expense", f"{row['total_expense']:,.2f}")
    c4.metric("Estimated Profit", f"{row['estimated_profit']:,.2f}")


def render_monthly_overview():
    import calendar

    st.write("Pick any date in the month you want to review:")
    picked = st.date_input("Month", value=today_ist(), key="monthly_overview_date")

    year, month = picked.year, picked.month
    last_day_num = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, last_day_num)
    # Don't flag future days as "missing" — only check up to today.
    check_end = min(month_end, today_ist())

    # One query per table for the whole month, instead of per-day queries.
    dates_by_cat = {
        cat_key: fetch_dates_in_range(cat["table"], month_start, month_end)
        for cat_key, cat in CATEGORIES.items()
    }
    output_dates = fetch_dates_in_range(OUTPUT_TABLE, month_start, month_end)

    rows = []
    for day_num in range(1, last_day_num + 1):
        this_date = date(year, month, day_num)
        if this_date > check_end:
            break  # skip future days entirely

        date_str = str(this_date)
        row = {"Date": date_str}
        missing_mandatory = []
        for cat_key in CATEGORIES:
            cat = CATEGORIES[cat_key]
            present = date_str in dates_by_cat[cat_key]
            row[cat["label"]] = "✅" if present else "🚩"
            if cat_key in MANDATORY_CATEGORIES and not present:
                missing_mandatory.append(cat["label"])
        row["Output"] = "✅" if date_str in output_dates else "🚩"
        row["Missing (mandatory)"] = ", ".join(missing_mandatory) if missing_mandatory else "—"
        rows.append(row)

    if not rows:
        st.info("No days to show yet for this month.")
        return

    complete_days = sum(1 for r in rows if r["Missing (mandatory)"] == "—")
    incomplete_days = len(rows) - complete_days
    c1, c2 = st.columns(2)
    c1.metric("Complete days", complete_days)
    c2.metric("Incomplete days", incomplete_days)

    st.dataframe(rows, use_container_width=True, hide_index=True)


def admin_view():
    show_banner()
    show_flash()
    st.title("📊 Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["Single Date View", "Compare Two Dates", "Monthly Overview"])

    with tab1:
        selected_date = st.date_input("Select date", value=today_ist(), key="single_date")

        st.subheader("Input data by category")
        for cat_key in CATEGORIES:
            render_admin_category_section(cat_key, selected_date)

        st.subheader("Output (calculated metrics)")
        output_row = fetch_category_row(OUTPUT_TABLE, selected_date)
        if output_row:
            st.dataframe(format_timestamps_ist([output_row]), use_container_width=True)
            show_output_totals(output_row)
        else:
            st.info("No output data for this date yet.")

    with tab2:
        source_options = {cat["label"]: cat["table"] for cat in CATEGORIES.values()}
        source_options["Output (Metrics)"] = OUTPUT_TABLE
        source_label = st.selectbox("Data source to compare", list(source_options.keys()))
        table_name = source_options[source_label]

        col_a, col_b = st.columns(2)
        with col_a:
            date_a = st.date_input("Date A", value=today_ist(), key="date_a")
        with col_b:
            date_b = st.date_input("Date B", value=today_ist(), key="date_b")

        row_a = fetch_category_row(table_name, date_a)
        row_b = fetch_category_row(table_name, date_b)

        result_col_a, result_col_b = st.columns(2)
        with result_col_a:
            st.subheader(f"{source_label} — {date_a}")
            if row_a:
                st.dataframe(format_timestamps_ist([row_a]), use_container_width=True)
                if table_name == OUTPUT_TABLE:
                    show_output_totals(row_a)
            else:
                st.info("No entry for this date.")
        with result_col_b:
            st.subheader(f"{source_label} — {date_b}")
            if row_b:
                st.dataframe(format_timestamps_ist([row_b]), use_container_width=True)
                if table_name == OUTPUT_TABLE:
                    show_output_totals(row_b)
            else:
                st.info("No entry for this date.")

    with tab3:
        render_monthly_overview()

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
