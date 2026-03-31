# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Educational hands-on workshop teaching memory-aware AI agents using Oracle AI Database, LangChain, and Tavily. The core deliverable is a **Research Paper Assistant** that searches, retrieves, and reasons over arxiv papers stored as vectors in Oracle AI Database. Delivered primarily through GitHub Codespaces with Jupyter notebooks.

## Environment Setup

The workshop runs inside a DevContainer (GitHub Codespaces or local VS Code). Setup is fully automated:

1. `.devcontainer/setup_build.sh` runs on container creation
2. `.devcontainer/setup_runtime.sh` provisions Oracle AI Database (Docker-in-Docker), starts Ollama, pulls Qwen3-1.7B, creates the VECTOR schema user, configures Vector Memory Area
3. `.devcontainer/start_oracle.sh` starts Oracle and Ollama on container restart
4. Dependencies: `pip install -r requirements.txt`

**Database credentials** (hardcoded for workshop use):
- DSN: `localhost:1521/FREEPDB1`
- SYS password: `OraclePwd_2025`
- VECTOR user password: `VectorPwd_2025`

**LLM**: Qwen3-1.7B served locally by Ollama at `http://localhost:11434`. No cloud API key needed. The `openai` Python SDK is used as the client, pointed at Ollama's OpenAI-compatible endpoint.

**Required API key** (forwarded from local env via `remoteEnv`):
- `TAVILY_API_KEY` (web search)

## Running the Workshop

```bash
# Launch Jupyter (from repo root)
jupyter lab workshop/

# The two notebooks:
# workshop/notebook_student.ipynb   — student version with TODO placeholders
# workshop/notebook_complete.ipynb  — reference solution
```

No formal build system, test suite, or linter. All code lives in notebook cells executed sequentially.

## Workshop Structure (Sequential, Parts 1-6)

| Part | Guide | Focus |
|------|-------|-------|
| 1 | `docs/part-1-oracle-setup.md` | Oracle connection, VECTOR schema, VECTOR column type |
| 2 | `docs/part-2-vector-search.md` | Embeddings, HNSW indexes, similarity search via OracleVS |
| 3 | `docs/part-3-memory-engineering.md` | 6 memory types (short-term, long-term, semantic, episodic, context, procedural), MemoryManager class |
| 4 | `docs/part-4-context-engineering.md` | Summarization, token counting, memory offloading |
| 5 | `docs/part-5-web-search.md` | Tavily API integration for live retrieval |
| 6 | `docs/part-6-agent-execution.md` | Agent harness, before/after comparison |

Parts must be completed in order. Each part builds on the previous one's notebook cells.

## Architecture

```
User Query
    ├── Tavily Web Search (live results)
    ├── Oracle AI Vector Search (embedded arxiv papers via OracleVS/langchain-oracledb)
    └── Memory Retrieval (6 memory types stored in Oracle VECTOR columns)
         │
         ├── Context Engineering (summarize/offload to stay within token limits)
         └── LLM Reasoning (Qwen3-1.7B via Ollama, OpenAI-compatible API)
              └── Response with before/after comparison
```

**Key integration point**: `langchain-oracledb` provides the `OracleVS` vector store, which wraps native Oracle `VECTOR` columns and `VECTOR_DISTANCE()` for similarity search. This replaces external vector databases entirely.

## Key Files

- `workshop/notebook_student.ipynb` — the primary file students (and contributors) modify. 113 cells covering all 6 parts.
- `workshop/notebook_complete.ipynb` — reference implementation. Compare against this when validating changes.
- `.devcontainer/setup_runtime.sh` — Oracle provisioning logic (retry loops, SPFILE config, user creation). Most setup bugs live here.
- `docs/TODO-checklist.md` — 16 numbered tasks mapping to guide sections.

## Patterns to Preserve

- **Least-privilege DB access**: workshop code uses the VECTOR user, not SYS. SYS is only for initial provisioning in setup scripts.
- **Retry logic for Oracle connections**: Docker healthcheck timing means connections need retry loops, not single attempts.
- **Session labeling**: connections set `clientinfo` for debugging (visible in `V$SESSION`).
- **Default model**: `qwen3:1.7b` via Ollama. All LLM calls go through `call_openai_chat()` which uses the `openai` SDK pointed at `localhost:11434/v1`.
