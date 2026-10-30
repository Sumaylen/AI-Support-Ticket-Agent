from threading import Lock

import streamlit as st


@st.cache_resource(show_spinner=False)
def get_ticket_lock():
    return Lock()


def render():
    st.markdown('<div class="desk-label">MERIDIAN GOODS</div>', unsafe_allow_html=True)
    st.title("How can we help?")
    st.write("Tell us what's going on and we'll help you find the next step.")
    with st.form("my_form"):
        st.subheader("Your support ticket")
        st.caption("Include the details we need to understand your issue.")
        text = st.text_area(
            "What do you need help with?",
            placeholder="For example: What are the payment options?",
            height=180,
            max_chars=1000,
            help="If your question is about an order, include your order and account number.",
        )
        submitted = st.form_submit_button(
            "Submit", type="primary", use_container_width=True
        )
    
    if submitted:
        ticket_lock = get_ticket_lock()

        if not text.strip():
            st.warning("Please describe your issue before submitting your ticket.")
        elif not ticket_lock.acquire(blocking=False):
            st.warning("The demo is busy. Please try again shortly.")
        else:
            try:
                st.session_state.pop("support_response", None)
                with st.spinner("Preparing your response…", show_time=True):
                    from src.graph import main
                    response = main(text.strip())
                if response:
                    st.session_state["support_response"] = response
                    st.session_state["submitted_ticket"] = text.strip()
                else:
                    st.error("We couldn't prepare a response. Please try again in a moment.")
            finally:
                ticket_lock.release()
    
    if st.session_state.get("support_response"):
        st.space("small")
        with st.container(border=True):
            st.subheader("Response")
            st.write(st.session_state["support_response"])
            st.warning("Responses are AI-generated and may contain errors.")
            with st.expander("View your ticket"):
                st.write(st.session_state["submitted_ticket"])
    else:
        st.caption("Your response will appear here after you submit a ticket.")
