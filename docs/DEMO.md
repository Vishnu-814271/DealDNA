# DealDNA AI — Hackathon Demonstration Guide

This guide walks through the exact 9-step demo scenario defined in **DEALDNA-SDD-001 Section 28** to showcase **Memory Evolution** and the **Closed Learning Loop**.

---

## 1. Prerequisites & Startup

### Start Backend
```bash
cd backend
.venv312\Scripts\activate   # or source .venv/bin/activate
python -m app.db_init       # Creates DB schema and seeds Acme + historical deals
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 2. The 9-Step Demo Walkthrough

### Context
* **Target Account:** Acme Technologies (`DEAL-1007`)
* **Deal Value:** $175,000 (Stage: `EVALUATION`, Probability: 65%)
* **Stakeholders:** Raj Mehta (VP Procurement), Anita Shah (CFO)
* **Pre-seeded Timeline Interactions:**
  1. *Meeting:* "We are interested, but your pricing is higher than Competitor X."
  2. *Call:* "Our CFO needs to understand ROI before allocating budget for Q4."
  3. *Email:* "Send us a relevant case study showing similar companies succeeding with this approach."

---

### Step 1: Open Deal Workspace
1. Navigate to **Deals** (`/deals`).
2. Click on **Acme Enterprise Platform Expansion** (`DEAL-1007`).
3. Observe the deal header, financial stats ($175k, 65%), and primary stakeholders.

### Step 2: Inspect Timeline & Verified Memory
1. Under the **Timeline** tab, review the 3 chronological interactions.
2. Note that each interaction is marked `Hindsight: SYNCED` with a document ID.
3. Switch to the **Memory Explorer** tab:
   * **World Memory:** Identifies Anita Shah (CFO) as the economic buyer requiring quantifiable ROI.
   * **Experience Memory:** Captures the explicit request for a case study.
   * **Observation Memory:** Inferred pricing sensitivity benchmarked against Competitor X.

### Step 3: Factual Query (Recall)
1. Switch to the **AI Agent Chat** tab.
2. Click the quick query button: *"What do you know about Acme?"*
3. **Expected Result:** The agent classifies intent as **`FACTUAL`** and recalls exact company facts, stakeholder roles, and objections without fabricating unsupported claims. Cites supporting interaction IDs.

### Step 4: Similar Deals & Win/Loss Patterns (Historical Learning)
1. Click the quick query button: *"Find similar deals and outcomes"* (or switch to the **Historical Patterns** tab).
2. **Expected Result:** Intent is **`PATTERN`**. The agent presents comparable historical accounts (e.g. Globex Corp, Initech, Cyberdyne) showing:
   * **Won Deals:** Closed after delivering customized CFO ROI models and customer proof points.
   * **Lost Deals:** Cyberdyne offered generic discounts without ROI validation and lost to Competitor X.

### Step 5: Strategic Next-Best-Action (Reflect)
1. In the chat, ask: *"What should I do next?"*
2. **Expected Result:** Intent is **`STRATEGY`**.
   * Confidence Label: **`supported`**
   * Recommendation: Prepare executive ROI validation memo for the CFO and deliver the requested case study.
   * Caveat: Avoid unilateral discounting before total cost of ownership is understood.
   * Cites exact interaction IDs as supporting evidence.

### Step 6: Memory Evolution (Ingesting a New Interaction)
1. Click **+ Ingest Interaction** (or use the button on the Timeline tab).
2. Enter:
   * **Type:** `MEETING`
   * **Participants:** `Anita Shah, Sarah Jenkins`
   * **Content:** `Anita Shah (CFO) reviewed our initial ROI memo. She requested a customized 3-year TCO model comparing direct labor savings against Competitor X before tomorrow's committee call.`
3. Click **Retain to Memory**.
4. Observe the interaction appear immediately on the timeline with `Hindsight: SYNCED`.

### Step 7: Demonstrate Updated Contextual Reasoning
1. Return to the **AI Agent Chat** tab and ask again: *"What should I do next?"*
2. **Demonstrated Proof of Evolution:** The agent now dynamically adapts its recommendation to focus on the 3-year TCO labor model for tomorrow's committee call, referencing the brand-new interaction as primary evidence.

### Step 8: Close the Learning Loop (Record Outcome)
1. Click **Record Outcome**.
2. Select **Status:** `WON`.
3. Enter Reason: `Delivered 3-year TCO labor savings model and peer benchmark case study directly to Anita Shah (CFO).`
4. Enter Strategy: `Executive ROI walkthrough + customer case study`.
5. Click **Record Outcome & Learn**.
6. The deal status updates to `WON`, and the outcome is retained as a permanent learning signal in Hindsight Observation Memory for future deals.

---

## 3. Verifying Acceptance Tests
To run the automated suite testing all acceptance criteria:
```bash
cd backend
.venv312\Scripts\python -m pytest -v tests/test_api.py
```
Expected result: **8 passed, 100% success**.
