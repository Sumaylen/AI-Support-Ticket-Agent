import json
from pathlib import Path

import streamlit as st

from app.ticket import get_ticket_lock


LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "final_ticket.json"


def load_tickets():
    with get_ticket_lock():
        entries = json.loads(LOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise ValueError("Expected a list of ticket records")
    return entries


def boolean_label(value, positive, negative):
    if value is True:
        return positive
    if value is False:
        return negative
    return "Not recorded"


def render():
    st.markdown('<div class="desk-label">SUPPORT DESK</div>', unsafe_allow_html=True)
    st.title("Ticket history")
    st.write("Review saved tickets, responses and processing results.")
    st.button("Refresh history", icon=":material/refresh:")

    try:
        tickets = load_tickets()
    except FileNotFoundError:
        st.info("No ticket history yet. Submit a ticket at the support desk to get started.")
        return
    except (ValueError, OSError):
        st.error("Ticket history couldn't be loaded. Please try refreshing in a moment.")
        return

    if not tickets:
        st.info("No ticket history yet. Submit a ticket at the support desk to get started.")
        return

    st.caption(f"{len(tickets)} tickets · Most recently saved first")

    index = st.selectbox(
        "Choose a ticket",
        options=list(reversed(range(len(tickets)))),
        format_func=lambda index: (
            f"#{index + 1} · {tickets[index].get('timestamp', 'Time not recorded')} · "
            f"{str(tickets[index].get('ticket', 'Ticket text not recorded'))[:80]}"
        ),
    )
    ticket = tickets[index]
    with st.container(border=True):
        st.subheader("Ticket details")
        st.caption(f"Saved: {ticket.get('timestamp', 'Not recorded')}")
        st.write(ticket.get("ticket") or "Ticket text not recorded.")
        category, urgency = st.columns(2)
        category.write(f"**Category:** {ticket.get('category') or 'Not recorded'}")
        urgency.write(f"**Urgency:** {ticket.get('urgency') or 'Not recorded'}")
        st.write("**Verification:** " + boolean_label(ticket.get("verification_result"), "Passed", "Failed"))
        st.write("**Escalation:** " + boolean_label(ticket.get("should_escalate"), "Required", "Not required"))
        reasons = ticket.get("escalate_reason")
        if reasons:
            st.write("**Escalation reasons**")
            if isinstance(reasons, list):
                for reason in reasons:
                    st.write(f"• {reason}")
            else:
                st.write(reasons)
        st.subheader("Response")
        st.write(ticket.get("final_response") or "No response recorded.")
        with st.expander("View saved JSON"):
            st.json(ticket)
