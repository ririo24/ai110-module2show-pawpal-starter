import streamlit as st
from datetime import date
import uuid
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Persist Owner in session_state; load from data.json on first run ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json()

owner: Owner = st.session_state.owner

# ----------------------------------------------------------------
# SECTION 1: Owner Setup
# ----------------------------------------------------------------
st.subheader("Owner Profile")

with st.form("owner_form"):
    owner_name  = st.text_input("Your name",  value=owner.name)
    owner_email = st.text_input("Email",       value=owner.email)
    owner_phone = st.text_input("Phone",       value=owner.phone)
    if st.form_submit_button("Save profile"):
        owner.name  = owner_name
        owner.email = owner_email
        owner.phone = owner_phone
        owner.save_to_json()
        st.success(f"Profile saved for {owner.name}!")

st.divider()

# ----------------------------------------------------------------
# SECTION 2: Add a Pet  →  calls owner.add_pet()
# ----------------------------------------------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    pet_name    = st.text_input("Pet name",  value="Mochi")
    pet_species = st.selectbox("Species",    ["dog", "cat", "other"])
    pet_breed   = st.text_input("Breed",     value="Mixed")
    pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    pet_weight  = st.number_input("Weight (kg)",  min_value=0.1, max_value=200.0, value=5.0)

    if st.form_submit_button("Add pet"):
        new_pet = Pet(
            id=str(uuid.uuid4()),
            name=pet_name,
            species=pet_species,
            breed=pet_breed,
            age=int(pet_age),
            weight=float(pet_weight),
            owner_id=owner.id,
        )
        owner.add_pet(new_pet)
        owner.save_to_json()
        st.success(f"{new_pet.name} added!")

# Show current pets as a table
if owner.pets:
    st.markdown("**Your pets:**")
    st.table([
        {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age, "Weight (kg)": p.weight}
        for p in owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ----------------------------------------------------------------
# SECTION 3: Schedule a Task  →  calls owner.scheduler.schedule_task()
# ----------------------------------------------------------------
st.subheader("Schedule a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling a task.")
else:
    with st.form("add_task_form"):
        pet_options = {p.name: p for p in owner.pets}
        selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()))
        task_title    = st.text_input("Task title", value="Morning walk")
        task_type     = st.selectbox("Task type", ["walk", "feeding", "vet", "grooming"])
        task_desc     = st.text_input("Notes", value="")
        task_date     = st.date_input("Due date", value=date.today())
        task_time     = st.text_input("Time (HH:MM)", value="09:00")
        task_recur    = st.selectbox("Repeat", ["none", "daily", "weekly"])

        if st.form_submit_button("Schedule task"):
            selected_pet = pet_options[selected_pet_name]
            new_task = Task(
                id=str(uuid.uuid4()),
                title=task_title,
                task_type=task_type,
                status="pending",
                due_date=task_date,
                pet=selected_pet,
                description=task_desc,
                time=task_time,
                recurrence=None if task_recur == "none" else task_recur,
            )
            warning = owner.scheduler.schedule_task(new_task)
            owner.save_to_json()
            st.success(f"'{new_task.title}' scheduled for {selected_pet.name} on {task_date} at {task_time}.")
            if warning:
                st.warning(
                    f"**Time conflict detected.**  \n"
                    f"'{new_task.title}' is scheduled at the same time as another pending task.  \n"
                    f"Check the **Scheduling Conflicts** section below to review and resolve it."
                )

st.divider()

# ----------------------------------------------------------------
# SECTION 4: Today's Schedule  →  sorted by time via sort_by_time()
# ----------------------------------------------------------------
st.subheader("Today's Schedule")

todays_tasks = [t for t in owner.scheduler.sort_by_time() if t.due_date == date.today()]

if todays_tasks:
    STATUS_BADGE = {"pending": "🟡 Pending", "completed": "✅ Completed", "cancelled": "❌ Cancelled"}
    TYPE_ICON    = {"walk": "🦮", "feeding": "🍖", "vet": "🏥", "grooming": "✂️"}

    st.table([
        {
            "Time":   task.time,
            "Task":   f"{TYPE_ICON.get(task.task_type, '')} {task.title}",
            "Pet":    task.pet.name,
            "Type":   task.task_type.capitalize(),
            "Status": STATUS_BADGE.get(task.status, task.status),
            "Notes":  task.description or "—",
        }
        for task in todays_tasks
    ])
else:
    st.info("No tasks scheduled for today.")

st.divider()

# ----------------------------------------------------------------
# SECTION 5: Conflict Warnings  →  calls owner.scheduler.get_conflicts()
# ----------------------------------------------------------------
st.subheader("Scheduling Conflicts")

conflicts = owner.scheduler.get_conflicts()

if conflicts:
    st.warning(
        f"**{len(conflicts)} conflict{'s' if len(conflicts) != 1 else ''} found.**  \n"
        "These tasks overlap in time. Reschedule one to avoid missed care."
    )
    st.table([
        {
            "Time":       a.time,
            "Date":       str(a.due_date),
            "Task A":     a.title,
            "Pet A":      a.pet.name,
            "Task B":     b.title,
            "Pet B":      b.pet.name,
        }
        for a, b in conflicts
    ])
else:
    st.success("No conflicts — your schedule is clear!")
