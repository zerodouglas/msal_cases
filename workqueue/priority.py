from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
from django.utils import timezone

@dataclass
class CaseScore:
    case_id: int
    score: float

# Tunable weights
WEIGHT_SEVERITY = 3.0        # impact of severity (1-5 → scaled)
WEIGHT_URGENCY = 4.0         # impact of time to due
WEIGHT_DA = 1.5              # extra boost if going to DA
WEIGHT_AGING = 0.5           # small boost per day since assignment

# Guardrails
MAX_URGENCY_BONUS = 10.0     # cap for extreme urgency


def compute_priority_score(case) -> float:
    now = timezone.now()

    # Severity normalized 0..1
    severity_norm = (case.severity - 1) / 4.0  # 1→0.0, 5→1.0

    # Urgency: inverse of time remaining
    due = case.effective_due_at
    seconds_remaining = max((due - now).total_seconds(), 0.0)
    policy_seconds = 10 * 24 * 3600
    urgency = 1.0 - min(seconds_remaining / policy_seconds, 1.0)  # 0 early → 1 at/overdue

    # DA boost
    da_boost = 1.0 if case.going_to_da else 0.0

    # Aging since assignment
    days_since_assign = max((now - case.assigned_at).days, 0)
    aging = min(days_since_assign * 0.1, 1.0)  # saturates at +1.0 after ~10 days

    raw = (
        WEIGHT_SEVERITY * severity_norm
        + WEIGHT_URGENCY * min(urgency * MAX_URGENCY_BONUS / MAX_URGENCY_BONUS, 1.0)
        + WEIGHT_DA * da_boost
        + WEIGHT_AGING * aging
    )

    # Final small nudge to break ties: earlier due date wins
    tie_breaker = -seconds_remaining / 1e6

    return raw + tie_breaker


def rank_cases(cases: Iterable) -> List:
    annotated = [(c, compute_priority_score(c)) for c in cases]
    annotated.sort(key=lambda t: t[1], reverse=True)
    return [c for c, _ in annotated]
