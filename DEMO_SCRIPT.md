# 3-Minute Screen-Recorded Demo Script: DealMindAI

## 5 High-Performing YouTube Titles
1. **I Gave My AI Agent Long-Term Memory (Why Naive RAG Fails)**
2. **Why AI Agents Have Amnesia — And How We Fixed It with Hindsight**
3. **Building an Autonomous Agent with Stateful Memory (Retain, Recall, Reflect)**
4. **Stop Stuffing Prompt Context: How Biomimetic Agent Memory Works**
5. **How We Solved Multi-Month Context Windows in Enterprise AI**

---

## Technical Setup Before You Record

Have these 4 tabs/windows open and pre-loaded:
* **Tab 1**: Deal Workspace: `http://localhost:3000/deals/DEAL-1007`
* **Tab 2**: Hindsight Memory Explorer: `http://localhost:3000/memory`
* **Tab 3**: AI Assistant Strategy Chat: `http://localhost:3000/assistant`
* **Terminal**: In `c:\Users\vishn\Desktop\DealDNA\backend` with virtual environment active

---

## Demo Script & Visual Cues

### Section 1: Quick Intro (0:00 – 0:30)

* **[SCREEN CUE]**: Start on camera, or on the DealMindAI dashboard at `http://localhost:3000`. Show the clean UI with active pipeline opportunities.
* **[NARRATION]**:
  > *"Hey everyone, I'm Vishnu. If you've ever built an LLM agent for enterprise workflows, you know the single biggest point of failure isn't the model's reasoning—it's that the agent has conversational amnesia.
  > 
  > Real B2B sales cycles drag on for three, six, or nine months across multiple decision-makers. But language models forget critical stakeholder objections the moment new notes come in or context windows reset.
  > 
  > To solve this, I built **DealMindAI**—a sales intelligence agent powered by **Hindsight by Vectorize.io** that gives language models persistent, biomimetic memory across long-term deal cycles."*

---

### Section 2: The Problem — The Amnesiac Agent (0:30 – 1:00)

* **[SCREEN CUE]**: Click into the deal page at `http://localhost:3000/deals/DEAL-1007` (Acme Technologies). Scroll through the deal timeline interactions.
* **[NARRATION]**:
  > *"Take a look at this enterprise deal: Acme Technologies, a $175,000 ARR contract.
  > 
  > In an early interaction, their VP of Engineering, Marcus Vance, confirmed DealMindAI passed their SOC2 security audit and approved rollout for Q4.
  > 
  > But three weeks later, CFO Anita Shah jumped on a call and said: 'I will not approve this contract without an executive ROI model proving payback under 12 months, and I need it before our board meeting on October 6th.'
  > 
  > With a standard stateless agent or basic RAG, the model either drowns in chunked tokens or hallucinates generic advice like 'offer a 10% discount.' It misses the hard October 6 deadline and completely fails to connect the VP's security approval with the CFO's pricing hurdle."*

---

### Section 3: Live Demo — Retain, Recall & Reflect in Action (1:00 – 2:30)

* **[SCREEN CUE]**: Navigate to `http://localhost:3000/memory` (Hindsight Memory Explorer). Show the cards filtered by **World**, **Experience**, and **Observation**.
* **[NARRATION]**:
  > *"Here's how we solved this using Hindsight's memory bank: `dealdna`. 
  > 
  > Instead of dumping text into naive vector similarity, memories are organized into three biological layers:
  > - **World Memories**: Verifiable facts like titles, SOC2 status, and firm deadlines.
  > - **Experience Memories**: Actual meeting exchanges, objections, and verbatim notes.
  > - **Observation Memories**: Inferred buyer tendencies and cross-deal patterns."*

* **[SCREEN CUE]**: Switch to the VS Code terminal. Show the code in `backend/app/modules/memory/hindsight_adapter.py` briefly, then execute the live verification suite:
  ```powershell
  .\.venv312\Scripts\python.exe verify_hindsight.py
  ```
* **[NARRATION]**:
  > *"Let's run our live verification suite against the Hindsight Cloud API. Watch what happens:
  > 
  > 1. **Retain**: At ingestion, Hindsight runs background entity resolution and temporal extraction. It automatically extracts 'Marcus Vance', 'Anita Shah', and 'DealDNA' without fragile regex rules.
  > 2. **Recall**: When querying 'Who approved SOC2 and Q4 rollout?', it uses multi-arm retrieval—combining dense vectors, keyword search, and temporal scoring. Look at that reranker score: 1.099.
  > 3. **Reflect**: This is the real breakthrough. Instead of feeding search snippets to an LLM, Hindsight's `/reflect` endpoint executes a cognitive reasoning loop. It deduces that while engineering risk is solved by Marcus Vance, financial sign-off is gated by Anita Shah's October 6 ROI deadline."*

* **[SCREEN CUE]**: Jump back to the browser on the AI Assistant page (`http://localhost:3000/assistant`). In the chat, ask:
  > *"What are the CFO's conditions regarding the ROI model and payback timeline?"*
  Hit enter. Show the response streaming in with zero canned fallbacks.
* **[NARRATION]**:
  > *"Look at the agent's answer in the live UI: It flags the exact 12-month payback requirement and highlights the October 6 deadline, synthesized directly from the Hindsight memory ledger. No prompt stuffing, no lost context."*

---

### Section 4: Wrap-Up & Key Takeaway (2:30 – 3:00)

* **[SCREEN CUE]**: Switch to the GitHub repository at `https://github.com/Vishnu-814271/DealDNA`. Scroll down to the README and architecture overview.
* **[NARRATION]**:
  > *"My biggest engineering takeaway from this build: **Vector similarity alone is blind to time.** A customer saying 'we hate the price' in June shouldn't cancel out 'contract approved' in August. 
  > 
  > Offloading state and temporal memory to a dedicated system like Hindsight transforms brittle chatbots into actual strategic intelligence partners.
  > 
  > The full repository, schema definitions, and verification scripts are open-source on GitHub—check the link below. Thanks for watching!"*
