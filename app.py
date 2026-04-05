import streamlit as st
from datetime import date
import uuid
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Persist Owner in session_state so it survives re-runs ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id=str(uuid.uuid4()), name="", email="", phone="")

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
        owner.add_pet(new_pet)          # calls the method we implemented
        st.success(f"{new_pet.name} added!")

# Show current pets
if owner.pets:
    st.markdown("**Your pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species}, {pet.breed}, age {pet.age})")
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
            )
            owner.scheduler.schedule_task(new_task)   # calls the method we implemented
            st.success(f"Task '{new_task.title}' scheduled for {selected_pet.name}!")

st.divider()

# ----------------------------------------------------------------
# SECTION 4: Today's Schedule  →  calls owner.scheduler.get_todays_tasks()
# ----------------------------------------------------------------
st.subheader("Today's Schedule")

todays_tasks = owner.scheduler.get_todays_tasks()

if todays_tasks:
    for task in todays_tasks:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{task.title}** — {task.pet.name} ({task.task_type})")
            if task.description:
                st.caption(task.description)
        with col2:
            st.markdown(f"`{task.status.upper()}`")
else:
    st.info("No tasks scheduled for today.")
