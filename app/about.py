from html import escape
from pathlib import Path

import streamlit as st


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def render_workflow_diagram():
    readme = README_PATH.read_text(encoding="utf-8")
    diagram = readme.split("```mermaid", 1)[1].split("```", 1)[0].strip()
    st.iframe(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <style>
                body {{ margin: 0; padding: 20px; background: #0f172a;
                        color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif;
                        border-radius: 16px; }}
                #workflow-diagram svg {{ display: block; width: 100%; height: auto; }}
                pre {{ overflow-x: auto; }}
            </style>
        </head>
        <body>
            <p id="diagram-status" role="status">Loading workflow diagram...</p>
            <div id="workflow-diagram"></div>
            <pre id="diagram-source" hidden>{escape(diagram)}</pre>
            <script type="module">
                const status = document.getElementById('diagram-status');
                const source = document.getElementById('diagram-source');
                try {{
                    const {{ default: mermaid }} = await import(
                        'https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs'
                    );
                    mermaid.initialize({{ startOnLoad: false, securityLevel: 'strict' }});
                    const {{ svg }} = await mermaid.render('workflow-svg', source.textContent);
                    document.getElementById('workflow-diagram').innerHTML = svg;
                    status.hidden = true;
                }} catch (error) {{
                    status.textContent = "The diagram couldn't load. Its Mermaid source is shown below.";
                    source.hidden = false;
                }}
            </script>
        </body>
        </html>
        """,
        height="content",
        alt="Support ticket workflow, from request checks through retrieval, response verification and escalation",
    )


def render():
    st.markdown('<div class="desk-label">MERIDIAN GOODS</div>', unsafe_allow_html=True)
    st.title("About the demo")
    st.write(
        "This project is a demo of an autonomous AI powered ticketing system, " \
        "utilizing Retrieval-Augmented Generation (RAG) and agentic capabilities " \
        "to resolve customer queries with information grounded in company policies and databases."
    )
    st.info(
        "Mermaid diagram of the ticket system workflow"
    )

    render_workflow_diagram()

    st.subheader("How it works")
    st.markdown(
        "1. **Check the request.** The agent checks for attempts to override its "
        "instructions and rejects requests outside its support scope.\n"
        "2. **Understand the ticket.** It categorizes the ticket and determines its urgency.\n"
        "3. **Find relevant information.** It retrieves relevant company policy extracts "
        "and can look up information from a database if deemed necessary.\n"
        "4. **Draft and check a response.** It uses the retrieved information "
        "to draft an answer, then self evaluates whether the sources support it.\n"
        "5. **Record the outcome.** It saves the response and processing results, "
        "including whether the ticket requires human review."
    )

    st.subheader("Limitations")
    st.markdown(
            "- Strict rate limits on the free groq plan means that the demo is not suitable "
            "for multi-user use or high traffic usage.\n"
            "- Each submission is processed independently, so follow-up "
            "questions must include the relevant details again.\n"
            "- Escalation is recorded for demonstration purposes. It does not "
            "contact a real support team.\n"
            "- AI-generated answers and its self verification check can both make "
            "mistakes."
        )

    st.subheader("AI usage")
    st.markdown(
        "AI tools assisted with: \n\n" 
        "- Creating fictional company policies and demo data. \n" 
        "- Building the frontend. \n" 
        "- Drafting evaluation test cases. \n"
        "- Generating system prompts. \n" 
        "- Reviewing human-written code. \n\n"
        "I designed and implemented most of the backend, including the RAG system, " \
        "agent tool-calling capabilities, Langgraph workflow and the evaluation tests."
    )
