"""Orders dashboard - sample data."""

import duckdb
import pandas as pd
import streamlit as st

from _common import page_header, kpi_row, aggrid_table

@st.cache_data
def load_orders() -> pd.DataFrame:
    con = duckdb.connect()
    return con.execute("""
        SELECT
            i                                       AS order_id,
            (i % 500) + 1                           AS customer_id,
            DATE '2025-01-01' + INTERVAL (i % 365) DAY AS order_date,
            ROUND(50 + random() * 950, 2)           AS amount,
            (ARRAY['north','south','east','west'])[1 + (i % 4)] AS region
        FROM range(1, 5001) t(i)
    """).fetchdf()

page_header("Orders dashboard", "Sample data - replace with your own table.")
df = load_orders()

kpi_row([
    ("Orders", f"{len(df):,}"),
    ("Total sales", f"${df['amount'].sum():,.0f}"),
    ("Average order", f"${df['amount'].mean():,.2f}"),
    ("Regions", str(df["region"].nunique())),
])
st.divider()

c1, c2, c3 = st.columns(3)
region = c1.multiselect("Region",
                        options=sorted(df["region"].unique()),
                        default=sorted(df["region"].unique()))
min_amount = c2.slider("Min amount", 0, 1000, 0, step=50)
date_range = c3.date_input("Order date range",
                           value=(df["order_date"].min(), df["order_date"].max()))

mask = (df["region"].isin(region)
        & (df["amount"] >= min_amount)
        & (df["order_date"].between(*date_range)))
filtered = df.loc[mask]

st.subheader("Orders")
st.caption(f"{len(filtered):,} rows match the filters.")
aggrid_table(filtered, page_size=25)

st.subheader("Daily sales")
daily = (filtered.groupby("order_date", as_index=False)["amount"]
         .sum().sort_values("order_date"))
st.line_chart(daily, x="order_date", y="amount")

st.subheader("Sales by region")
by_region = (filtered.groupby("region", as_index=False)["amount"]
             .sum().sort_values("amount", ascending=False))
st.bar_chart(by_region, x="region", y="amount")