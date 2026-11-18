"""CLI demo for PawPal+: builds an owner with two pets and prints today's schedule.

Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(tasks: list[Task]) -> None:
    """Print tasks as an aligned table."""
    print(f"  {'TIME':<7}{'PET':<7}{'TASK':<20}{'MIN':>4}  {'PRIORITY':<9}STATUS")
    print(f"  {'-' * 5:<7}{'-' * 5:<7}{'-' * 18:<20}{'-' * 3:>4}  {'-' * 8:<9}{'-' * 7}")
    for t in tasks:
        status = "done" if t.completed else "pending"
        print(f"  {t.time:<7}{t.pet_name:<7}{t.description:<20}{t.duration_minutes:>4}  {t.priority:<9}{status}")


def main() -> None:
    """Run the PawPal+ terminal demo."""
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    luna = owner.add_pet(Pet(name="Luna", species="cat", age=5))

    mochi.add_task(Task("Morning walk", "08:00", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "07:45", 10, "high", "daily"))
    mochi.add_task(Task("Vet checkup", "14:00", 60, "high", "once"))
    luna.add_task(Task("Play session", "17:00", 20, "medium", "daily"))

    scheduler = Scheduler(owner)
    print(f"Today's Schedule for {owner.name} ({len(owner.pets)} pets)")
    print("=" * 40)
    print_schedule(scheduler.todays_schedule())

    scheduler.mark_task_complete(luna.tasks[0])
    print(f"\nAfter completing Luna's breakfast ({len(owner.get_all_tasks())} tasks total):")
    print_schedule(scheduler.todays_schedule())


if __name__ == "__main__":
    main()
