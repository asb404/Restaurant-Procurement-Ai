import streamlit as st
import requests

st.set_page_config(layout="wide")
if "show_notification" not in st.session_state:
    st.session_state.show_notification = False
if "quote_data" not in st.session_state:
    st.session_state.quote_data = None
if "menu_data" not in st.session_state:
    st.session_state.menu_data = None
if "pricing_data" not in st.session_state:
    st.session_state.pricing_data = None
if "distributor_data" not in st.session_state:
    st.session_state.distributor_data = None
if "rfp_id" not in st.session_state:
    st.session_state.rfp_id = None
if "pipeline_error" not in st.session_state:
    st.session_state.pipeline_error = None

st.markdown("""
<style>

/* GLOBAL */
body, .stApp {
    background: #0b0f19;
    color: #e5e7eb;
}

/* HEADER */
.title {
    font-size: 28px;
    font-weight: 700;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 20px;
}

/* LEFT PANEL */
.panel {
    background: #111827;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

/* INPUT FIX */
input {
    background: #0f172a !important;
    border: 1px solid #1f2937 !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
}

/* BUTTON */
.stButton button {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    border-radius: 10px;
    height: 45px;
    font-weight: 600;
    border: none;
}
.stButton button:hover {
    opacity: 0.9;
}

/* CARD */
.card {
    background: #111827;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #1f2937;
    margin-bottom: 16px;
}

/* STEP HEADER */
.header-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

/* BADGE */
.badge {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 20px;
}

.pending { background:#374151; }
.processing { background:#1d4ed8; }
.done { background:#059669; }
.error { background:#dc2626; }

/* CONTENT */
.content {
    height: 220px;
    overflow-y: auto;
    font-size: 14px;
    color: #d1d5db;
}

/* TABLE */
table {
    width: 100%;
}
td, th {
    padding: 6px;
    border-bottom: 1px solid #1f2937;
}

/* DISTRIBUTOR */
.dist {
    background:#0f172a;
    padding:8px;
    border-radius:8px;
    margin-bottom:6px;
}

</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/process-menu"
GENERATE_MOCK_QUOTES_URL = "http://127.0.0.1:8000/generate-mock-quotes"
COMPARE_QUOTES_URL = "http://127.0.0.1:8000/compare-quotes"

# HEADER
st.markdown('<div class="title">Restaurant Procurement AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered sourcing & pricing intelligence</div>', unsafe_allow_html=True)

left, right = st.columns([1,2])

# ---------------- LEFT ----------------
with left:

    name = st.text_input("Restaurant Name", placeholder="Spice Garden")
    loc = st.text_input("Location", placeholder="Mumbai")
    url = st.text_input("Menu URL", placeholder="https://menu.pdf")

    run = st.button("Run Pipeline", use_container_width=True)
    generate_quotes = st.button("Generate Quotes", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RIGHT ----------------
with right:
    s1 = st.empty()
    s2 = st.empty()
    s3 = st.empty()
    s4 = st.empty()
    s5 = st.empty()

def step(ph, title, content, status):
    ph.markdown(f"""
    <div class="card">
        <div class="header-row">
            <b>{title}</b>
            <span class="badge {status}">{status}</span>
        </div>
        <div class="content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

# INIT
step(s1, "Parsed Menu", "Waiting...", "pending")
step(s2, "Pricing", "Waiting...", "pending")
step(s3, "Distributors", "Waiting...", "pending")
step(s4, "RFP Status", "Waiting...", "pending")
step(s5, "Quote Comparison", "Waiting...", "pending")

# ---------------- RUN ----------------
if run:
    if not name or not loc or not url:
        st.error("Fill all fields")
    else:
        payload = {
            "restaurant_name": name,
            "location": loc,
            "pdf_url": url
        }

        try:
            res = requests.post(API_URL, json=payload)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            st.session_state.pipeline_error = str(e)
        else:
            st.session_state.pipeline_error = None

            dishes = data.get("dishes", [])
            distributors = data.get("distributors_contacted", [])
            rfp_id = data.get("rfp_id")

            menu_html = ""
            for dish in dishes:
                menu_html += f"<b>{dish.get('dish')}</b><br>"
                for ingredient in dish.get("ingredients", []):
                    menu_html += f"- {ingredient.get('name')}<br>"
                menu_html += "<br>"

            pricing_rows: list[dict] = []
            seen = set()
            for dish in dishes:
                for ingredient in dish.get("ingredients", []):
                    ingredient_name = ingredient.get("name")
                    if ingredient_name in seen:
                        continue
                    seen.add(ingredient_name)
                    trend = ingredient.get("pricing", {}).get("trend", "stable")
                    pricing_rows.append(
                        {
                            "ingredient": ingredient_name,
                            "price": ingredient.get("pricing", {}).get("price", "N/A"),
                            "trend": trend,
                        }
                    )

            distributor_html = ""
            for distributor in distributors:
                distributor_html += (
                    f"<div class='dist'><b>{distributor['name']}</b><br>{distributor['contact_email']}</div>"
                )

            st.session_state.menu_data = menu_html or "No data"
            st.session_state.pricing_data = pricing_rows
            st.session_state.distributor_data = distributor_html or "No distributors"
            st.session_state.rfp_id = rfp_id
            st.session_state.quote_data = None

            if distributors:
                st.toast(f"📧 Emails sent to {len(distributors)} distributors")
            else:
                st.toast("⚠️ No distributors found")

if generate_quotes:
    rfp_id = st.session_state.get("rfp_id")
    if not rfp_id:
        st.session_state.pipeline_error = "Run pipeline first to create an RFP."
    else:
        try:
            mock_res = requests.post(f"{GENERATE_MOCK_QUOTES_URL}/{rfp_id}", timeout=120)
            mock_res.raise_for_status()

            cmp_res = requests.get(f"{COMPARE_QUOTES_URL}/{rfp_id}", timeout=120)
            cmp_res.raise_for_status()
            st.session_state.quote_data = cmp_res.json()
            st.session_state.pipeline_error = None
        except Exception as error:
            st.session_state.pipeline_error = f"Failed: {error}"

if st.session_state.pipeline_error:
    step(s1, "Parsed Menu", st.session_state.pipeline_error, "error")
    step(s2, "Pricing", st.session_state.pipeline_error, "error")
    step(s3, "Distributors", st.session_state.pipeline_error, "error")
    step(s4, "RFP Status", st.session_state.pipeline_error, "error")
    step(s5, "Quote Comparison", st.session_state.pipeline_error, "error")
else:
    if st.session_state.menu_data:
        step(s1, "Parsed Menu", st.session_state.menu_data, "done")
    else:
        step(s1, "Parsed Menu", "Waiting...", "pending")

    if st.session_state.pricing_data:
        trend_meta = {
            "increasing": ("📈", "Increasing", "#10b981"),
            "decreasing": ("📉", "Decreasing", "#ef4444"),
            "stable": ("➖", "Stable", "#9ca3af"),
        }
        pricing_table = "<table><tr><th>Ingredient</th><th>Price</th><th>Trend</th></tr>"
        for row in st.session_state.pricing_data:
            trend_value = str(row.get("trend", "stable")).strip().lower()
            icon, label, color = trend_meta.get(trend_value, trend_meta["stable"])
            trend_html = (
                f"<span style='color:{color};display:inline-flex;align-items:center;"
                f"white-space:nowrap;gap:6px;'>{icon}<span>{label}</span></span>"
            )
            pricing_table += (
                f"<tr><td>{row['ingredient']}</td><td>{row['price']}</td>"
                f"<td>{trend_html}</td></tr>"
            )
        pricing_table += "</table>"
        step(s2, "Pricing", pricing_table, "done")
    else:
        step(s2, "Pricing", "Waiting...", "pending")

    if st.session_state.distributor_data:
        step(s3, "Distributors", st.session_state.distributor_data, "done")
    else:
        step(s3, "Distributors", "Waiting...", "pending")

    if st.session_state.rfp_id:
        step(s4, "RFP Status", f"RFP Created: <b>{st.session_state.rfp_id}</b>", "done")
    else:
        step(s4, "RFP Status", "No RFP generated yet.", "pending")

quote_data = st.session_state.get("quote_data")
if quote_data:
    with s5.container():
        st.subheader("Step 5: Quote Comparison")
        totals = quote_data.get("totals", [])
        if totals:
            table_html = ["<table><tr><th>Distributor</th><th>Total Cost</th></tr>"]
            for row in totals:
                distributor = row.get("distributor_name", "Unknown")
                total_cost = round(float(row.get("total_cost", 0.0)), 2)
                table_html.append(f"<tr><td>{distributor}</td><td>{total_cost}</td></tr>")
            table_html.append("</table>")
            st.markdown("".join(table_html), unsafe_allow_html=True)
        else:
            st.info("No quote totals available.")

        recommended = quote_data.get("recommended_distributor")
        if recommended:
            recommended_name = recommended.get("distributor_name", "Unknown")
            st.success(f"Recommended: {recommended_name}")
else:
    step(s5, "Quote Comparison", "Click 'Generate Quotes' to fetch comparison.", "pending")