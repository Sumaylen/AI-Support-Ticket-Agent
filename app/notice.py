import streamlit as st


@st.dialog("Before you use this demo", dismissible=False)
def show_demo_notice():
    st.write(
        "This is a project demo. The company, policies and account/order "
        "information are entirely fictional."
        "Any resemblance to real companies, individuals or transactions is purely coincidental."
    )
    st.write(
        "Submitted messages are saved and may be viewed "
        "by anyone in Ticket history."
    )
    st.write(
        "Do not enter any personal or sensative information."
    )
    if st.button("I understand", type="primary", width="stretch"):
        st.session_state["demo_notice_accepted"] = True
        st.rerun()


def require_demo_acceptance():
    if not st.session_state.get("demo_notice_accepted", False):
        show_demo_notice()
        st.stop()
