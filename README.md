# DealDNA AI — The Revenue Memory Engine

DealDNA AI is a persistent memory-powered revenue intelligence platform designed to eliminate sales knowledge fragmentation. It converts customer interactions into long-term memories via **Hindsight Memory**, discovers recurring win/loss patterns from past outcomes, and recommends evidence-backed next actions.

---

## Key Capabilities (DEALDNA-SRS-001 & DEALDNA-SDD-001)

- **Persistent Memory Lifecycle:** `Ingest` → `Retain` → `Recall` / `Reflect` → `Evidence-Backed Recommendation` → `Outcome Feedback`.
- **Hindsight Memory Layers:**
  - **World Memory:** Durable account, stakeholder, and preference facts.
  - **Experience Memory:** Chronological meeting notes, objections, promises, and events.
  - **Observation Memory:** High-level inferred patterns and win/loss lessons.
- **Agent Orchestrator & Intent Router:**
  - `FACTUAL`: Precision recall of customer facts and verified statements.
  - `SUMMARY`: Contextual deal briefs with current risk analysis.
  - `STRATEGY`: Strategic reflection generating next-best-action with confidence labels and caveats.
  - `PATTERN`: Similar deal surfacing and recurring win/loss relationship discovery.
- **Closed Learning Loop:** Captures `WON`, `LOST`, and `STALLED` outcomes with reasons and strategies, immediately retraining the memory engine for future accounts.
- **Resilient Storage Architecture:** Standard PostgreSQL support with seamless zero-config local SQLite fallback.

---

## Project Structure

```
DealDNA/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app with correlation-id middleware
│   │   ├── config.py                # Environment configuration
│   │   ├── db.py                    # Resilient DB engine (PostgreSQL + SQLite fallback)
│   │   ├── models.py                # 10 core SQLAlchemy models matching SDD
│   │   ├── schemas.py               # Pydantic v2 validation & response contracts
│   │   ├── db_init.py               # Schema initializer & demo seeder
│   │   ├── seed_data.py             # Acme Technologies & historical comparable deals
│   │   ├── api/v1/endpoints/        # Deals, Interactions, Agent, Memory, Companies, Health
│   │   └── modules/
│   │       ├── memory/              # Hindsight Memory Adapter (Retain, Recall, Reflect)
│   │       ├── agents/              # Intent Router, Context Builder, Orchestrator
│   │       ├── deals/               # Deal & Timeline business logic
│   │       └── recommendations/     # Evidence-linked recommendation service
│   └── tests/test_api.py            # Automated acceptance test suite (8 test cases)
├── frontend/
│   ├── src/app/
│   │   ├── deals/                   # Pipeline overview & New Deal modal
│   │   ├── deals/[id]/              # Dynamic Deal Workspace (Timeline, Chat, Recs, Memory)
│   │   ├── dashboard/               # Executive KPI dashboard & demo callout
│   │   ├── memory/                  # Global Hindsight Memory Explorer
│   │   └── assistant/               # Cross-deal AI Revenue Intelligence Chat
├── docs/
│   ├── DEMO.md                      # 9-Step Hackathon Demonstration Script
│   └── architecture-overview.md     # Architectural principles
└── scripts/
    └── seed_demo_data.py            # Data seeding runner
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Initialize database schema and seed the Acme Technologies demo dataset
.venv312\Scripts\python -m app.db_init

# Launch the FastAPI server on port 8000
.venv312\Scripts\uvicorn app.main:app --reload --port 8000
```

The API docs are available at **http://localhost:8000/docs**.

### 2. Run Acceptance Test Suite

```bash
cd backend
.venv312\Scripts\python -m pytest -v tests/test_api.py
```
*Expected: 8 passed.*

### 3. Frontend

```bash
cd frontend
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## Hackathon Demonstration Walkthrough

Follow the step-by-step walkthrough in [docs/DEMO.md](docs/DEMO.md) to showcase **Memory Evolution** on Acme Technologies (`DEAL-1007`).
