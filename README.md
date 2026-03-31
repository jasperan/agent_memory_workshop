# Oracle Agent Memory Workshop

**Build memory-aware AI agents with Oracle AI Database, LangChain, and Tavily**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/speechlyze/agent_memory_workshop)

---

## What You Will Build

A **Research Paper Assistant** — an AI agent that searches, retrieves, and reasons over arxiv papers stored as vectors in Oracle AI Database. Along the way you'll implement a `MemoryManager` with six memory types, context engineering techniques that prevent context window overflow, and a turn-level agent harness — finishing with a before/after comparison that makes the impact of memory engineering visible.

## Workshop Parts

| Part | Topic | Guide |
|---|---|---|
| 1 | Oracle AI Database setup and connection | [Part 1 Guide](docs/part-1-oracle-setup.md) |
| 2 | Vector search with LangChain OracleVS | [Part 2 Guide](docs/part-2-vector-search.md) |
| 3 | Memory engineering: 6 memory types in Oracle | [Part 3 Guide](docs/part-3-memory-engineering.md) |
| 4 | Context engineering: summarisation and offloading | [Part 4 Guide](docs/part-4-context-engineering.md) |
| 5 | Web access with Tavily | [Part 5 Guide](docs/part-5-web-search.md) |
| 6 | Agent execution and memory vs no-memory comparison | [Part 6 Guide](docs/part-6-agent-execution.md) |

> **[TODO Checklist](docs/TODO-checklist.md)** — all 16 tasks at a glance with links to their guide sections.

## Getting Started

### Option A: GitHub Codespaces (recommended for the workshop)

1. Click the **Open in GitHub Codespaces** badge above
2. Click the **Create Codespace** button to launch your environment

   ![Create Codespace](images/codespaces_creation.png)

3. Wait for the environment to build (~3-5 minutes)

   ![Codespace startup](images/codespace_startup.png)

4. Once the terminal prompt appears, start Oracle AI Database:

   > **Tip:** If your browser prompts you to allow clipboard pasting, click **Allow** so you can paste commands into the terminal.

   ```bash
   docker compose -f .devcontainer/docker-compose.yml up -d oracle
   ```

   ![Oracle getting pulled](images/oracle_getting_pulled.png)

5. Wait for Oracle to become healthy (~60-90 seconds), then verify:
   ```bash
   docker ps
   ```
   You should see `(healthy)` in the STATUS column for the `oracle-free` container.

   ![Oracle ready](images/oracle_ready.png)

6. Confirm the Python connection works:
   ```bash
   python3 -c "import oracledb; c = oracledb.connect(user='VECTOR', password='VectorPwd_2025', dsn='localhost:1521/FREEPDB1'); print('Connected. Oracle version:', c.version); c.close()"
   ```

   ![Database ready](images/database_ready.png)

7. Open [`workshop/notebook_student.ipynb`](workshop/notebook_student.ipynb) in the file explorer
8. Select the **Python 3** kernel from the top-right kernel picker
9. Follow the notebook cells top to bottom, using the part guides in `docs/` when you hit a TODO

You will need:
- A GitHub account (free)
- A `TAVILY_API_KEY` for web search — pre-configured as a Codespace environment variable
- The LLM (Qwen3-1.7B) runs locally via Ollama — no cloud API key needed

> **Note:** On subsequent Codespace opens, Oracle should start automatically via `postStartCommand`. If you ever see a connection error in the notebook, run step 3 above again from the terminal.

### Option B: Local development

```bash
git clone https://github.com/YOUR-ORG/agent-memory-workshop
cd agent-memory-workshop

# Start Oracle AI Database
docker compose -f .devcontainer/docker-compose.yml up -d oracle

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter lab workshop/notebook_student.ipynb
```

Wait approximately 2 minutes for Oracle to initialise before running notebook cells.

## Workshop Files

```
agent-memory-workshop/
├── .devcontainer/
│   ├── devcontainer.json     Codespaces configuration
│   ├── docker-compose.yml    Oracle AI Database + workshop container
│   └── setup.sh              Dependency installation and Oracle health check
├── workshop/
│   ├── notebook_student.ipynb   Your working notebook (contains TODO gaps)
│   └── notebook_complete.ipynb  Complete reference (do not open until done)
├── docs/
│   ├── part-1-oracle-setup.md
│   ├── part-2-vector-search.md
│   ├── part-3-memory-engineering.md
│   ├── part-4-context-engineering.md
│   ├── part-5-web-search.md
│   └── part-6-agent-execution.md
└── README.md
```

## Stack

- Oracle AI Database via `gvenzl/oracle-free`
- `langchain-oracledb` — LangChain integration for Oracle vector store
- `sentence-transformers` — local embedding model, no API key needed
- `ollama` + `openai` SDK — local LLM inference (Qwen3-1.7B) via OpenAI-compatible API
- `tavily-python` — web search for agents
- `oracledb` — Python Oracle driver

## Presentation Slides

A PDF version of the workshop presentation is available at [`docs/agent_memory_presentation.pdf`](docs/agent_memory_presentation.pdf) for learners who want to follow along or review the material offline.

## Where to Next?

- **[Agent Memory: Building Memory-Aware Agents](https://www.deeplearning.ai/short-courses/agent-memory-building-memory-aware-agents/)** — DeepLearning.AI short course for deeper exploration of agent memory patterns
- **[Oracle AI Developer Hub](https://github.com/oracle-devrel/oracle-ai-developer-hub)** — More technical assets, samples, and projects with Oracle AI
- **[Oracle Developer Resource](https://www.oracle.com/developer/)** — Documentation, tools, and community for Oracle developers

---

Built for the Oracle AI Developer Experience team.
