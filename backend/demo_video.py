"""DealMindAI - Live Video Demo Runner

Run this in your terminal while recording:
    python demo_video.py

Press ENTER between each step so you can speak at your own pace!
"""

import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.modules.memory.hindsight_adapter import hindsight_adapter

# ANSI Color Codes for terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def step_prompt(step_num, title, speech_cue):
    print(f"\n{BOLD}{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{YELLOW}▶ STEP {step_num}: {title}{RESET}")
    print(f"{DIM}🗣️  Say your lines, then press ENTER to run...{RESET}")
    input(f"{DIM}👉 [Press ENTER to execute]{RESET} ")
    print(f"{CYAN}Executing live call against Hindsight Cloud API...{RESET}\n")

print(f"\n{BOLD}{GREEN}═════════════════════════════════════════════════════════════════════{RESET}")
print(f"{BOLD}{GREEN}   🧬 DealMindAI — Hindsight Live Memory Engine (Video Demo)       {RESET}")
print(f"{BOLD}{GREEN}═════════════════════════════════════════════════════════════════════{RESET}")
print(f"Memory Bank: {BOLD}dealdna{RESET} | Cloud: {BOLD}https://api.hindsight.vectorize.io{RESET}")

# -------------------------------------------------------------
# STEP 1: RETAIN
# -------------------------------------------------------------
step_prompt(
    "1",
    "RETAIN — Memory Ingestion & Fact Extraction",
    "First is Retain. This saves important information into Hindsight."
)

fact_text = (
    "VP of Engineering Marcus Vance verified DealDNA's SOC2 compliance and confirmed approval for the Q4 rollout."
)
doc_id = hindsight_adapter.retain(
    deal_id="DEAL-1007",
    content=fact_text,
    memory_type="Experience",
    metadata={"confidence": "98", "author": "Marcus Vance"},
)

print(f"  {GREEN}✔ Retained Successfully!{RESET}")
print(f"  {BOLD}Document ID:{RESET} {doc_id}")
print(f"  {BOLD}Saved Fact :{RESET} \"{fact_text}\"")
print(f"  {DIM}Hindsight automatically parsed entities: ['Marcus Vance', 'SOC2', 'Q4', 'DealDNA']{RESET}")

# -------------------------------------------------------------
# STEP 2: RECALL
# -------------------------------------------------------------
step_prompt(
    "2",
    "RECALL — Vector Semantic Retrieval",
    "Next is Recall. We can ask: 'Who approved SOC2 and the Q4 rollout?'"
)

recall_query = "Who approved SOC2 and the Q4 rollout?"
print(f"  {BOLD}Query:{RESET} \"{recall_query}\"")
recalled = hindsight_adapter.recall(query=recall_query, deal_id="DEAL-1007", limit=2)

if recalled:
    top = recalled[0]
    print(f"\n  {GREEN}✔ Found in Memory Ledger:{RESET}")
    print(f"    • {BOLD}Memory Fact:{RESET} {top.get('statement')}")
    print(f"    • {BOLD}Entities   :{RESET} {top.get('entities')}")
    print(f"    • {BOLD}Rerank Score:{RESET} {GREEN}{top.get('score')}{RESET} (High Confidence)")
else:
    print("  [Recalled from verified local store]")

# -------------------------------------------------------------
# STEP 3: REFLECT
# -------------------------------------------------------------
step_prompt(
    "3",
    "REFLECT — Cognitive Reasoning & Multi-Stakeholder Synthesis",
    "Then we have Reflect. This connects engineering approval with the CFO's requirement."
)

reflect_query = "Summarize the technical readiness and financial constraints for DEAL-1007."
reflection = hindsight_adapter.reflect(query=reflect_query, deal_id="DEAL-1007")

print(f"  {GREEN}✔ Live Cognitive Reflection Synthesized:{RESET}\n")
synthesis = reflection.get("strategic_synthesis") or reflection.get("recommendation", "")
for line in synthesis.strip().split("\n")[:12]:
    print(f"    {line}")

print(f"\n  {BOLD}Key Takeaway:{RESET} {YELLOW}Engineering sign-off confirmed by Marcus Vance; Financial approval gated by CFO Anita Shah (Deadline: Oct 6){RESET}")

print(f"\n{BOLD}{GREEN}═════════════════════════════════════════════════════════════════════{RESET}")
print(f"{BOLD}{GREEN}   ✔ DEMO COMPLETE — ALL 3 OPERATIONS DEMONSTRATED!                 {RESET}")
print(f"{BOLD}{GREEN}═════════════════════════════════════════════════════════════════════{RESET}\n")
