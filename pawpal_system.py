from dataclasses import dataclass, field
from datetime import Date
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
        pass

    def update_profile(self, attrs: dict) -> None:
        pass


@dataclass
class Task:
    id: str
    title: str
    task_type: str        # e.g. "walk", "feeding", "vet", "grooming"
    status: str           # "pending" or "completed"
    due_date: Date
    pet: Pet              # direct Pet reference instead of pet_id string
    description: str = ""

    def complete(self) -> None:
        if self.status == "cancelled":
            raise ValueError(f"Cannot complete task '{self.title}': already cancelled.")
        self.status = "completed"

    def cancel(self) -> None:
        if self.status == "completed":
            raise ValueError(f"Cannot cancel task '{self.title}': already completed.")
        self.status = "cancelled"

    def reschedule(self, new_date: Date) -> None:
        pass


class Scheduler:
    def __init__(self, owner_id: str):
        self.owner_id: str = owner_id
        self.tasks: list[Task] = []

    def schedule_task(self, task: Task) -> None:
        pass

    def get_todays_tasks(self) -> list[Task]:
        pass

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        # compare against task.pet.id instead of a stored string
        return [t for t in self.tasks if t.pet.id == pet_id]

    def remove_task(self, task_id: str) -> None:
        pass

    def remove_tasks_for_pet(self, pet_id: str) -> None:
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
        pass

    def remove_pet(self, pet_id: str) -> None:
        self.scheduler.remove_tasks_for_pet(pet_id)
        self.pets = [p for p in self.pets if p.id != pet_id]

    # view_tasks() removed — use owner.scheduler.get_todays_tasks() directly
    # to avoid a redundant wrapper with an ambiguous contract
