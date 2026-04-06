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

I used Claude accross several parts of this project. For instance, during the testing phase, I asked Clause to analyze the codebase and identify which happy paths and edge cases were worth/most important to test. Claude then generated many test which covered testing sorting, recurrence, conflict detection, and filtering. 

- What kinds of prompts or questions were most helpful?

THe most helpful prompt were ones where I was super specific and gave loads of context to what I wanted Claude to do. For example, when I was asking Claude which were the most important edge cases to test, I specified that it should focus on both happy paths and edge cases which produced much more useful output than me just asking Claude to just "write tests". Prompts where I refrenced that actual codebase and the file that I wanted it to work better was also super helpful in getting more relevant responses from Claude.  Questions that asked Clause to explain its reasosing also helped me understand the code it produced more deeply rather than just accepting its output blindly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept an AI suggestion as-is was for the recurring task logic. Claude had set the next due date to task.due_date instead of date.today(). At first, it looked like a reasonable change but when I really thought about it, I thought that Claude's suggestion wouldn't make sense. If a daily task was overdue and completed late, the next occurrence would land on today or even in the past instead of tomorrow. When thinking about a scenario where that would happen to verify Claude's suggestion, I decided not to accept the suggested changes. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The behaviors I tested were softing correctness, recurrence logic, conflict detection, and filtering. For sorting, the tests verified that the tasks were being put in chronological order regardless of the order these tasks were inserted in. The recurrence tests confirmed that completing a daily tasks creates a new but same (characteristic-wise) task due the next day. They also tested recurring weekly tasks and that completing a task that doesn't reoccur wouldn't create a new task. The conflict detection tests checked that two pending tasks at the same time and date would produce a warning message for the user. Filtering tests made sure that status filters worked properly and that pet names were not case sensitive. 

These tests were important because we want to make sure that the program is reliable, and in order for it to be reliable all these behaviors must work correclty together.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I want to say I'm fairly confident in the core logic of this program. All the tests passed when I ran it and I believe that these test cover the most critical points of the program. I feel pretty confident about are sorting, basic conflict detection, and the recurrence logic, since those have both happy paths and meaningful edge cases covered. 

If I had more time, I would add tests for the reschedule function. I think being able to reschedule tasks would be a really helpful tool for a pet owner so I'd want to confirm that it properly works.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    
I'm pretty satisfied with the test suite. I went from havign two basic tests to having 24 tests with the help of Claude. My program feels like its truly durable and reliable since it covers so many real edge cases and not just basic happy paths. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

There are quite a few things I would improve upon, one of them being, I would want the user to be able to see more than just today's schedule. I would want the user to have more of a calendar view, that way they could be aware of vet vists weeks away and be able to see which tasks they've set as reccuring. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about designing systems with the help of AI is that AI is most useful when I am super specific about what I want it to help me with and when I really understand my system well enough to evaluate what it suggests. Early on in the project, I realized that when I gave Claude broad prompts, it produced generic outputs, but once I started giving it specific prompts, I was able to get better outputs from it. Also, just being able to really understand my program really helps me in knowing which of Claude's suggestions I should accept or reject.



## Challenge 5
I compared Claude with Copilot. Here is the prompt I gave each of them: "Based on the current files of this program, provide the logic for rescheduling weekly tasks. Do not implement it in my program, but show me the solution." Both soltutions filter the same set of tasks, pending and weekly, and put the date change into task.reschedule(). However, the Copilot's solution is more Pythonic. Claude's solution takes a date and moves each task's weekday relative to a new week. Its solution is more flexible but more complex. Copilot's solution is simple since it simply adds 7 days to each task's current date, which makes it pretty straightforward and predictable. Copilot's solution is more Pythonic since it really has one sole function with no extra parameters or math and is easier to read and test.
