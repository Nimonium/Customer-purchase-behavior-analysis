"""
===============================================================================
APP.PY — Real-Time Customer Purchase Analytics Dashboard
===============================================================================
Course: AI & Statistics — Customer Purchase Behaviour Analysis Project

NOTE FOR REPORT / VIVA:
This Streamlit dashboard displays real-time auto-updating analytics on a 
transaction stream fed by 'simulator.py' into 'stream.db'. 
- The REAL-TIME ASPECT is the dashboard engineering: automatic 2-second refreshes, 
  rolling metrics, dynamic cumulative calculations, and stabilization readouts.
- The DATA FEED is a simulated replay of the historical 'customer_data.csv' dataset.
===============================================================================
"""

import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & AUTOREFRESH
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Live Analytics Dashboard | Customer Purchase Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 2000 ms (2 seconds)
# This keeps the dashboard live without manual browser reloads
st_autorefresh(interval=2000, limit=None, key="stream_dashboard_autorefresh")


# -----------------------------------------------------------------------------
# 2. DATABASE READ HELPER
# -----------------------------------------------------------------------------
def load_stream_data(db_path="stream.db"):
    """
    Safely connects to SQLite and reads live_transactions table into a DataFrame.
    Returns an empty DataFrame if database or table is not ready.
    """
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        # Enable WAL mode for smooth concurrent reads while simulator writes
        conn.execute("PRAGMA journal_mode=WAL;")
        df = pd.read_sql_query("SELECT * FROM live_transactions ORDER BY stream_id ASC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & VIVA EXPLANATION NOTE
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Stream Controls")

# Stream Reset Button
if st.sidebar.button("🗑️ Reset Stream Database", type="secondary", use_container_width=True):
    try:
        conn = sqlite3.connect("stream.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS live_transactions;")
        conn.commit()
        conn.close()
        st.sidebar.success("Database reset! Please restart 'simulator.py' in Terminal 1.")
    except Exception as e:
        st.sidebar.error(f"Error resetting database: {e}")

st.sidebar.divider()

# Viva / Demo Explanation Note for Manual Submissions:
# This form allows manual submission of a single live transaction directly into stream.db
# to demonstrate that manually-entered events instantly flow through the exact same
# real-time pipeline (KPIs, line chart, gauge, distributions, and correlation) as simulator.py.

st.sidebar.subheader("➕ Submit a Live Transaction")

with st.sidebar.form(key="manual_transaction_form"):
    age = st.number_input("Age", min_value=12, max_value=90, value=30)
    gender = st.selectbox("Gender", options=["Male", "Female"])
    income = st.number_input("Income ($)", min_value=1000, max_value=200000, value=30000, step=500)
    education = st.selectbox("Education", options=["HighSchool", "College", "Bachelor", "Masters"])
    region = st.selectbox("Region", options=["North", "South", "East", "West"])
    loyalty_status = st.selectbox("Loyalty Status", options=["Regular", "Silver", "Gold"])
    purchase_frequency = st.selectbox("Purchase Frequency", options=["rare", "occasional", "frequent"])
    purchase_amount = st.number_input("Purchase Amount ($)", min_value=1, max_value=100000, value=5000, step=50)
    product_category = st.selectbox("Product Category", options=["Electronics", "Clothing", "Books", "Food", "Health", "Home", "Beauty"])
    promotion_usage = st.checkbox("Promotion/coupon used?")
    satisfaction_score = st.slider("Satisfaction Score", min_value=1, max_value=10, value=5)
    
    submit_button = st.form_submit_button("Submit Transaction")

if submit_button:
    try:
        conn = sqlite3.connect("stream.db", timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        
        # Check if live_transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='live_transactions';")
        if not cursor.fetchone():
            st.sidebar.error("Start simulator.py first to initialize the database.")
            conn.close()
        else:
            # Generate new unique customer id
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM live_transactions;")
            new_customer_id = cursor.fetchone()[0]
            
            now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            promo_val = 1 if promotion_usage else 0
            
            insert_sql = """
            INSERT INTO live_transactions (
                id, age, gender, income, education, region,
                loyalty_status, purchase_frequency, purchase_amount,
                product_category, promotion_usage, satisfaction_score, received_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(insert_sql, (
                int(new_customer_id),
                int(age),
                str(gender),
                float(income),
                str(education),
                str(region),
                str(loyalty_status),
                str(purchase_frequency),
                float(purchase_amount),
                str(product_category),
                promo_val,
                int(satisfaction_score),
                now_timestamp
            ))
            conn.commit()
            new_stream_id = cursor.lastrowid
            conn.close()
            
            st.sidebar.success(f"Transaction submitted! Stream ID #{new_stream_id}")
    except sqlite3.OperationalError:
        st.sidebar.error("Start simulator.py first to initialize the database.")
    except Exception as e:
        st.sidebar.error(f"Error submitting transaction: {e}")

st.sidebar.divider()

# Viva / Report Architecture Explanation Note
st.sidebar.subheader("📌 Technical Architecture Note")
st.sidebar.info(
    """
    **Simulation vs. Real-Time Mechanics**:
    - **Data Source**: Replay of historical records from `customer_data.csv`.
    - **Real-Time Layer**: SQLite process decoupling (`stream.db`), 2-second Streamlit auto-refresh loop, cumulative rolling metrics, and streaming Pearson correlation convergence ($r \\approx 0.95$).
    
    *Designed for AI & Statistics course demonstration.*
    """
)


# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD CONTENT
# -----------------------------------------------------------------------------
st.title("⚡ Real-Time Customer Purchase Analytics")
st.markdown("Live streaming dashboard tracking transaction activity, customer metrics, and statistical correlations.")

# Fetch latest data snapshot
df = load_stream_data("stream.db")

if df.empty:
    st.warning("⚠️ **Waiting for transaction stream data...**")
    st.markdown(
        """
        No records found in `stream.db`. 
        
        **How to start the live stream:**
        1. Open a terminal and run: `python simulator.py`
        2. Keep the simulator running while viewing this auto-refreshing dashboard.
        """
    )
else:
    total_received = len(df)
    running_avg_amount = df["purchase_amount"].mean()
    running_avg_satisfaction = df["satisfaction_score"].mean()
    latest_row = df.iloc[-1]
    latest_category = latest_row["product_category"]
    latest_time = latest_row.get("received_at", "N/A")

    # -------------------------------------------------------------------------
    # a) TOP KPI ROW
    # -------------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Total Transactions",
            value=f"{total_received:,}",
            delta=f"Latest ID #{latest_row['stream_id']}"
        )

    with kpi2:
        st.metric(
            label="Running Avg Purchase",
            value=f"${running_avg_amount:,.2f}"
        )

    with kpi3:
        st.metric(
            label="Avg Satisfaction Score",
            value=f"{running_avg_satisfaction:.2f} / 10"
        )

    with kpi4:
        st.metric(
            label="Latest Category",
            value=latest_category,
            delta=f"At {latest_time.split(' ')[-1] if ' ' in str(latest_time) else latest_time}"
        )

    st.divider()

    # -------------------------------------------------------------------------
    # b) & e) MIDDLE ROW: CUMULATIVE LINE CHART & ROLLING SATISFACTION GAUGE
    # -------------------------------------------------------------------------
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Running Average Purchase Amount Over Time")
        
        # Calculate expanding cumulative mean
        df["running_avg_purchase"] = df["purchase_amount"].expanding().mean()
        
        fig_line = px.line(
            df,
            x="stream_id",
            y="running_avg_purchase",
            labels={
                "stream_id": "Stream ID (Transaction Count)",
                "running_avg_purchase": "Running Avg Amount ($)"
            },
            color_discrete_sequence=["#2563EB"]
        )
        fig_line.update_traces(hovertemplate="Stream ID: %{x}<br>Running Avg: $%{y:,.2f}")
        fig_line.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="rgba(243, 244, 246, 0.5)",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        st.subheader("🎯 Satisfaction Gauge")
        
        # Plotly Gauge Chart for Satisfaction Score out of 10
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=running_avg_satisfaction,
                number={"suffix": " / 10", "font": {"size": 22, "color": "#1F2937"}},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Rolling Avg Satisfaction", "font": {"size": 14, "color": "#4B5563"}},
                gauge={
                    "axis": {"range": [0, 10], "tickwidth": 1, "tickcolor": "#6B7280"},
                    "bar": {"color": "#2563EB"},
                    "bgcolor": "white",
                    "borderwidth": 1,
                    "bordercolor": "#E5E7EB",
                    "steps": [
                        {"range": [0, 4], "color": "#FEE2E2"},
                        {"range": [4, 7], "color": "#FEF3C7"},
                        {"range": [7, 10], "color": "#D1FAE5"}
                    ],
                }
            )
        )
        fig_gauge.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # -------------------------------------------------------------------------
    # c), d), & f) LOWER ROW: CATEGORY BAR, LOYALTY DONUT, CORRELATION READOUT
    # -------------------------------------------------------------------------
    col_bar, col_pie, col_corr = st.columns([1.2, 1.2, 1.0])

    with col_bar:
        st.subheader("📊 Category Distribution")
        cat_counts = df["product_category"].value_counts().reset_index()
        cat_counts.columns = ["product_category", "count"]
        
        fig_bar = px.bar(
            cat_counts,
            x="product_category",
            y="count",
            text="count",
            labels={"product_category": "Category", "count": "Transactions"},
            color_discrete_sequence=["#3B82F6"]
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_tickangle=-30,
            paper_bgcolor="white",
            plot_bgcolor="rgba(243, 244, 246, 0.3)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pie:
        st.subheader("🍰 Loyalty Breakdown")
        loyalty_counts = df["loyalty_status"].value_counts().reset_index()
        loyalty_counts.columns = ["loyalty_status", "count"]
        
        fig_pie = px.pie(
            loyalty_counts,
            names="loyalty_status",
            values="count",
            hole=0.4,
            color_discrete_sequence=["#60A5FA", "#2563EB", "#1E40AF"]
        )
        fig_pie.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_corr:
        st.subheader("🔬 Statistical Live Correlation")
        
        # Calculate live Pearson correlation r between income and purchase_amount
        if len(df) > 1 and df["income"].nunique() > 1 and df["purchase_amount"].nunique() > 1:
            pearson_r = df["income"].corr(df["purchase_amount"])
        else:
            pearson_r = 0.0

        st.metric(
            label="Pearson r (Income vs. Purchase)",
            value=f"{pearson_r:.4f}"
        )
        
        st.caption(
            f"""
            **Statistical Insight**:
            As more stream samples arrive ($N = {total_received:,}$), the live correlation coefficient 
            $r$ stabilizes toward **~0.95**, mirroring the strong positive linear relationship found 
            in offline batch analysis.
            """
        )

    st.divider()

    # -------------------------------------------------------------------------
    # g) RECENT TRANSACTIONS TABLE
    # -------------------------------------------------------------------------
    st.subheader("📋 10 Most Recent Received Transactions")
    recent_transactions = df.tail(10).sort_values(by="stream_id", ascending=False)
    
    # Select key display columns
    display_cols = [
        "stream_id", "received_at", "product_category", "purchase_amount",
        "satisfaction_score", "income", "loyalty_status", "region"
    ]
    
    st.dataframe(
        recent_transactions[display_cols].style.format({
            "purchase_amount": "${:,.2f}",
            "income": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
