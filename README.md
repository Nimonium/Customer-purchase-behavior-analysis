# 📊 Customer Purchase Behaviour Analysis & Real-Time Analytics Dashboard

> **AI & Statistics Course Project — Avantika University**  
> *A statistical investigation of 100,000 retail customer records extended into a real-time streaming analytics dashboard.*

---

## 📌 Project Overview

This project analyzes a dataset of **100,000 retail customer transactions** through two core phases:

1. **Batch Statistical Analysis**: Descriptive statistics, correlation matrices, hypothesis testing ($\chi^2$ test of independence), and probabilistic analysis (Bayes' theorem).
2. **Real-Time Streaming Analytics Extension**: A process-decoupled system (`simulator.py` + `app.py`) that replays historical CSV data as a live stream into a shared SQLite database (`stream.db`), rendering real-time auto-updating metrics, charts, and correlation convergence on an interactive Streamlit dashboard.

---

## 💡 Key Statistical Findings

* **Income vs. Purchase Amount**: Across all 100,000 records, customer income is the dominant driver of transaction spend ($r = 0.95$, $R^2 = 0.90$).
* **Loyalty Status Independence**: Chi-square independence testing revealed no statistically significant association between customer loyalty tier and purchase frequency ($\chi^2 = 3.15$, $p = 0.53$).
* **Promotion Usage**: Promotional campaigns and coupon usage showed no significant correlation with overall spend or customer satisfaction scores.

---

## 📂 Repository Structure

```text
├── customer_data.csv        # Source dataset (100,000 rows, 12 feature columns)
├── simulator.py             # Replays CSV records as a live transaction stream into SQLite
├── app.py                   # Streamlit dashboard — reads SQLite stream & auto-refreshes
├── requirements.txt         # Dependencies for dashboard & streaming pipeline
├── README.md                # Project documentation & execution guide
└── docs/                    # Analysis reports & presentation decks
```

---

## 📊 Dataset Schema

The dataset contains 100,000 complete customer records across 12 features with zero missing values:

| Column | Type | Range / Options | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | $1 - 100,000$ | Unique customer identifier |
| `age` | Integer | $12 - 49$ | Customer age |
| `gender` | Categorical | `Male`, `Female` | Customer gender |
| `income` | Float | $\$5,000 - \$50,000$ | Annual income |
| `education` | Categorical | `HighSchool`, `College`, `Bachelor`, `Masters` | Highest education level |
| `region` | Categorical | `North`, `South`, `East`, `West` | Geographical region |
| `loyalty_status` | Categorical | `Regular`, `Silver`, `Gold` | Customer loyalty tier |
| `purchase_frequency` | Categorical | `rare`, `occasional`, `frequent` | Buying frequency |
| `purchase_amount` | Float | $\$1,118 - \$26,204$ | Transaction dollar amount |
| `product_category` | Categorical | `Electronics`, `Clothing`, `Books`, `Food`, `Health`, `Home`, `Beauty` | Category purchased |
| `promotion_usage` | Binary | `0` or `1` | Coupon/promotion applied |
| `satisfaction_score` | Integer | $1 - 10$ | Post-purchase satisfaction rating |

---

## ⚡ Running the Real-Time Streaming Dashboard

The dashboard architecture decouples data ingestion (**Producer**: `simulator.py`) from dashboard rendering (**Consumer**: `app.py`) via an SQLite database (`stream.db`) operating in **Write-Ahead Logging (WAL)** mode.

Running the system requires two active terminal windows:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Data Stream Simulator (Terminal 1)
```bash
python simulator.py
```
*Options*:
* `-i` / `--interval`: Set delay between row insertions in seconds (default: `1.0s`). E.g., `python simulator.py -i 0.5`.
* `-s` / `--seed`: Set random seed for dataset shuffling (default: `42`).

### 3. Launch Streamlit Dashboard (Terminal 2)
```bash
streamlit run app.py
```
*The dashboard will automatically open at `http://localhost:8501` and refresh every 2 seconds.*

---

## 🖥️ Dashboard Features

* **Live Top KPIs**: Real-time total transaction count, running average purchase amount, running average satisfaction score, and latest product category.
* **Cumulative Average Trend Line**: Line chart tracking the expanding cumulative average purchase amount over streaming IDs.
* **Rolling Satisfaction Gauge**: Interactive Plotly gauge indicator ($1-10$ score).
* **Live Distribution Visualizations**: Category transaction bar chart and loyalty breakdown donut chart.
* **Live Statistical Correlation Readout**: Dynamically recomputes the Pearson correlation coefficient ($r$) between income and purchase amount on arriving records, demonstrating real-time convergence toward $\approx 0.95$.
* **Manual Transaction Entry Form**: Sidebar form allowing manual submission of live transactions directly into `stream.db` to observe real-time pipeline processing.
* **Stream Reset Control**: One-click database reset button for quick demo resets.

---

## 🎓 Technical Note on "Real-Time" Architecture

> [!NOTE]  
> **Simulation vs. Real-Time Dashboard Mechanics**:  
> `simulator.py` replays existing historical dataset rows sequentially. What is genuinely real-time is the **dashboard system architecture** — automated process separation via SQLite WAL mode, periodic Streamlit execution loops (`st_autorefresh`), cumulative statistics calculation, and live correlation stabilization. This approach models production streaming architectures (e.g., Kafka/Flink pipelines) in a standalone local environment.

---

## 👤 Project Information

* **Course**: AI & Statistics
* **Instructor**: Prof. Kamlesh Ahuja
* **Institution**: Avantika University
* **Authors**:
  * Saptashya Pahari (`PU02424EUG10023`)
  * Manya Chourisya (`PU02424EUG10012`)

---

## 📜 License

Created for academic demonstration and research purposes under the AI & Statistics course curriculum. Not intended for commercial deployment.
