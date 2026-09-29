from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_and_ready():
    r_health = client.get("/api/v1/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    r_ready = client.get("/api/v1/ready")
    assert r_ready.status_code == 200
    assert r_ready.json()["status"] == "ready"


def test_deals_list_and_detail():
    # AC-001: Deals exist and can be listed
    res = client.get("/api/v1/deals")
    assert res.status_code == 200
    deals = res.json()
    assert len(deals) >= 1
    
    # Check Acme Technologies deal (DEAL-1007)
    acme_deal = next((d for d in deals if d["id"] == "DEAL-1007"), None)
    assert acme_deal is not None
    assert acme_deal["name"] == "Acme Enterprise Platform Expansion"
    assert acme_deal["stage"] in ("EVALUATION", "WON")
    assert acme_deal["company"]["name"] == "Acme Technologies"


def test_interaction_timeline_and_memory_retention():
    # AC-002: Timeline returns chronological interactions
    res = client.get("/api/v1/deals/DEAL-1007/timeline")
    assert res.status_code == 200
    timeline = res.json()
    assert len(timeline) >= 3
    
    # Check interaction content from SDD Section 28
    pricing_int = next((i for i in timeline if "pricing is higher" in i["content"]), None)
    assert pricing_int is not None
    assert pricing_int["memory_sync_status"] == "SYNCED"
    assert pricing_int["hindsight_document_id"] is not None

    cfo_int = next((i for i in timeline if "CFO needs to understand ROI" in i["content"]), None)
    assert cfo_int is not None


def test_factual_query_recall():
    # AC-003: Factual query recalls correct customer/deal fact
    payload = {
        "deal_id": "DEAL-1007",
        "message": "What do you know about Acme?",
    }
    res = client.post("/api/v1/agent/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FACTUAL"
    assert "Acme Technologies" in data["answer"]
    assert len(data["evidence"]) > 0


def test_patterns_and_similar_deals():
    # AC-007: Similar historical deals and patterns can be surfaced
    res = client.get("/api/v1/deals/DEAL-1007/patterns")
    assert res.status_code == 200
    data = res.json()
    assert data["confidence_label"] == "supported"
    assert len(data["comparable_deals"]) >= 2
    assert any(d["outcome"] == "WON" for d in data["comparable_deals"])


def test_strategic_query_recommendation_and_evidence():
    # AC-004 & AC-005: Strategic query returns recommendation with evidence
    payload = {
        "deal_id": "DEAL-1007",
        "message": "What should I do next to progress this deal?",
    }
    res = client.post("/api/v1/agent/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STRATEGY"
    assert data["recommendation"] is not None
    assert data["confidence_label"] == "supported"
    assert len(data["evidence"]) > 0
    # Must link to an interaction ID
    assert data["evidence"][0]["interaction_id"] is not None


def test_memory_evolution_after_new_interaction():
    # AC-010: Adding an interaction updates memory and affects subsequent reasoning
    new_int_payload = {
        "type": "MEETING",
        "participants": ["Anita Shah", "Sarah Jenkins"],
        "content": "Anita Shah (CFO) reviewed the initial ROI proposal and requested a customized 3-year TCO comparison.",
        "summary": "CFO requested 3-year TCO comparison.",
    }
    post_res = client.post("/api/v1/deals/DEAL-1007/interactions", json=new_int_payload)
    assert post_res.status_code == 201
    created_int = post_res.json()
    assert created_int["id"] is not None
    assert created_int["memory_sync_status"] == "SYNCED"

    # Query memories for Acme
    mem_res = client.get("/api/v1/deals/DEAL-1007/memories")
    assert mem_res.status_code == 200
    memories = mem_res.json()
    assert len(memories) > 3


def test_deal_outcome_closed_learning_loop():
    # AC-008 & AC-009: Closing a deal records outcome and stores in memory
    outcome_payload = {
        "status": "WON",
        "reason": "Delivered 3-year TCO model and peer benchmark case study to Anita Shah (CFO).",
        "strategy_used": "Executive ROI walkthrough + customer case study",
    }
    res = client.post("/api/v1/deals/DEAL-1007/outcome", json=outcome_payload)
    assert res.status_code == 201
    outcome_data = res.json()
    assert outcome_data["status"] == "WON"

    # Verify deal is now WON
    deal_res = client.get("/api/v1/deals/DEAL-1007")
    assert deal_res.status_code == 200
    assert deal_res.json()["stage"] == "WON"
