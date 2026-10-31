import sys
from pathlib import Path


# Streamlit may add only app/ to the import path when running this entrypoint.
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from app.ticket import render as ticket_page
from app.policies import render as policies_page
from app.database import render as database_page
from app.history import render as history_page
from app.evaluation import render as evaluation_page
from app.about import render as about_page
from app.notice import require_demo_acceptance

st.set_page_config(page_title="Support desk", page_icon="💬", layout="centered")

require_demo_acceptance()

#cache avoids repeatdly running the databse initialization
@st.cache_resource(show_spinner="Preparing the policy database...")
def ensure_knowledge_base():
    from build_knowledge_base import main
    main()


ensure_knowledge_base()

st.markdown(
    """
    <style>
        .stMain .block-container { max-width: 820px; padding-top: 3rem; }
        h1 { letter-spacing: -0.04em; }
        div[data-testid="stForm"] { border-radius: 16px; padding: 1.5rem; }
        div[data-testid="stTextArea"] textarea { border-radius: 10px; }
        div[data-testid="stFormSubmitButton"] button { border-radius: 10px; }
        .desk-label {
            color: #64748b; font-size: 0.75rem; font-weight: 700;
            letter-spacing: 0.14em; margin-bottom: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### How to use")
    st.markdown(
        "1. Open Submit a ticket and describe your issue and click submit.\n"
        "2. Browse Company policies or Demo data to verify an answer or find more information.\n"
        "3. Open Ticket history to view processed ticket results."
    )
    st.markdown("#### What you can ask")
    st.write(
        "Ask about company policies, your account or an order. "
        "For account and order questions, use IDs from Demo data."
    )
    st.markdown(
        "**Examples**:\n\n"
        "- What are the payment options?\n"
        "- What plan is account 1013 on?\n"
        "- What is the status of order 4501 for account 1013?\n"
        "- What are the orders for account 1010"
    )

page = st.navigation([
    st.Page(ticket_page, title="Submit a ticket", icon=":material/chat_bubble_outline:", url_path="support", default=True),
    st.Page(policies_page, title="Company policies", icon=":material/menu_book:", url_path="policies"),
    st.Page(database_page, title="Demo data", icon=":material/table_view:", url_path="data"),
    st.Page(history_page, title="Ticket history", icon=":material/history:", url_path="history"),
    st.Page(evaluation_page, title="Evaluation", icon=":material/monitoring:", url_path="evaluation"),
    st.Page(about_page, title="About the demo", icon=":material/info:", url_path="about"),
])
page.run()
