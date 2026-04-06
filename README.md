# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Program

### Smarter Scheduling
PawPal+ now includes some algorithms which make it more functional. PawPal+ can now sort, filter, detect conflicts, and handle recurring tasks. Tasks can be sorted by time using sort_by_time(), which uses a lambda function to sort strings in "HH:MM" format, which returns a chronologically ordered schedule. Tasks can also be filtered by status and pet name. PawPal+ also has conflict detection, schedule_task() checks if there are any existing pending tasks that overlap with any other task at the same date and time slot. If a collision is found, a warning is given to the user but the task is still added. These features help the scheduler/user to be better organized.

### Testing PawPal+
Command to run tests: python -m pytest

I use: python3 -m pytest

The tests/test_pawpal.py file tests sorting correctness, reoccurence logic, conflict detection, and filtering. 

The sorting tests test that tasks get returned in chronological order regardless of the order they get inserted in, that the original list doesn't get changed, and that edge cases like emplty or single-item schedules don't break.

Reoccurence logic tests verify that completing a, daily or weekly, task creates a task due the subsiquent day or week. It also make sure that that task also inherits all the information from that completed task. Reoccurence logic tests also make sure that tasks that don't reoccur don't accidentally produce subsiquent tasks, and that invalid inputs raise errors.

Conflict Detection tests check that two pending tasks at the same time and due date throw a warning, and that completed or cancelled tasks don't block time slots. They also double check that the same time on different dates don't cause issues and that resolving one task stops a conflict. 

Filtering tests confim that when selecting to filter via one type of status, only tasks with a matching status get displayed. They also check the happy path that pet names aren't case-sensitive.

A confidence level I would give for the system's reliability based on test results is probably a 4 out of 5 stars. I think that having many happy paths and edge cases covered in test_pawpal.py helps ensure that the program is dependable. But I am sure that there are some edge cases that I missed so I wouldn't want to say with full certainty that this system is 100% reliable. But I do think with all the sorting, reocurrence logic, and conflict detection, and all the tests to ensure that all the logic works, does make me feel decently confident that this system is fairly reliable.


### Features
Pet Management: A user can add pets with profile details like name, species, breed, age, weight. A user can also update any pet profile attribute and remove a pet. 

Task Scheduling: A user can schedule tasks with a title, type, date, time, and optional notes. Task types include: walk, feeding, vet, and grooming. Tasks can always be added even if conflicts occur.

Sorting: Tasks are sorted in chronological order, the original task list order is preserved, and today's schedule is displayed in an earliest to latest manner.

Conflict Detection: A warning is given when two pending tasks share the same time and date. Get_conflicts returns all the pending overlapping tasks. Completed and cancelled tasks aren't included in conflict tests/checks.

Recurrence: Tasks can be repeat daily or weekly. Completing a recurring task automatically schedules the next occurrence with all the same information. 

Filtering: Filtering filters tasks by status (pending, completed, or cancelled) and by pet-name.

### 📸 Demo

<a href="/course_images/ai110/pawpalChallenges1.png" target="_blank"><img src='/course_images/ai110/pawpalChallenges1.png' title='PawPal App' width='' alt='PawPal Owner Profile' class='center-block' /></a>
<a href="/course_images/ai110/pawpalChallenges2.png" target="_blank"><img src='/course_images/ai110/pawpalChallenges2.png' title='PawPal App' width='' alt='PawPal Your Pets' class='center-block' /></a>
<a href="/course_images/ai110/pawpalChallenges3.png" target="_blank"><img src='/course_images/ai110/pawpalChallenges3.png' title='PawPal App' width='' alt='PawPal Schedule a Task' class='center-block' /></a>
<a href="/course_images/ai110/pawpalChallenges4.png" target="_blank"><img src='/course_images/ai110/pawpalChallenges4.png' title='PawPal App' width='' alt='PawPal Todays Tasks' class='center-block' /></a>