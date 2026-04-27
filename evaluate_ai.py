"""
evaluate_ai.py — Test harness for the PawPal+ AI advisor.

Runs the advisor on 4 predefined pet profiles and prints a summary table
showing the reliability score, pass/fail status, and how many attempts
were needed.

Usage:
    python evaluate_ai.py

Requires ANTHROPIC_API_KEY to be set in the environment or in a .env file.
"""

import os
import sys
from datetime import date, timedelta

# Load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from pawpal_system import Pet, Task
from ai_advisor import PetCareAdvisor, RELIABILITY_THRESHOLD


# ── Test cases ─────────────────────────────────────────────────────────────────

def _make_cases():
    """Return a list of (label, pet, tasks) tuples."""
    cases = []

    # Case 1: Young Labrador with several upcoming tasks
    buddy = Pet(id="eval-p1", name="Buddy", species="dog",
                breed="Labrador Retriever", age=2, weight=28.0, owner_id="eval-o1")
    buddy_tasks = [
        Task(id="e1", title="Morning Walk", task_type="walk", status="pending",
             due_date=date.today(), pet=buddy, time="08:00"),
        Task(id="e2", title="Feeding", task_type="feeding", status="pending",
             due_date=date.today(), pet=buddy, time="07:30"),
        Task(id="e3", title="Vet Checkup", task_type="vet", status="pending",
             due_date=date.today() + timedelta(days=3), pet=buddy, time="14:00"),
    ]
    cases.append(("Young Labrador (tasks present)", buddy, buddy_tasks))

    # Case 2: Senior Persian cat with a vet visit
    mittens = Pet(id="eval-p2", name="Mittens", species="cat",
                  breed="Persian", age=13, weight=3.8, owner_id="eval-o1")
    mittens_tasks = [
        Task(id="e4", title="Senior Wellness Exam", task_type="vet", status="pending",
             due_date=date.today() + timedelta(days=1), pet=mittens, time="10:00"),
        Task(id="e5", title="Dinner", task_type="feeding", status="pending",
             due_date=date.today(), pet=mittens, time="18:00"),
    ]
    cases.append(("Senior Persian cat (vet upcoming)", mittens, mittens_tasks))

    # Case 3: Unusual species — hamster with no tasks scheduled
    nibbles = Pet(id="eval-p3", name="Nibbles", species="other",
                  breed="Syrian Hamster", age=1, weight=0.15, owner_id="eval-o1")
    cases.append(("Hamster (no tasks)", nibbles, []))

    # Case 4: Overweight adult Beagle with grooming and feeding tasks
    rex = Pet(id="eval-p4", name="Rex", species="dog",
              breed="Beagle", age=7, weight=18.0, owner_id="eval-o1")
    rex_tasks = [
        Task(id="e6", title="Grooming", task_type="grooming", status="pending",
             due_date=date.today(), pet=rex, time="11:00"),
        Task(id="e7", title="Low-calorie Lunch", task_type="feeding", status="pending",
             due_date=date.today(), pet=rex, time="12:30"),
    ]
    cases.append(("Adult Beagle overweight (grooming + feeding)", rex, rex_tasks))

    return cases


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_evaluation() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.")
        print("  Add it to a .env file or export it in your shell, then re-run.")
        sys.exit(1)

    try:
        advisor = PetCareAdvisor()
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    cases = _make_cases()
    results = []

    print(f"\n{'=' * 66}")
    print(f"  PawPal+ AI Advisor — Evaluation ({len(cases)} test cases)")
    print(f"  Reliability threshold: {RELIABILITY_THRESHOLD} / 5.0")
    print(f"{'=' * 66}\n")

    for label, pet, tasks in cases:
        print(f"  Testing: {label} …", end="", flush=True)
        try:
            r = advisor.get_reliable_advice(pet, tasks)
            c = r.critique
            status = "PASS" if c.passed else "FAIL"
            results.append({
                "label":    label,
                "status":   status,
                "overall":  c.overall_score,
                "safety":   c.safety_score,
                "complete": c.completeness_score,
                "relevant": c.relevance_score,
                "attempts": r.attempts,
                "feedback": c.feedback,
                "error":    None,
            })
            print(f" {status} ({c.overall_score:.2f})")
        except Exception as exc:
            results.append({
                "label": label, "status": "ERROR", "overall": 0,
                "safety": 0, "complete": 0, "relevant": 0,
                "attempts": 0, "feedback": "", "error": str(exc),
            })
            print(f" ERROR — {exc}")

    # ── Summary table ──────────────────────────────────────────────────────────
    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = sum(1 for r in results if r["status"] == "FAIL")
    errored = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n{'=' * 66}")
    print(f"  RESULTS SUMMARY")
    print(f"{'=' * 66}")
    print(f"  {'Test Case':<42} {'Score':>5}  {'S':>4} {'C':>4} {'R':>4}  {'Try':>3}  Status")
    print(f"  {'-' * 42} {'-' * 5}  {'-' * 4} {'-' * 4} {'-' * 4}  {'-' * 3}  ------")
    for r in results:
        if r["status"] == "ERROR":
            print(f"  {r['label']:<42} {'—':>5}  {'—':>4} {'—':>4} {'—':>4}  {'—':>3}  ERROR")
        else:
            print(
                f"  {r['label']:<42} {r['overall']:>5.2f}  "
                f"{r['safety']:>4.1f} {r['complete']:>4.1f} {r['relevant']:>4.1f}  "
                f"{r['attempts']:>3}  {r['status']}"
            )
    print(f"  {'-' * 60}")
    print(f"  Passed: {passed}/{len(cases)}  |  Failed: {failed}  |  Errors: {errored}")
    print(f"{'=' * 66}\n")

    print("  Column key: Score=overall(0-5), S=safety, C=completeness, R=relevance, Try=attempts\n")
    print("  Detailed notes from the critic model:")
    for r in results:
        note = r["error"] if r["status"] == "ERROR" else r["feedback"]
        print(f"  [{r['status']}] {r['label']}: {note}")
    print()

    # Exit non-zero if any case failed or errored (useful for CI)
    if failed or errored:
        sys.exit(1)


if __name__ == "__main__":
    run_evaluation()
