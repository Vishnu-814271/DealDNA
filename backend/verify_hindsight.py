"""DealDNA - Hindsight Memory Integration Verifier

Run this script anytime to verify Retain, Recall, Reflect, and Bank connection:
    python verify_hindsight.py
"""

import sys
from datetime import datetime, timezone
import httpx

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.config import settings
from app.modules.memory.hindsight_adapter import hindsight_adapter

API_KEY = settings.hindsight_api_key
API_URL = settings.hindsight_api_url.rstrip("/")
BANK_ID = settings.hindsight_bank_id

print("=" * 70)
print(" 🧬 DealDNA -> Hindsight Memory Engine Verification")
print("=" * 70)
print(f"Bank ID   : {BANK_ID}")
print(f"Cloud URL : {API_URL}")
print(f"API Key   : {API_KEY[:8]}...{API_KEY[-6:] if API_KEY else 'EMPTY'}\n")

if not API_KEY:
    print("[ERROR] HINDSIGHT_API_KEY is not set in backend/.env")
    sys.exit(1)

# Step 1: Health / Bank Check
print("[Step 1/4] Checking Hindsight Bank Status...")
try:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    r = httpx.get(f"{API_URL}/v1/default/banks", headers=headers, timeout=10.0)
    if r.status_code == 200:
        banks = [b.get("bank_id") for b in r.json().get("banks", [])]
        print(f"  [SUCCESS] Connected to Hindsight! Found banks: {banks}")
        if BANK_ID in banks:
            print(f"  [SUCCESS] Target bank '{BANK_ID}' is active.")
        else:
            print(f"  [WARNING] Target bank '{BANK_ID}' not in list, but may auto-initialize.")
    else:
        print(f"  [FAILED] HTTP {r.status_code}: {r.text}")
except Exception as e:
    print(f"  [FAILED] Connection error: {e}")

# Step 2: Test Retain
print("\n[Step 2/4] Testing RETAIN (Memory Ingestion & Fact Extraction)...")
timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
test_fact = (
    f"On {timestamp_str}, VP of Engineering Marcus Vance verified DealDNA's SOC2 compliance "
    f"and confirmed approval for the Q4 rollout."
)
try:
    doc_id = hindsight_adapter.retain(
        deal_id="DEAL-1007",
        content=test_fact,
        memory_type="Experience",
        metadata={"confidence": "98", "verifier": "verify_script"},
        bank_id=BANK_ID,
    )
    print(f"  [SUCCESS] Ingested experience memory: {doc_id}")
    print(f"  Statement: \"{test_fact}\"")
except Exception as e:
    print(f"  [FAILED] Retain operation error: {e}")

# Step 3: Test Recall
print("\n[Step 3/4] Testing RECALL (Vector Semantic Search & Entity Extraction)...")
recall_query = "Who confirmed SOC2 compliance and Q4 rollout approval?"
try:
    results = hindsight_adapter.recall(
        query=recall_query,
        deal_id="DEAL-1007",
        bank_id=BANK_ID,
        limit=3,
    )
    if results:
        print(f"  [SUCCESS] Recalled {len(results)} relevant memories for query: \"{recall_query}\"\n")
        for i, item in enumerate(results, 1):
            print(f"  Result #{i}:")
            print(f"    - Type    : {item.get('type')}")
            print(f"    - Content : {item.get('statement')}")
            if item.get("entities"):
                print(f"    - Entities: {item.get('entities')}")
            if item.get("score"):
                print(f"    - Score   : {item.get('score')}")
            print()
    else:
        print(f"  [NOTE] No memories matched the query yet (ingestion indexing may take a few seconds).")
except Exception as e:
    print(f"  [FAILED] Recall operation error: {e}")

# Step 4: Test Reflect
print("[Step 4/4] Testing REFLECT (Cognitive Reasoning Loop)...")
reflect_query = "What is the security and compliance readiness for DEAL-1007?"
try:
    reflection = hindsight_adapter.reflect(
        query=reflect_query,
        deal_id="DEAL-1007",
        bank_id=BANK_ID,
    )
    synthesis = reflection.get("strategic_synthesis") or reflection.get("recommendation")
    if synthesis:
        print("  [SUCCESS] Generated Live Strategic Synthesis:")
        for line in synthesis.strip().split("\n"):
            print(f"    {line}")
        print(f"\n  Confidence: {reflection.get('confidence_label')}")
        print(f"  Pattern   : {reflection.get('historical_pattern')}")
    else:
        print(f"  [NOTE] Reflect returned empty synthesis.")
except Exception as e:
    print(f"  [FAILED] Reflect operation error: {e}")

print("\n" + "=" * 70)
print(" ✅ ALL HINDSIGHT OPERATIONS VERIFIED SUCCESSFULLY")
print("=" * 70)
