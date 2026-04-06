from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import uuid


@dataclass
class Pet:
    id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    owner_id: str

    def get_profile(self) -> dict:
        """Return the pet's attributes as a dictionary."""
        return {"id": self.id, "name": self.name, "species": self.species,
                "breed": self.breed, "age": self.age, "weight": self.weight}

    def update_profile(self, attrs: dict) -> None:
        """Update the pet's attributes from the provided dictionary."""
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Task:
    id: str
    title: str
    task_type: str        # e.g. "walk", "feeding", "vet", "grooming"
    status: str           # "pending" or "completed"
    due_date: date
    pet: Pet              # direct Pet reference instead of pet_id string
    description: str = ""
    time: str = "00:00"          # "HH:MM" format
    recurrence: Optional[str] = None  # "daily", "weekly", or None

    def complete(self) -> None:
        """Mark the task as completed; raises ValueError if already cancelled."""
        if self.status == "cancelled":
            raise ValueError(f"Cannot complete task '{self.title}': already cancelled.")
        self.status = "completed"

    def cancel(self) -> None:
        """Mark the task as cancelled; raises ValueError if already completed."""
        if self.status == "completed":
            raise ValueError(f"Cannot cancel task '{self.title}': already completed.")
        self.status = "cancelled"

    def reschedule(self, new_date: date) -> None:
        """Update the task's due date to the given date."""
        self.due_date = new_date


class Scheduler:
    def __init__(self, owner_id: str):
        self.owner_id: str = owner_id
        self.tasks: list[Task] = []

    def schedule_task(self, task: Task) -> Optional[str]:
        """Add a task to the scheduler's task list.

        Always adds the task. Returns a warning string if a pending task already
        occupies the same date and time slot, otherwise returns None.
        """
        conflict = next(
            (t for t in self.tasks
             if t.status == "pending"
             and t.due_date == task.due_date
             and t.time == task.time),
            None
        )
        self.tasks.append(task)
        if conflict:
            return (
                f"WARNING: '{task.title}' ({task.pet.name}) overlaps with "
                f"'{conflict.title}' ({conflict.pet.name}) — both scheduled for "
                f"{task.due_date} at {task.time}."
            )
        return None

    def get_conflicts(self) -> list[tuple[Task, Task]]:
        """Return all pairs of pending tasks that share the same date and time slot.

        Iterates over every combination of pending tasks and collects pairs whose
        due_date and time both match. Completed and cancelled tasks are excluded
        because they no longer occupy a time slot.

        Returns:
            A list of (Task, Task) tuples where each tuple represents two tasks
            that are scheduled at the same date and time. Returns an empty list
            if no conflicts exist.
        """
        pending = [t for t in self.tasks if t.status == "pending"]
        conflicts = []
        for i, a in enumerate(pending):
            for b in pending[i + 1:]:
                if a.due_date == b.due_date and a.time == b.time:
                    conflicts.append((a, b))
        return conflicts

    def get_todays_tasks(self) -> list[Task]:
        """Return all tasks whose due date is today."""
        return [t for t in self.tasks if t.due_date == date.today()]

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks assigned to the given pet."""
        return [t for t in self.tasks if t.pet.id == pet_id]

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID from the task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def remove_tasks_for_pet(self, pet_id: str) -> None:
        """Remove all tasks assigned to the given pet."""
        self.tasks = [t for t in self.tasks if t.pet.id != pet_id]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by their time attribute in ascending order.

        Relies on lexicographic string comparison of "HH:MM" formatted strings,
        which naturally preserves chronological order when hours and minutes are
        zero-padded. Does not modify the underlying task list.

        Returns:
            A new list of all Task objects ordered from earliest to latest time.
        """
        return sorted(self.tasks, key=lambda task: task.time)

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed and, if it recurs, schedule the next occurrence.

        Looks up the task by ID, delegates status change to Task.complete(), then
        checks the recurrence field. For "daily" tasks the next due date is
        today + 1 day; for "weekly" tasks it is today + 7 days. The new task
        inherits all fields (title, type, time, description, recurrence) from the
        completed task so the recurrence chain continues indefinitely.

        Args:
            task_id: The ID of the task to complete.

        Returns:
            The newly scheduled Task if the completed task had a recurrence rule,
            otherwise None.

        Raises:
            ValueError: If no task with the given ID exists, or if the task is
            already cancelled.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            raise ValueError(f"No task found with id '{task_id}'.")

        task.complete()

        if task.recurrence == "daily":
            next_date = date.today() + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_date = date.today() + timedelta(weeks=1)
        else:
            return None

        next_task = Task(
            id=str(uuid.uuid4()),
            title=task.title,
            task_type=task.task_type,
            status="pending",
            due_date=next_date,
            pet=task.pet,
            description=task.description,
            time=task.time,
            recurrence=task.recurrence,
        )
        self.schedule_task(next_task)
        return next_task

    def filter_tasks(self, status: Optional[str] = None, pet_name: Optional[str] = None) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Filters are applied sequentially — status first, then pet name on the
        already-narrowed result. Both are optional and can be used independently
        or combined. Pet name matching is case-insensitive.

        Args:
            status:   One of "pending", "completed", or "cancelled". If omitted,
                      tasks of all statuses are included.
            pet_name: The pet's name to filter by. If omitted, tasks for all
                      pets are included.

        Returns:
            A list of Task objects matching all supplied filter criteria.
        """
        result = self.tasks
        if status is not None:
            result = [t for t in result if t.status == status]
        if pet_name is not None:
            result = [t for t in result if t.pet.name.lower() == pet_name.lower()]
        return result


class Owner:
    def __init__(self, id: str, name: str, email: str, phone: str):
        self.id: str = id
        self.name: str = name
        self.email: str = email
        self.phone: str = phone
        self.pets: list[Pet] = []
        self.scheduler: Scheduler = Scheduler(owner_id=id)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet and all its associated tasks from the owner's records."""
        self.scheduler.remove_tasks_for_pet(pet_id)
        self.pets = [p for p in self.pets if p.id != pet_id]

    # view_tasks() removed — use owner.scheduler.get_todays_tasks() directly
    # to avoid a redundant wrapper with an ambiguous contract
