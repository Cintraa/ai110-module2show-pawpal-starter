"""PawPal+ Streamlit UI (Phase 3: wired to the logic layer).

The Owner object lives in st.session_state so it survives Streamlit's reruns.
Run with:  streamlit run app.py
"""

from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Pet care planner: add pets, schedule their tasks, and see the day in order.")

# Create the Owner once per browser session, then reuse it on every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
            st.success(f"Added {pet_name}.")
        except ValueError as err:
            st.error(str(err))

if owner.pets:
    st.write("Pets:", ", ".join(f"{p.name} ({p.species}, {p.task_count} tasks)" for p in owner.pets))

    st.subheader("Schedule a task")
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        start = st.time_input("Start time", value=time(8, 0))
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            owner.get_pet(pet_choice).add_task(
                Task(description, start.strftime("%H:%M"), int(duration), priority, frequency)
            )
            st.success(f"Added '{description}' for {pet_choice}.")
else:
    st.info("Add a pet to start scheduling tasks.")

st.subheader("Today's schedule")
tasks = scheduler.todays_schedule()
if tasks:
    st.table(
        [
            {"Time": t.time, "Pet": t.pet_name, "Task": t.description, "Minutes": t.duration_minutes,
             "Priority": t.priority, "Repeats": t.frequency, "Done": t.completed}
            for t in tasks
        ]
    )
else:
    st.info("No tasks yet.")
