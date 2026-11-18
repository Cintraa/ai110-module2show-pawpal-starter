"""PawPal+ logic layer (skeleton generated from diagrams/uml_draft.mmd).

Class names, attributes and empty method stubs only - no logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care activity."""

    description: str
    time: str  # "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str = "dog"
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner with several pets and a daily time budget."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet."""
        raise NotImplementedError


class Scheduler:
    """The 'brain' that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for one owner."""
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        """Return tasks in chronological order."""
        raise NotImplementedError

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Filter tasks by pet and/or completion status."""
        raise NotImplementedError

    def detect_conflicts(self) -> list[str]:
        """Return warnings for tasks scheduled at the same time."""
        raise NotImplementedError

    def generate_daily_plan(self) -> list[Task]:
        """Pick and order today's tasks within the owner's time budget."""
        raise NotImplementedError
