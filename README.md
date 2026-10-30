# AI Support Ticket Agent (WIP)
**This project involves an AI agent that classifies support tickets, retrieves relevant context using RAG and either drafts fact-checked responses or escalates to a human if necessary.**

## Progress
- Phase 0 - Set up local LLM + Groq ✅
- Phase 1 - Database setup ✅
- Phase 2 - Retrieval + RAG pipeline ✅
- Phase 3 - Ticket workflow + agent logic ✅
- Phase 4 - UI/UX + testing
- Phase 5 - Deployment + polish

## Setup
**Python 3.14.7** was used for this project.

**Note:** You run setup.bat once to create the virtual environment, download the necessary requirements, and create & populate the database.
1. Run `setup.bat`.
2. This creates a local `.env` if needed.
3. Edit `.env` and set your API key. If you do not already have one, get one here: https://console.groq.com/

### Use the Groq model

Model: `qwen/qwen3.8-27b`

```env
GROQ_API_KEY=your_key_here
LLM_BACKEND=groq
```

> Warning: this setup was validated with the tested model above. Other models may require different configuration, tuning, or prompt adjustments and are not guaranteed to work correctly.

## Run the dashboard

From the project root, using the Python environment created during setup, run:

```powershell
python -m streamlit run app/dashboard.py
```

The `app` folder contains the dashboard, support ticket page, company policies page and a read-only demo data page for browsing accounts and orders. Ticket history displays saved records from `logs/final_ticket.json`, including responses, verification and escalation results. The About the demo page displays the Mermaid workflow diagram from this README, explains the workflow and describes the demo's limitations and how submitted messages are saved.

## Run the ticket workflow

From the project root, using the Python environment created during setup, run:

```powershell
python -m src.graph
```

Run this as a module so Python can resolve the `src.*` imports. Running `python src/graph.py` directly can cause `ModuleNotFoundError: No module named 'src'`.

## Optional: run locally with llama.cpp

Model: `Qwen_Qwen3.5-4B-Q4_K_M`

1. Install llama.cpp into the root directory from the official repo: https://github.com/ggml-org/llama.cpp/releases
2. Put your GGUF model in `model\`.
3. Update `.env`:

```env
LLM_BACKEND=local
```

5. Start the server:

```bat
run.bat
```

> Warning: this setup was validated with the tested model above. Other models may require different configuration, tuning, or prompt adjustments and are not guaranteed to work correctly.

## Evaluation

The Evaluation page charts classification accuracy across three saved runs, each containing 269 tickets. It appears between Ticket history and About the demo in the dashboard navigation.

### Classification results

| Version | Change | Passed | Failed | Accuracy |
| --- | --- | ---: | ---: | ---: |
| v1 | Qwen 27B baseline; strict JSON schema output disabled | 201 | 68 | 74.72% |
| v2 | GPT-OSS 120B; strict JSON schema output enabled | 223 | 46 | 82.90% |
| v3 | GPT-OSS 120B with classifier prompt adjustments | 241 | 28 | 89.59% |

### Summary

The model and output configuration change in v2 increased accuracy by 8.18 percentage points. Prompt adjustments in v3 clarified commonly confused categories and increased accuracy by a further 6.69 percentage points. These runs measure category classification, not end-to-end response accuracy.

### Raw evaluation logs

- [v1: Qwen 27B baseline](logs/EVALUATE_CLASSIFIER_QWEN_27B_STRICT_FALSE_v1.txt)
- [v2: GPT-OSS 120B with strict output](logs/EVALUATE_CLASSIFIER_GPT_120B_STRICT_TRUE_v2.txt)
- [v3: GPT-OSS 120B with prompt adjustments](logs/EVALUATE_CLASSIFIER_GPT_120B_STRICT_TRUE_v3.txt)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '16px',
    'primaryTextColor': '#f8fafc',
    'secondaryTextColor': '#e2e8f0',
    'tertiaryTextColor': '#f8fafc',
    'lineColor': '#a78bfa',
    'primaryColor': '#1f2937',
    'primaryBorderColor': '#c4b5fd',
    'secondaryColor': '#312e81',
    'tertiaryColor': '#1e1b4b',
    'clusterBkg': '#0f172a',
    'clusterBorder': '#a78bfa'
  },
  'flowchart': {
    'curve': 'linear',
    'nodeSpacing': 35,
    'rankSpacing': 45,
    'padding': 18
  }
}}%%
graph TD;
        __start__([<p>__start__</p>]):::first
        prompt_guard(prompt_guard)
        llm_prompt_guard(llm_prompt_guard)
        blocked(blocked)
        classify(classify)
        requires_lookup(requires_lookup)
        lookup(lookup)
        invalid_lookup(invalid_lookup)
        retrieve(retrieve)
        response(response)
        should_escalate(should_escalate)
        escalate(escalate)
        __end__([<p>__end__</p>]):::last
        __start__ --> prompt_guard;
        classify -. &nbsp;blocked_route&nbsp; .-> blocked;
        classify -. &nbsp;continue_route&nbsp; .-> requires_lookup;
        invalid_lookup --> should_escalate;
        llm_prompt_guard -. &nbsp;blocked_route&nbsp; .-> blocked;
        llm_prompt_guard -. &nbsp;continue_route&nbsp; .-> classify;
        lookup -. &nbsp;invalid_route&nbsp; .-> invalid_lookup;
        lookup -. &nbsp;retrieve_route&nbsp; .-> retrieve;
        lookup -. &nbsp;escalate_route&nbsp; .-> should_escalate;
        prompt_guard -. &nbsp;blocked_route&nbsp; .-> blocked;
        prompt_guard -. &nbsp;continue_route&nbsp; .-> llm_prompt_guard;
        requires_lookup -. &nbsp;lookup_route&nbsp; .-> lookup;
        requires_lookup -. &nbsp;retrieve_route&nbsp; .-> retrieve;
        response --> should_escalate;
        retrieve --> response;
        should_escalate -. &nbsp;end_route&nbsp; .-> __end__;
        should_escalate -. &nbsp;escalate_route&nbsp; .-> escalate;
        blocked --> __end__;
        escalate --> __end__;

        classDef default fill:#1f2937,stroke:#c4b5fd,stroke-width:2.5px,color:#f8fafc,rx:12,ry:12;
        classDef first fill:#0f172a,stroke:#c4b5fd,stroke-width:2.5px,color:#f8fafc;
        classDef last fill:#312e81,stroke:#c4b5fd,stroke-width:2.5px,color:#f8fafc;
```
