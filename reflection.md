# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. What classes did you include, and what responsibilities did you assign to each?

My initial UML design included 4 main classes, based off the suggested main components. They were Owner, Pet, Task, and Scheduler. The responsibitilty of the Owner was holding the information regarding the owner, so their name, contact info, and their pet names. The actions that the Owner could perform was adding a pet or removing one from their profile, and view tasks. The Scheduler hold the information of who owns it and the tasks on it. It can prefrom scheduling a task, accessing the tasks of the day, accessing the tasks of the day by pet, and remove a task from the schedule. The Task holds information regarding name of the task, the type of task it is, if its complete or not, the due date of the task, and the pet the task needs to be performend on. The Pet has information regarding the name of the pet, the type of pet it is and its breed, the age and weight of the pet, and who it's owner is. The Pet class holds the methods to get the profile of the pet and update the profile of the pet.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

    Yes, 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
