from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "company.db"


def load_records():
    with closing(sqlite3.connect(DATABASE_PATH.as_uri() + "?mode=ro", uri=True)) as connection:
        accounts = pd.read_sql_query(
            "SELECT account_id, email, plan FROM accounts ORDER BY account_id", connection
        )
        orders = pd.read_sql_query(
            "SELECT order_id, account_id, item, status, expected_delivery "
            "FROM orders ORDER BY order_id", connection
        )
    return accounts, orders


def render():
    st.markdown('<div class="desk-label">MERIDIAN GOODS</div>', unsafe_allow_html=True)
    st.title("Demo data")
    st.write(
        "Browse accounts and orders to try out the support desk. "
        "Include an account ID and its order ID in your ticket to ask about an order."
    )
   
    try:
        accounts, orders = load_records()
    except (sqlite3.Error, pd.errors.DatabaseError):
        st.error("The demo records are currently unavailable. Please try again later.")
        return

    query = st.text_input(
        "Search records",
        placeholder="Search by account ID, order ID, item, email or status",
    ).strip()
    account_tab, order_tab = st.tabs(["Accounts", "Orders"])
    for tab, records, label in (
        (account_tab, accounts, "accounts"),
        (order_tab, orders, "orders"),
    ):
        with tab:
            if query:
                matches = records.astype(str).apply(
                    lambda column: column.str.contains(query, case=False, regex=False)
                ).any(axis=1)
                records = records.loc[matches]
            st.caption(f"Showing {len(records)} {label}")
            if records.empty:
                st.info("No records match your search. Try another search or clear the field.")
            else:
                st.dataframe(
                    records,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "account_id": st.column_config.NumberColumn("Account ID", format="%d"),
                        "order_id": st.column_config.NumberColumn("Order ID", format="%d"),
                        "email": "Email",
                        "plan": "Plan",
                        "item": "Item",
                        "status": "Status",
                        "expected_delivery": "Expected delivery",
                    },
                )
