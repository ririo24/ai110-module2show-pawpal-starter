import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def make_pet(id="p1", name="Buddy"):
    return Pet(id=id, name=name, species="Dog", breed="Labrador", age=3, weight=30.5, owner_id="o1")


def make_task(pet, id="t1", title="Morning Walk", time="08:00", recurrence=None, status="pending"):
    return Task(
        id=id,
        title=title,
        task_type="walk",
        status=status,
        due_date=date.today(),
        pet=pet,
        time=time,
        recurrence=recurrence,
    )


def make_scheduler(*tasks):
    s = Scheduler(owner_id="o1")
    for task in tasks:
        s.tasks.append(task)
    return s


# ── Existing Tests ─────────────────────────────────────────────────────────────

# Test 1: Task Completion
# Verify that calling complete() changes the task's status to "completed"
def test_task_completion_changes_status():
    pet = make_pet()
    task = make_task(pet)

    assert task.status == "pending"
    task.complete()
    assert task.status == "completed"


# Test 2: Task Addition
# Verify that adding a task to a pet's scheduler increases the task count
def test_task_addition_increases_count():
    owner = Owner(id="o1", name="Alex", email="alex@email.com", phone="555-0100")
    pet = make_pet()
    owner.pets.append(pet)

    task = make_task(pet)

    before = len(owner.scheduler.tasks)
    owner.scheduler.tasks.append(task)
    after = len(owner.scheduler.tasks)

    assert after == before + 1


# ── Sorting Tests ──────────────────────────────────────────────────────────────

# Test 3: Happy path — tasks added out of order are returned chronologically
def test_sort_by_time_returns_chronological_order():
    pet = make_pet()
    t1 = make_task(pet, id="t1", title="Evening Feed",  time="18:00")
    t2 = make_task(pet, id="t2", title="Midday Walk",   time="12:00")
    t3 = make_task(pet, id="t3", title="Morning Walk",  time="07:30")
    s = make_scheduler(t1, t2, t3)

    sorted_tasks = s.sort_by_time()

    assert [t.time for t in sorted_tasks] == ["07:30", "12:00", "18:00"]


# Test 4: Edge case — single task list sorts without error
def test_sort_by_time_single_task():
    pet = make_pet()
    s = make_scheduler(make_task(pet, time="09:00"))

    sorted_tasks = s.sort_by_time()

    assert len(sorted_tasks) == 1
    assert sorted_tasks[0].time == "09:00"


# Test 5: Edge case — empty scheduler returns empty list
def test_sort_by_time_empty_scheduler():
    s = Scheduler(owner_id="o1")
    assert s.sort_by_time() == []


# Test 6: Edge case — sort does not mutate the original task list order
def test_sort_by_time_does_not_mutate_original():
    pet = make_pet()
    t1 = make_task(pet, id="t1", time="18:00")
    t2 = make_task(pet, id="t2", time="07:00")
    s = make_scheduler(t1, t2)

    s.sort_by_time()

    assert s.tasks[0].time == "18:00"  # original order unchanged


# ── Recurrence Tests ───────────────────────────────────────────────────────────

# Test 7: Happy path — completing a daily task creates a new task for tomorrow
def test_complete_daily_task_creates_next_day_task():
    pet = make_pet()
    task = make_task(pet, id="t1", title="Daily Feeding", recurrence="daily")
    s = make_scheduler(task)

    next_task = s.complete_task("t1")

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.status == "pending"
    assert next_task.recurrence == "daily"


# Test 8: Happy path — completing a weekly task creates a task 7 days out
def test_complete_weekly_task_creates_next_week_task():
    pet = make_pet()
    task = make_task(pet, id="t1", title="Weekly Grooming", recurrence="weekly")
    s = make_scheduler(task)

    next_task = s.complete_task("t1")

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)


# Test 9: Happy path — recurring task child inherits title, time, and type
def test_complete_recurring_task_child_inherits_fields():
    pet = make_pet()
    task = make_task(pet, id="t1", title="Nightly Meds", time="21:00", recurrence="daily")
    s = make_scheduler(task)

    next_task = s.complete_task("t1")

    assert next_task.title == "Nightly Meds"
    assert next_task.time == "21:00"
    assert next_task.task_type == "walk"


# Test 10: Happy path — completing a non-recurring task returns None (no child created)
def test_complete_non_recurring_task_returns_none():
    pet = make_pet()
    task = make_task(pet, id="t1", recurrence=None)
    s = make_scheduler(task)

    result = s.complete_task("t1")

    assert result is None
    assert len(s.tasks) == 1  # no new task added


# Test 11: Edge case — completing a recurring task adds the child to the scheduler
def test_complete_recurring_task_adds_child_to_scheduler():
    pet = make_pet()
    task = make_task(pet, id="t1", recurrence="daily")
    s = make_scheduler(task)

    s.complete_task("t1")

    assert len(s.tasks) == 2
    assert s.tasks[1].status == "pending"


# Test 12: Edge case — completing a cancelled task raises ValueError
def test_complete_cancelled_task_raises_value_error():
    pet = make_pet()
    task = make_task(pet, id="t1", status="cancelled")
    s = make_scheduler(task)

    with pytest.raises(ValueError):
        s.complete_task("t1")


# Test 13: Edge case — completing a task with unknown ID raises ValueError
def test_complete_task_unknown_id_raises_value_error():
    s = Scheduler(owner_id="o1")

    with pytest.raises(ValueError):
        s.complete_task("nonexistent-id")


# ── Conflict Detection Tests ───────────────────────────────────────────────────

# Test 14: Happy path — two tasks at same date+time triggers a warning
def test_schedule_task_returns_warning_on_time_conflict():
    pet = make_pet()
    t1 = make_task(pet, id="t1", title="Vet Visit",  time="14:00")
    t2 = make_task(pet, id="t2", title="Grooming",   time="14:00")
    s = make_scheduler(t1)

    warning = s.schedule_task(t2)

    assert warning is not None
    assert "WARNING" in warning


# Test 15: Happy path — tasks at different times produce no warning
def test_schedule_task_no_warning_for_different_times():
    pet = make_pet()
    t1 = make_task(pet, id="t1", time="09:00")
    t2 = make_task(pet, id="t2", time="14:00")
    s = make_scheduler(t1)

    warning = s.schedule_task(t2)

    assert warning is None


# Test 16: Happy path — get_conflicts returns the conflicting pair
def test_get_conflicts_returns_conflicting_pair():
    pet = make_pet()
    t1 = make_task(pet, id="t1", title="Vet",      time="14:00")
    t2 = make_task(pet, id="t2", title="Grooming", time="14:00")
    s = make_scheduler(t1, t2)

    conflicts = s.get_conflicts()

    assert len(conflicts) == 1
    titles = {conflicts[0][0].title, conflicts[0][1].title}
    assert titles == {"Vet", "Grooming"}


# Test 17: Edge case — completed task at same time is NOT a conflict
def test_get_conflicts_ignores_completed_tasks():
    pet = make_pet()
    t1 = make_task(pet, id="t1", time="14:00", status="completed")
    t2 = make_task(pet, id="t2", time="14:00")
    s = make_scheduler(t1, t2)

    assert s.get_conflicts() == []


# Test 18: Edge case — cancelled task at same time is NOT a conflict
def test_get_conflicts_ignores_cancelled_tasks():
    pet = make_pet()
    t1 = make_task(pet, id="t1", time="10:00", status="cancelled")
    t2 = make_task(pet, id="t2", time="10:00")
    s = make_scheduler(t1, t2)

    assert s.get_conflicts() == []


# Test 19: Edge case — same time on different dates is NOT a conflict
def test_get_conflicts_same_time_different_dates_no_conflict():
    pet = make_pet()
    t1 = Task(id="t1", title="Walk", task_type="walk", status="pending",
              due_date=date.today(), pet=pet, time="09:00")
    t2 = Task(id="t2", title="Walk", task_type="walk", status="pending",
              due_date=date.today() + timedelta(days=1), pet=pet, time="09:00")
    s = make_scheduler(t1, t2)

    assert s.get_conflicts() == []


# Test 20: Edge case — conflict is resolved after completing one of the tasks
def test_get_conflicts_resolves_after_completion():
    pet = make_pet()
    t1 = make_task(pet, id="t1", time="14:00")
    t2 = make_task(pet, id="t2", time="14:00")
    s = make_scheduler(t1, t2)

    assert len(s.get_conflicts()) == 1
    s.complete_task("t1")
    assert s.get_conflicts() == []


# ── Filter Tests ───────────────────────────────────────────────────────────────

# Test 21: Happy path — filter by status returns only matching tasks
def test_filter_tasks_by_status():
    pet = make_pet()
    t1 = make_task(pet, id="t1", status="pending")
    t2 = make_task(pet, id="t2", status="completed")
    s = make_scheduler(t1, t2)

    result = s.filter_tasks(status="pending")

    assert len(result) == 1
    assert result[0].id == "t1"


# Test 22: Happy path — filter by pet name is case-insensitive
def test_filter_tasks_by_pet_name_case_insensitive():
    buddy = make_pet(id="p1", name="Buddy")
    whiskers = make_pet(id="p2", name="Whiskers")
    t1 = make_task(buddy,    id="t1")
    t2 = make_task(whiskers, id="t2")
    s = make_scheduler(t1, t2)

    assert len(s.filter_tasks(pet_name="BUDDY")) == 1
    assert len(s.filter_tasks(pet_name="buddy")) == 1


# Test 23: Edge case — pet with no tasks returns empty list from get_tasks_by_pet
def test_get_tasks_by_pet_no_tasks_returns_empty():
    s = Scheduler(owner_id="o1")
    assert s.get_tasks_by_pet("p99") == []


# Test 24: Edge case — remove_pet clears all of that pet's tasks
def test_remove_pet_removes_associated_tasks():
    owner = Owner(id="o1", name="Alex", email="a@a.com", phone="555-0100")
    buddy = make_pet(id="p1", name="Buddy")
    owner.add_pet(buddy)
    t1 = make_task(buddy, id="t1")
    t2 = make_task(buddy, id="t2")
    owner.scheduler.tasks.extend([t1, t2])

    owner.remove_pet("p1")

    assert owner.scheduler.get_tasks_by_pet("p1") == []
    assert "p1" not in [p.id for p in owner.pets]
