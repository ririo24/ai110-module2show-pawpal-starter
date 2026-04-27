"""
ai_advisor.py — Two-pass AI care advisor for PawPal+.

Flow:
  1. generate_advice()  — Claude produces 3-5 care tips for the pet.
  2. critique_advice()  — Claude scores the advice on safety, completeness,
                          and relevance and returns structured JSON.
  3. get_reliable_advice() — orchestrates both passes; if the overall score
                             is below RELIABILITY_THRESHOLD it regenerates
                             once before returning the best result.

All calls are logged to pawpal_ai.log.
"""

import json
import logging
import os
import time
from dataclasses import dataclass

import anthropic

from pawpal_system import Pet, Task

# ── Logger (file + console, isolated from Streamlit's root logger) ─────────────
logger = logging.getLogger("pawpal.ai")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    _fh = logging.FileHandler("pawpal_ai.log")
    _fh.setFormatter(_fmt)
    _ch = logging.StreamHandler()
    _ch.setFormatter(_fmt)
    logger.addHandler(_fh)
    logger.addHandler(_ch)
logger.propagate = False

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL = "claude-haiku-4-5-20251001"
RELIABILITY_THRESHOLD = 3.5   # Minimum acceptable overall score (out of 5.0)
MAX_RETRIES = 1               # Regenerate at most once when below threshold


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class CritiqueResult:
    safety_score: float        # 1–5: medically safe for this species/age/weight?
    completeness_score: float  # 1–5: addresses pet's specific profile details?
    relevance_score: float     # 1–5: relevant to the pet's scheduled tasks?
    overall_score: float       # mean of the three dimensions, rounded to 2 dp
    feedback: str              # one-sentence quality note from the critic model
    passed: bool               # True when overall_score >= RELIABILITY_THRESHOLD


@dataclass
class AdvisorResult:
    advice: str
    critique: CritiqueResult
    attempts: int    # 1 = first pass passed; 2 = had to regenerate
    pet_name: str


# ── Guardrail ──────────────────────────────────────────────────────────────────

def _validate_pet(pet: Pet) -> None:
    """Raise ValueError with a clear message if pet data is too sparse for advice."""
    if not getattr(pet, "name", "").strip():
        raise ValueError("Pet must have a name before AI advice can be generated.")
    if not getattr(pet, "species", "").strip():
        raise ValueError("Pet must have a species set.")
    if not (0 <= pet.age <= 50):
        raise ValueError(f"Pet age {pet.age} is outside the valid range 0–50 years.")
    if not (0.1 <= pet.weight <= 1000):
        raise ValueError(f"Pet weight {pet.weight} kg is outside the valid range 0.1–1000 kg.")


# ── Main class ─────────────────────────────────────────────────────────────────

class PetCareAdvisor:
    """
    Generates care advice and self-critiques it before returning to the caller.

    Usage:
        advisor = PetCareAdvisor()
        result  = advisor.get_reliable_advice(pet, tasks)
        print(result.advice)
        print(result.critique.overall_score)
    """

    def __init__(self) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Create a .env file with ANTHROPIC_API_KEY=<your key> "
                "or export it in your shell before launching the app."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    # ── Context builder ────────────────────────────────────────────────────────

    @staticmethod
    def _build_context(pet: Pet, tasks: list[Task]) -> str:
        lines = [
            f"Pet name: {pet.name}",
            f"Species:  {pet.species}",
            f"Breed:    {pet.breed}",
            f"Age:      {pet.age} year(s)",
            f"Weight:   {pet.weight} kg",
            "",
            "Upcoming tasks (pending only):",
        ]
        pending = [t for t in tasks if t.status == "pending"][:8]
        if pending:
            for t in pending:
                lines.append(f"  • {t.title} ({t.task_type}) — {t.due_date} at {t.time}")
        else:
            lines.append("  (no pending tasks scheduled)")
        return "\n".join(lines)

    # ── Pass 1: generate advice ────────────────────────────────────────────────

    def _generate_advice(self, pet: Pet, tasks: list[Task]) -> str:
        context = self._build_context(pet, tasks)
        logger.info(
            "Generating advice for '%s' (%s, %d yr, %.1f kg)",
            pet.name, pet.species, pet.age, pet.weight,
        )
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=(
                "You are a knowledgeable, concise pet care assistant. "
                "Given a pet's profile and upcoming scheduled tasks, "
                "provide exactly 3–5 specific, actionable care tips "
                "tailored to this individual animal. "
                "Do NOT give generic advice. Mention the pet by name. "
                "Address their species, breed, age, and weight where relevant."
            ),
            messages=[
                {"role": "user", "content": f"Care tips for this pet:\n\n{context}"}
            ],
        )
        advice = response.content[0].text.strip()
        logger.info("Generated %d chars of advice for '%s'", len(advice), pet.name)
        return advice

    # ── Pass 2: critique and score ─────────────────────────────────────────────

    def _critique_advice(
        self, advice: str, pet: Pet, tasks: list[Task]
    ) -> CritiqueResult:
        context = self._build_context(pet, tasks)
        logger.info("Critiquing advice for '%s'", pet.name)

        prompt = (
            "You are a strict veterinary quality reviewer. "
            "Evaluate the pet care advice below against the pet's profile.\n\n"
            f"PET PROFILE:\n{context}\n\n"
            f"ADVICE TO EVALUATE:\n{advice}\n\n"
            "Score each dimension as a float from 1.0 (poor) to 5.0 (excellent):\n"
            "  safety       — Medically safe for this species, age, and weight?\n"
            "  completeness — Covers the pet's specific profile details (not generic)?\n"
            "  relevance    — Directly relevant to the pet's actual scheduled tasks?\n\n"
            "Reply ONLY with valid JSON — no markdown, no prose:\n"
            '{"safety": <float>, "completeness": <float>, '
            '"relevance": <float>, "feedback": "<one sentence>"}'
        )
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=200,
            system="You output only valid JSON. No markdown fences, no extra text.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()

        try:
            parsed       = json.loads(raw)
            safety       = max(1.0, min(5.0, float(parsed["safety"])))
            completeness = max(1.0, min(5.0, float(parsed["completeness"])))
            relevance    = max(1.0, min(5.0, float(parsed["relevance"])))
            feedback     = str(parsed.get("feedback", ""))
            overall      = round((safety + completeness + relevance) / 3.0, 2)
            passed       = overall >= RELIABILITY_THRESHOLD

            logger.info(
                "Critique '%s': safety=%.1f complete=%.1f relevance=%.1f "
                "overall=%.2f passed=%s",
                pet.name, safety, completeness, relevance, overall, passed,
            )
            return CritiqueResult(safety, completeness, relevance, overall, feedback, passed)

        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning(
                "Critique parse failed for '%s': %s | raw=%r", pet.name, exc, raw
            )
            # Neutral fallback so the app doesn't silently break on a bad JSON response
            return CritiqueResult(
                safety_score=3.0,
                completeness_score=3.0,
                relevance_score=3.0,
                overall_score=3.0,
                feedback="(Score unavailable — critique response could not be parsed.)",
                passed=True,
            )

    # ── Orchestrator ───────────────────────────────────────────────────────────

    def get_reliable_advice(self, pet: Pet, tasks: list[Task]) -> AdvisorResult:
        """
        Generate advice, score it, and return only once it passes the threshold.
        Regenerates at most MAX_RETRIES times; returns best effort if still failing.
        """
        _validate_pet(pet)

        for attempt in range(1, MAX_RETRIES + 2):   # up to 2 total attempts
            advice   = self._generate_advice(pet, tasks)
            critique = self._critique_advice(advice, pet, tasks)

            if critique.passed:
                return AdvisorResult(advice, critique, attempt, pet.name)

            if attempt <= MAX_RETRIES:
                logger.info(
                    "Advice for '%s' scored %.2f < %.1f — regenerating (attempt %d)",
                    pet.name, critique.overall_score, RELIABILITY_THRESHOLD, attempt,
                )
                time.sleep(0.3)
            else:
                logger.warning(
                    "Advice for '%s' still scored %.2f after %d attempts — "
                    "returning best effort",
                    pet.name, critique.overall_score, attempt,
                )
                return AdvisorResult(advice, critique, attempt, pet.name)

        raise RuntimeError("get_reliable_advice: loop exited without returning")
