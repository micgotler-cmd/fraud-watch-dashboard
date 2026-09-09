import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="FRAUD_WATCH // terminal",
    page_icon="🖥️",
    initial_sidebar_state="expanded",
)

GREEN = "#00ff41"
DARK_GREEN = "#003b00"
MID_GREEN = "#0a8f2f"
BG = "#0d0208"
PANEL_BG = "#0a0d0a"
GRAY = "#4d4d4d"

# ---------------------------------------------------------------------------
# CUSTOM CSS — MATRIX / HACKER TERMINAL THEME
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Share Tech Mono', 'Courier New', monospace !important;
    }}

    .stApp {{
        background-color: {BG};
        background-image:
            linear-gradient(rgba(0,255,65,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,255,65,0.03) 1px, transparent 1px);
        background-size: 24px 24px;
        color: {GREEN};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {PANEL_BG};
        border-right: 1px solid {DARK_GREEN};
    }}
    section[data-testid="stSidebar"] * {{
        color: {GREEN} !important;
    }}

    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {GREEN} !important;
        text-shadow: 0 0 8px rgba(0,255,65,0.55);
        letter-spacing: 1px;
    }}

    p, span, label, div {{
        color: #a6f5b8;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background-color: {PANEL_BG};
        border: 1px solid {DARK_GREEN};
        border-radius: 4px;
        padding: 14px 16px;
        box-shadow: 0 0 12px rgba(0,255,65,0.15);
    }}
    div[data-testid="stMetric"] label {{
        color: {MID_GREEN} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {GREEN} !important;
        text-shadow: 0 0 10px rgba(0,255,65,0.6);
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 1px solid {DARK_GREEN};
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {PANEL_BG};
        color: {MID_GREEN};
        border: 1px solid {DARK_GREEN};
        border-bottom: none;
        border-radius: 4px 4px 0 0;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {DARK_GREEN} !important;
        color: {GREEN} !important;
        box-shadow: 0 0 10px rgba(0,255,65,0.4);
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid {DARK_GREEN};
        box-shadow: 0 0 12px rgba(0,255,65,0.15);
    }}

    /* Buttons */
    .stButton > button, .stDownloadButton > button {{
        background-color: {PANEL_BG};
        color: {GREEN};
        border: 1px solid {GREEN};
        font-family: 'Share Tech Mono', monospace;
        box-shadow: 0 0 8px rgba(0,255,65,0.25);
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background-color: {DARK_GREEN};
        color: #ffffff;
        box-shadow: 0 0 16px rgba(0,255,65,0.6);
    }}

    /* Sliders */
    div[data-baseweb="slider"] > div > div > div {{
        background: {GREEN} !important;
    }}

    /* Horizontal rule / divider look */
    hr {{
        border-color: {DARK_GREEN};
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {BG}; }}
    ::-webkit-scrollbar-thumb {{ background: {DARK_GREEN}; border-radius: 5px; }}

    .terminal-caption {{
        color: {MID_GREEN};
        font-size: 0.85rem;
        border-left: 3px solid {GREEN};
        padding-left: 10px;
        margin: 6px 0 18px 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=GREEN, family="Share Tech Mono, Courier New, monospace"),
        xaxis=dict(gridcolor=DARK_GREEN, zerolinecolor=DARK_GREEN, linecolor=DARK_GREEN),
        yaxis=dict(gridcolor=DARK_GREEN, zerolinecolor=DARK_GREEN, linecolor=DARK_GREEN),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=[GREEN, "#ff2e2e", MID_GREEN, "#00cfff", "#ffee00", "#ff8800"],
    )
)

FRAUD_COLOR_MAP = {"Fraud": "#ff2e2e", "Legit": GREEN}

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("credit_card_fraud_10k.csv")
    df["fraud_label"] = df["is_fraud"].map({1: "Fraud", 0: "Legit"})
    return df


df = load_data()

# ---------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ---------------------------------------------------------------------------
st.sidebar.markdown("## ▓▓ FILTER_CONSOLE ▓▓")
st.sidebar.markdown("`> configure query parameters_`")

if st.sidebar.button("⟲ RESET ALL FILTERS"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

amount_min, amount_max = float(df["amount"].min()), float(df["amount"].max())
amount_range = st.sidebar.slider(
    "AMOUNT ($)", amount_min, amount_max, (amount_min, amount_max), key="amount_range"
)

hour_range = st.sidebar.slider(
    "TRANSACTION HOUR", 0, 23, (0, 23), key="hour_range"
)

categories = sorted(df["merchant_category"].unique())
selected_categories = st.sidebar.multiselect(
    "MERCHANT CATEGORY", categories, default=categories, key="categories"
)

foreign_choice = st.sidebar.radio(
    "FOREIGN TRANSACTION", ["All", "Yes", "No"], horizontal=True, key="foreign_choice"
)

mismatch_choice = st.sidebar.radio(
    "LOCATION MISMATCH", ["All", "Yes", "No"], horizontal=True, key="mismatch_choice"
)

trust_min, trust_max = int(df["device_trust_score"].min()), int(df["device_trust_score"].max())
trust_range = st.sidebar.slider(
    "DEVICE TRUST SCORE", trust_min, trust_max, (trust_min, trust_max), key="trust_range"
)

velocity_min, velocity_max = int(df["velocity_last_24h"].min()), int(df["velocity_last_24h"].max())
velocity_range = st.sidebar.slider(
    "VELOCITY (LAST 24H)", velocity_min, velocity_max, (velocity_min, velocity_max), key="velocity_range"
)

age_min, age_max = int(df["cardholder_age"].min()), int(df["cardholder_age"].max())
age_range = st.sidebar.slider(
    "CARDHOLDER AGE", age_min, age_max, (age_min, age_max), key="age_range"
)

fraud_choice = st.sidebar.radio(
    "FRAUD STATUS", ["All", "Fraud only", "Legit only"], key="fraud_choice"
)

# ---------------------------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------------------------
mask = (
    df["amount"].between(amount_range[0], amount_range[1])
    & df["transaction_hour"].between(hour_range[0], hour_range[1])
    & df["merchant_category"].isin(selected_categories)
    & df["device_trust_score"].between(trust_range[0], trust_range[1])
    & df["velocity_last_24h"].between(velocity_range[0], velocity_range[1])
    & df["cardholder_age"].between(age_range[0], age_range[1])
)

if foreign_choice != "All":
    mask &= df["foreign_transaction"] == (1 if foreign_choice == "Yes" else 0)
if mismatch_choice != "All":
    mask &= df["location_mismatch"] == (1 if mismatch_choice == "Yes" else 0)
if fraud_choice != "All":
    mask &= df["is_fraud"] == (1 if fraud_choice == "Fraud only" else 0)

fdf = df[mask]

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown("# 🖥️ FRAUD_WATCH // TERMINAL v1.0")
st.markdown(
    '<div class="terminal-caption">'
    "&gt; live query on credit_card_fraud_10k.csv — adjust FILTER_CONSOLE to isolate fraud-predictive patterns_"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------------------------
total_n = len(fdf)
fraud_n = int(fdf["is_fraud"].sum())
fraud_rate = (fraud_n / total_n * 100) if total_n else 0.0
avg_amount = fdf["amount"].mean() if total_n else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("TOTAL TRANSACTIONS", f"{total_n:,}")
k2.metric("FRAUD DETECTED", f"{fraud_n:,}")
k3.metric("FRAUD RATE", f"{fraud_rate:.2f}%")
k4.metric("AVG AMOUNT", f"${avg_amount:,.2f}")

st.markdown("---")

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📟 OVERVIEW", "🧬 FEATURE ANALYSIS", "🗃️ DATA EXPLORER"])

with tab1:
    if total_n == 0:
        st.warning("NO RECORDS MATCH CURRENT FILTERS.")
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            counts = fdf["fraud_label"].value_counts().reindex(["Legit", "Fraud"]).fillna(0).reset_index()
            counts.columns = ["fraud_label", "count"]
            fig = px.bar(
                counts, x="fraud_label", y="count", color="fraud_label",
                color_discrete_map=FRAUD_COLOR_MAP, template=PLOTLY_TEMPLATE,
                title="TRANSACTION COUNT: FRAUD vs LEGIT",
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="count")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fraud_rate,
                number={"suffix": "%", "font": {"color": GREEN}},
                title={"text": "FRAUD RATE (current filter)", "font": {"color": GREEN}},
                gauge={
                    "axis": {"range": [0, max(10, fraud_rate * 2)], "tickcolor": GREEN},
                    "bar": {"color": "#ff2e2e"},
                    "bgcolor": BG,
                    "borderwidth": 1,
                    "bordercolor": DARK_GREEN,
                    "steps": [
                        {"range": [0, max(10, fraud_rate * 2) * 0.5], "color": DARK_GREEN},
                        {"range": [max(10, fraud_rate * 2) * 0.5, max(10, fraud_rate * 2)], "color": "#1a0000"},
                    ],
                },
            ))
            fig.update_layout(paper_bgcolor=BG, font={"color": GREEN}, height=350)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if total_n < 2:
        st.warning("NOT ENOUGH RECORDS FOR FEATURE ANALYSIS.")
    else:
        st.markdown("### ▸ PREDICTOR RANKING (correlation with is_fraud)")
        numeric_cols = [
            "amount", "transaction_hour", "foreign_transaction", "location_mismatch",
            "device_trust_score", "velocity_last_24h", "cardholder_age",
        ]
        corr = fdf[numeric_cols + ["is_fraud"]].corr()["is_fraud"].drop("is_fraud")
        corr = corr.sort_values(key=abs, ascending=True).reset_index()
        corr.columns = ["feature", "correlation"]
        fig = px.bar(
            corr, x="correlation", y="feature", orientation="h",
            color="correlation", color_continuous_scale=["#ff2e2e", GRAY, GREEN],
            template=PLOTLY_TEMPLATE, title="Correlation of each feature with fraud",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<div class="terminal-caption">'
            "&gt; larger absolute value = stronger signal. positive = higher value → more fraud; negative = lower value → more fraud."
            "</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            cat_rate = fdf.groupby("merchant_category")["is_fraud"].mean().mul(100).sort_values(ascending=False).reset_index()
            cat_rate.columns = ["merchant_category", "fraud_rate_pct"]
            fig = px.bar(
                cat_rate, x="merchant_category", y="fraud_rate_pct",
                template=PLOTLY_TEMPLATE, title="FRAUD RATE BY MERCHANT CATEGORY",
                color="fraud_rate_pct", color_continuous_scale=["#003b00", "#ff2e2e"],
            )
            fig.update_layout(coloraxis_showscale=False, yaxis_title="fraud rate (%)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            flag_data = []
            for flag_col, flag_name in [("foreign_transaction", "Foreign TX"), ("location_mismatch", "Location Mismatch")]:
                for val in [0, 1]:
                    subset = fdf[fdf[flag_col] == val]
                    rate = subset["is_fraud"].mean() * 100 if len(subset) else 0
                    flag_data.append({"flag": flag_name, "value": "Yes" if val else "No", "fraud_rate_pct": rate})
            flag_df = pd.DataFrame(flag_data)
            fig = px.bar(
                flag_df, x="flag", y="fraud_rate_pct", color="value", barmode="group",
                template=PLOTLY_TEMPLATE, title="FRAUD RATE: FOREIGN TX / LOCATION MISMATCH",
                color_discrete_map={"Yes": "#ff2e2e", "No": GREEN},
            )
            fig.update_layout(yaxis_title="fraud rate (%)")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### ▸ DISTRIBUTION: FRAUD vs LEGIT")
        dist_cols = ["amount", "device_trust_score", "velocity_last_24h", "transaction_hour", "cardholder_age"]
        chosen = st.multiselect("Select features to plot", dist_cols, default=dist_cols, key="dist_cols")

        for i in range(0, len(chosen), 2):
            row_cols = st.columns(2)
            for j, col_name in enumerate(chosen[i:i + 2]):
                with row_cols[j]:
                    fig = px.histogram(
                        fdf, x=col_name, color="fraud_label", barmode="overlay",
                        histnorm="percent", opacity=0.65,
                        color_discrete_map=FRAUD_COLOR_MAP, template=PLOTLY_TEMPLATE,
                        title=f"{col_name} — fraud vs legit",
                    )
                    fig.update_layout(yaxis_title="% of group")
                    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown(f"### ▸ RAW QUERY RESULTS — `{total_n}` rows matched")
    st.dataframe(fdf.drop(columns=["fraud_label"]), use_container_width=True, height=480)
    csv = fdf.drop(columns=["fraud_label"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ DOWNLOAD FILTERED DATA (.csv)", data=csv,
        file_name="fraud_watch_filtered.csv", mime="text/csv",
    )
