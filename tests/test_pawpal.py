"""Quick tests for the PawPal+ core classes."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi")
    assert pet.task_count == 0
    pet.add_task(Task("Breakfast", "07:30"))
    pet.add_task(Task("Walk", "08:00"))
    assert pet.task_count == 2
    assert all(t.pet_name == "Mochi" for t in pet.tasks)
