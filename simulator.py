"""
===============================================================================
SIMULATOR.PY — Live Transaction Stream Simulator
===============================================================================
Course: AI & Statistics — Customer Purchase Behaviour Analysis Project

NOTE FOR REPORT / VIVA:
This script simulates a live data stream by replaying historical customer data 
from 'customer_data.csv' row-by-row into a SQLite database (stream.db). 
The data feed itself is a SIMULATED REPLAY of historical records, while the 
"real-time" aspect comes from the streaming mechanics (sequential insertion, 
timestamps, and rolling analytics in the Streamlit dashboard).
===============================================================================
"""

import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime
import pandas as pd


def parse_arguments():
    """Parse command line arguments for interval and seed."""
    parser = argparse.ArgumentParser(
        description="Simulate a live transaction stream by replaying customer_data.csv into SQLite."
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Delay between row insertions in seconds (default: 1.0s)"
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=42,
        help="Fixed random seed for reproducible dataset shuffling (default: 42)"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="customer_data.csv",
        help="Path to historical CSV dataset (default: customer_data.csv)"
    )
    return parser.parse_args()


def init_database(db_path="stream.db"):
    """
    Initialize SQLite database and create live_transactions table.
    Drops existing table on startup so each run starts fresh.
    Configures Write-Ahead Logging (WAL) for safe concurrent reads from Streamlit.
    """
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    
    # Enable WAL (Write-Ahead Logging) mode for concurrent read/write operations
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    # Drop table if exists to start fresh on every run
    cursor.execute("DROP TABLE IF EXISTS live_transactions;")
    
    # Create target table schema matching customer_data.csv plus metadata columns
    create_table_sql = """
    CREATE TABLE live_transactions (
        stream_id INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        age INTEGER,
        gender TEXT,
        income REAL,
        education TEXT,
        region TEXT,
        loyalty_status TEXT,
        purchase_frequency TEXT,
        purchase_amount REAL,
        product_category TEXT,
        promotion_usage INTEGER,
        satisfaction_score INTEGER,
        received_at TEXT
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()
    print(f"Database '{db_path}' initialized successfully. Table 'live_transactions' ready.")


def stream_data(csv_path, interval, seed, db_path="stream.db"):
    """
    Reads CSV, shuffles rows reproducibly using a fixed seed, and streams 
    one row into SQLite every `interval` seconds indefinitely.
    """
    if not os.path.exists(csv_path):
        print(f"Error: Dataset '{csv_path}' not found. Please ensure it is in the working directory.")
        sys.exit(1)

    print(f"Loading dataset '{csv_path}'...")
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"Loaded {total_rows:,} rows. Shuffling dataset with seed={seed}...")

    # Shuffle dataset reproducibly
    shuffled_df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    print(f"\n🚀 Starting live transaction stream (Interval: {interval}s per row)...")
    print("Press Ctrl+C to stop simulation cleanly.\n")

    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()

    row_index = 0
    loop_count = 1

    try:
        while True:
            # Loop back to beginning if dataset end is reached
            if row_index >= total_rows:
                row_index = 0
                loop_count += 1
                print(f"\n--- Reached end of dataset. Starting loop #{loop_count} ---\n")

            row = shuffled_df.iloc[row_index]
            now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert row into SQLite
            insert_sql = """
            INSERT INTO live_transactions (
                id, age, gender, income, education, region,
                loyalty_status, purchase_frequency, purchase_amount,
                product_category, promotion_usage, satisfaction_score, received_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            try:
                cursor.execute(insert_sql, (
                    int(row['id']),
                    int(row['age']),
                    str(row['gender']),
                    float(row['income']),
                    str(row['education']),
                    str(row['region']),
                    str(row['loyalty_status']),
                    str(row['purchase_frequency']),
                    float(row['purchase_amount']),
                    str(row['product_category']),
                    int(row['promotion_usage']),
                    int(row['satisfaction_score']),
                    now_timestamp
                ))
                conn.commit()
            except sqlite3.OperationalError:
                print("\nTable not found — it may have been reset from the dashboard. Recreating table and continuing...")
                conn.close()
                init_database(db_path)
                conn = sqlite3.connect(db_path, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                continue
            
            stream_id = cursor.lastrowid
            category = row['product_category']
            amount = float(row['purchase_amount'])

            # Log progress line to console
            print(f"Row {stream_id} inserted — {category}, ${amount:,.2f}")

            row_index += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n🛑 Simulation stopped cleanly by user (Ctrl+C).")
        print(f"Total rows inserted into '{db_path}': {stream_id if 'stream_id' in locals() else 0}")
    finally:
        conn.close()


if __name__ == "__main__":
    args = parse_arguments()
    init_database("stream.db")
    stream_data(
        csv_path=args.csv,
        interval=args.interval,
        seed=args.seed,
        db_path="stream.db"
    )
