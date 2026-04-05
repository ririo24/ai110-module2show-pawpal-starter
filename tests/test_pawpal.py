import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def make_pet():
    return Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", age=3, weight=30.5, owner_id="o1")


def make_task(pet):
    return Task(
        id="t1",
        title="Morning Walk",
        task_type="walk",
        status="pending",
        due_date=date.today(),
        pet=pet,
    )


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
