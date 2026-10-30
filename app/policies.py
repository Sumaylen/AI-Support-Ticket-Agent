from pathlib import Path

import streamlit as st

from app.ticket import render as ticket_page


POLICY_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "policies"


def render():
    st.markdown('<div class="desk-label">MERIDIAN GOODS</div>', unsafe_allow_html=True)
    st.title("Company policies")
    st.write(
        "Find the details on orders, refunds, shipping and your account. "
        "Check a response or browse before sending us a question."
    )
    st.page_link(
        st.Page(ticket_page, title="Support desk", url_path="support", default=True),
        label="Ask a question at the support desk",
        icon=":material/chat_bubble_outline:",
    )
    st.space("small")

    query = st.text_input(
        "Search policies",
        placeholder="Try refunds, delivery or payment methods",
    )
    policies = []
    for path in sorted(POLICY_DIRECTORY.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        heading, _, body = content.partition("\n")
        title = heading.lstrip("# ").strip()
        policies.append((title, body.strip(), content))

    if not policies:
        st.info("Company policies are currently unavailable. Please try again later.")
        return

    terms = query.casefold().split()
    matches = [
        (title, body)
        for title, body, content in policies
        if all(term in content.casefold() for term in terms)
    ]
    st.caption(f"{len(matches)} of {len(policies)} policies")
    if not matches:
        st.info("No policies match your search. Try a different word or clear the search to browse all policies.")
        return

    for title, body in sorted(matches):
        with st.expander(title, expanded=bool(terms)):
            st.markdown(body)
