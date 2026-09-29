"""Intent Router.
Classifies user questions into FACTUAL, SUMMARY, STRATEGY, or PATTERN intents.
"""

from typing import Literal

IntentType = Literal["FACTUAL", "SUMMARY", "STRATEGY", "PATTERN"]


def classify_intent(message: str) -> IntentType:
    msg = message.strip().lower()

    # Pattern / Similar Deals queries
    if any(k in msg for k in ["similar", "pattern", "compare", "historical", "prior deal", "win/loss", "benchmark"]):
        return "PATTERN"

    # Strategy / Next Step queries
    if any(k in msg for k in ["what should i do", "next step", "recommend", "how to unblock", "action", "strategy", "advice", "close this", "move forward"]):
        return "STRATEGY"

    # Summary queries
    if any(k in msg for k in ["summarize", "summary", "brief", "overview", "status of", "catch me up"]):
        return "SUMMARY"

    # Factual queries (Default to FACTUAL for questions like "What do you know about Acme?", "Who is the contact?", etc.)
    return "FACTUAL"
