"""
Sentiment analysis for news using transformers. Score -1 to +1, mapped to points.
"""
from typing import List, Dict
import re

# Lightweight fallback if transformers not available
try:
    from transformers import pipeline
    _pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception:
    _pipe = None


def analyze_sentiment(text: str) -> float:
    """
    Return sentiment score in [-1, 1]. Positive -> higher.
    """
    if not text or not text.strip():
        return 0.0
    text = re.sub(r"\s+", " ", text)[:512]
    if _pipe is None:
        # Fallback: simple keyword heuristic
        text_lower = text.lower()
        pos = sum(1 for w in ["rise", "growth", "beat", "surge", "gain", "bull", "upgrade"] if w in text_lower)
        neg = sum(1 for w in ["fall", "drop", "miss", "cut", "bear", "downgrade", "loss"] if w in text_lower)
        if pos + neg == 0:
            return 0.0
        return (pos - neg) / max(pos + neg, 1)
    try:
        out = _pipe(text[:512])[0]
        label = (out or {}).get("label", "NEUTRAL")
        score = float((out or {}).get("score", 0.5))
        if "POSITIVE" in str(label).upper():
            return score
        if "NEGATIVE" in str(label).upper():
            return -score
        return 0.0
    except Exception:
        return 0.0


def batch_sentiment(titles: List[str]) -> Dict[str, float]:
    """Return dict title -> sentiment [-1, 1]."""
    return {t: analyze_sentiment(t) for t in titles}
