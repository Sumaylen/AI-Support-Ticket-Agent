# AI Support Ticket Agent (WIP)
**This project involves an AI agent that classifies support tickets, retrieves relevant context using RAG and either drafts fact-checked responses or escalates to a human if necessary.**

## Progress
- Phase 0 - Set up local LLM + Groq ✅
- Phase 1 - Database setup ✅
- Phase 2 - Retrieval + RAG pipeline
- Phase 3 - Ticket workflow + agent logic
- Phase 4 - UI/UX + testing
- Phase 5 - Deployment + polish

## Setup
**Note:** You run setup.bat once to create the virtual environment, download the neccessary requirements and to create & populate the database
1. Run `setup.bat`.
2. This creates a local `.env` if needed.
3. Edit `.env` and set your API key. If you do not already have one, get one here: https://console.groq.com/

```env
GROQ_API_KEY=your_key_here
LLM_BACKEND=groq
```

## Optional: run locally with llama.cpp

If you want to use a local model instead:

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
