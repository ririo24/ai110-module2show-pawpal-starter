from dataclasses import dataclass, field
from datetime import date
from typing import Optional


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

    def schedule_task(self, task: Task) -> None:
        """Add a task to the scheduler's task list."""
        self.tasks.append(task)

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
