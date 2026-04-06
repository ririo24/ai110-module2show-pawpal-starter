# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. What classes did you include, and what responsibilities did you assign to each?

My initial UML design included 4 main classes, based off the suggested main components. They were Owner, Pet, Task, and Scheduler. The responsibitilty of the Owner was holding the information regarding the owner, so their name, contact info, and their pet names. The actions that the Owner could perform was adding a pet or removing one from their profile, and view tasks. The Scheduler hold the information of who owns it and the tasks on it. It can prefrom scheduling a task, accessing the tasks of the day, accessing the tasks of the day by pet, and remove a task from the schedule. The Task holds information regarding name of the task, the type of task it is, if its complete or not, the due date of the task, and the pet the task needs to be performend on. The Pet has information regarding the name of the pet, the type of pet it is and its breed, the age and weight of the pet, and who it's owner is. The Pet class holds the methods to get the profile of the pet and update the profile of the pet.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

    Yes. Previously, I had a function called view_tasks() for Owner, however, Claude said that it was slightly redundant since I have a function called get_todays_tasks() in Scheduler, which essentially performs the same function. Claude also suggested that instead of Task storing the pet's ID as a string, I should replace it with a direct reference to a Pet object so it can access all pet details immediately. When I had pet be a string, in order to get information about the pet, I would have to manually look it up elsewhere since there was no direct connetion between a task and its pet object, but now that Task.pet stores a Pet, that process is much simpler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

    My scheduler considers constraints like time slot conflicts and task reoccurence. Time slot conflicts are tackled by not allowing two pending tasks being able to share the same due_date and time. Task reoccurence is handled that daily and weekly reoccuring events automatically generate the next occurrence once they are completed. Time was prioritized first because two appointments just physically can't happen at the same time regardless of pet, owner, or the task. Reoccurence came next in constraint importance because tasks like feeding and grooming are routine and having to reschedule them every day would defeat the purpose of a scheduler. Things like priority level or owner availability times are other constraints to be considered, I just thought that time conflicts and task reoccurence were good constraints to handle first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

    One tradeoff that my scheduler makes is that it warns of conficts but still adds the task to the schedule instead of blocking it completely. This means the scheduler will always accept a task even if a pet owner schedules a task like a grooming appointment and a vet checkup at the same time. Both tasks are added and simply a warning is returned. An alternative solution would be to throw an exception and force the user to pick a difference time before proceeding with scheduling. However, the warning is resonable for this scenario since the stakes are low and a pet owener might intentionally schedule overlapping tasks. A pet owner might want to take their dog on a quick walk before going to the vet and so the scheduler shouldn't stop that from happening. I think returning a warning is a good compromise since it allows the owner to put in tasks they have to complete, while also informing them of the scheduling conflict so they can make informed decisions. The tradeoff here is that the schedule can end up being conflicted but that isn't like a terrible risk since the user is aware of the conflict. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
