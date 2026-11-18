"""PawPal+ logic layer.

* ``Task``      - one pet-care activity (what, when, how long, how often, done?).
* ``Pet``       - a pet and the list of tasks that belong to it.
* ``Owner``     - a person who owns several pets; exposes every task via ``get_all_tasks``.
* ``Scheduler`` - the "brain": reads tasks from the Owner and organizes them.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
VALID_FREQUENCIES = ("once", "daily", "weekly")


def _new_id() -> str:
    """Return a short unique id for a task."""
    return uuid.uuid4().hex[:8]


@dataclass
class Task:
    """A single pet-care activity scheduled at a time of day."""

    description: str
    time: str  # "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    pet_name: str = ""  # filled in by Pet.add_task
    task_id: str = field(default_factory=_new_id)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def summary(self) -> str:
        """One-line human readable description of the task."""
        status = "done" if self.completed else "pending"
        return f"{self.time} {self.pet_name}: {self.description} ({self.duration_minutes} min, {self.priority}, {status})"


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str = "dog"
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet (stamping the pet's name on it) and return it."""
        task.pet_name = self.name
        self.tasks.append(task)
        return task

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        """Return this pet's tasks, optionally hiding completed ones."""
        return [t for t in self.tasks if include_completed or not t.completed]

    @property
    def task_count(self) -> int:
        """Number of tasks attached to this pet."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages several pets and a daily time budget for pet care."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet; pet names must be unique per owner (case-insensitive)."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}.")
        self.pets.append(pet)
        return pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive), or None."""
        wanted = name.strip().lower()
        return next((p for p in self.pets if p.name.lower() == wanted), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet in one flat list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain' of PawPal+: organizes every pet's tasks through Owner.get_all_tasks()."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that works on one owner's pets."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """All tasks across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def todays_schedule(self) -> list[Task]:
        """Every task across all pets, ordered by start time."""
        return sorted(self.get_all_tasks(), key=lambda t: t.time)

    def mark_task_complete(self, task: Task) -> None:
        """Mark one of the owner's tasks as complete."""
        task.mark_complete()
