# Task Manager Domain Model Extraction

## Executive Summary
The Task Manager is a work management system designed to organize, prioritize, and track tasks through their lifecycle. It implements a sophisticated priority scoring algorithm that factors multiple business dimensions beyond simple priority levels.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         TASK MANAGER                         │
│                      (Aggregate Root)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  id: UUID                                                     │
│  title: String (required)                                    │
│  description: String                                         │
│  priority: TaskPriority ──────────┐                         │
│  status: TaskStatus ──────────────┼──────────────┐          │
│  created_at: DateTime             │              │          │
│  updated_at: DateTime             │              │          │
│  due_date: DateTime (optional)    │              │          │
│  completed_at: DateTime (optional)│              │          │
│  tags: List[String]               │              │          │
│                                   │              │          │
│  Methods:                         │              │          │
│  • mark_as_done()                │              │          │
│  • is_overdue()                  │              │          │
│  • update(...)                   │              │          │
│                                   │              │          │
└───────────────────────────────────┼──────────────┼──────────┘
                                    │              │
                    ┌───────────────┘              │
                    │                              │
                    ▼                              ▼
        ┌──────────────────────┐      ┌─────────────────────┐
        │   TaskPriority       │      │    TaskStatus       │
        │   (Enum)             │      │    (Enum)           │
        ├──────────────────────┤      ├─────────────────────┤
        │ • LOW (1)            │      │ • TODO              │
        │ • MEDIUM (2)         │      │ • IN_PROGRESS       │
        │ • HIGH (3)           │      │ • REVIEW            │
        │ • URGENT (4)         │      │ • DONE              │
        └──────────────────────┘      └─────────────────────┘
             (Weighted Scale)            (State Flow)
              for Scoring                  →→→→→
```

### Entity Overview

| Entity | Type | Purpose |
|--------|------|---------|
| **Task** | Aggregate Root | Represents a unit of work with full lifecycle and timestamps |
| **TaskPriority** | Value Object (Enum) | Captures relative importance (1-4 weighted scale) |
| **TaskStatus** | Value Object (Enum) | Tracks task position in workflow (4 states) |

---

## Core Entity Classes

### 1. **Task** (Primary Aggregate Root)
The central entity representing a unit of work.

**Attributes:**
- `id` (UUID): Unique identifier auto-generated at creation
- `title` (String): Descriptive name of the task (required)
- `description` (String): Detailed information about the task
- `priority` (TaskPriority): Relative importance level
- `status` (TaskStatus): Current position in workflow
- `created_at` (DateTime): Immutable creation timestamp
- `updated_at` (DateTime): Last modification timestamp (auto-updated)
- `due_date` (DateTime, optional): Target completion date
- `completed_at` (DateTime, optional): Actual completion timestamp
- `tags` (List[String]): Flexible categorization/labeling system

**Business Methods:**
- `mark_as_done()`: Transitions task to DONE status and captures completion timestamp
- `is_overdue()`: Boolean check - returns true if due_date < now AND status ≠ DONE
- `update(**kwargs)`: Generic property updater with timestamp side effect

**Entity Explanation:**
Task is the centerpiece of the domain model and represents a concrete unit of work that needs to be tracked through completion. It encapsulates all relevant information about that work including what it is (title, description), when it needs to happen (due_date), how important it is (priority), where it stands (status), and contextual labels (tags). Every task is immutable once created (id, created_at never change) but mutable during its lifecycle. Tasks are the only persistent entities in the system—all data ultimately represents tasks and their current state.

---

## Enumerations (Domain Value Objects)

### 2. **TaskPriority** (Enum)
Represents the relative importance of a task within the system.

**Values (Weighted):**
- `LOW` = 1
- `MEDIUM` = 2 (default)
- `HIGH` = 3
- `URGENT` = 4

**Business Significance:** Used as base multiplier in priority score calculation (multiplied by 10).

**Entity Explanation:**
TaskPriority is a value object that captures the relative importance level assigned to a task. It's a simple enumeration with four discrete levels that reflect business urgency. The numeric weights are not arbitrary—they serve as the foundation for the priority scoring algorithm that compares tasks across the entire system. A MEDIUM priority task with a due date today may rank higher than an URGENT task due next month, demonstrating that priority is just one factor in overall task importance. TaskPriority is immutable and represents a shared domain concept used consistently across the organization.

---

### 3. **TaskStatus** (Enum)
Defines the task's position in its workflow lifecycle.

**States:**
- `TODO` ("todo"): Initial state, not yet started
- `IN_PROGRESS` ("in_progress"): Currently being worked on
- `REVIEW` ("review"): Awaiting approval or validation
- `DONE` ("done"): Completed state

**State Transitions:** Tasks move linearly through states (no backwards transitions defined).

**Entity Explanation:**
TaskStatus is a value object representing the current workflow state of a task. It defines the four-stage pipeline that work flows through in this organization: the task is identified (TODO), someone starts work on it (IN_PROGRESS), that work is examined by others (REVIEW), and finally it is complete (DONE). Status changes are the primary way the system models progress. Unlike TaskPriority which evaluates importance, TaskStatus describes position in the workflow. The system enforces that only tasks in DONE status have a completion timestamp, and only completed tasks cannot be overdue—demonstrating how status is not merely a label but drives business logic enforcement.

---

## Business Logic & Domain Concepts

### 4. **Priority Scoring Algorithm** 
A sophisticated multi-factor calculation system that ranks tasks beyond simple priority levels.

**Score Components:**

#### Base Priority Score
```
base_score = priority_weight × 10
```
- LOW: 10 points
- MEDIUM: 20 points (default)
- HIGH: 30-40 points
- URGENT: 40-60 points

#### Due Date Factor (Time Pressure)
Penalizes urgency based on days until due date:
- **Overdue** (days_until_due < 0): +35 points
- **Due Today** (days_until_due = 0): +20 points
- **Due within 2 days**: +15 points
- **Due within 7 days**: +10 points
- **Due later**: 0 points

#### Status Adjustments (Completion Discount)
- `DONE` status: -50 points (effectively deprioritizes completed tasks)
- `REVIEW` status: -15 points (partially deprioritizes)

#### Tag Boosters (Business Signal)
Tasks tagged with special keywords receive priority boosts:
- Keywords: "blocker", "critical", "urgent"
- Boost: +8 points per matching tag

#### Recency Bonus
Encourages addressing recently-updated tasks:
- Updated within last 24 hours: +5 points

#### Total Calculation Example:
```
URGENT task, 2 days overdue, tagged "blocker"
= (4 × 10) + 35 + 8 + 5 = 67 points
```

---

### 5. **Related Domain Concepts**

#### Overdue Detection
A task is considered overdue when:
- `due_date` exists
- `due_date < current_time`
- `status ≠ DONE`

**Business Implication:** Overdue tasks regardless of original priority receive significant score boost.

#### Task Lifecycle Timestamps
The system tracks three key moments:
1. **created_at**: When the task was first created (immutable)
2. **updated_at**: When any property last changed (mutable, auto-updated)
3. **completed_at**: When task transitioned to DONE status (null until completion)

#### Tag System
- Flexible labeling mechanism independent of priority/status
- Supports multi-assignment (task can have multiple tags)
- Domain-specific keywords trigger business logic:
  - "blocker": dependency-blocking task
  - "critical": system/business critical
  - "urgent": time-sensitive
- Tags can be added/removed dynamically

---

## Derived / Aggregate Concepts

### 6. **Task Collections & Queries**

#### Filtering Dimensions
- **By Status**: Get all tasks in each workflow state
- **By Priority**: Group tasks by importance level
- **By Overdue**: Identify at-risk tasks
- **By Date Range**: Completed tasks in specific periods (e.g., last 7 days)

#### Top Priority Ranking
Returns top N tasks sorted by calculated importance score (default limit: 5).

---

### 7. **System Statistics**
Derived metrics computed from task collection:

- **Total Task Count**: Overall workload volume
- **Status Distribution**: Breakdown of workflow states (todo, in_progress, review, done)
- **Priority Distribution**: Count by priority level
- **Overdue Count**: Number of at-risk tasks
- **Completed Recently**: Tasks finished in last 7 days (velocity metric)

---

## Application Terminology & Concepts

### Storage Pattern
- **TaskStorage**: Persistence abstraction (JSON-based)
- Tasks persisted as complete objects with all timestamps and relations
- Storage can be queried by status, priority, or for overdue detection

### Parsing & Input
- **TaskParser**: Converts text/CLI input to Task objects
- Date format: ISO 8601 (YYYY-MM-DD)
- Priority accepts numeric values (1-4) or names

### Management Layer
- **TaskManager**: Orchestrates CRUD operations and queries
- Enforces business rules (e.g., auto-timestamping on updates)
- Provides high-level operations (mark as done, add tag, etc.)

---

## Key Business Rules Summary

| Rule | Implementation |
|------|-----------------|
| All tasks start as TODO | Constructor default |
| Completion sets timestamp | `mark_as_done()` method |
| Overdue tasks are high-priority signal | Score boost: +35 |
| Blockers get priority boost | Tag detection: +8 |
| Recent updates stay visible | Recency bonus: +5 |
| Completed work is deprioritized | Status penalty: -50 |
| Tasks must have title | Constructor requirement |
| Priority defaults to MEDIUM | Constructor default |
| Tags are flexible/additive | Dynamic tag management |

---

## New Business Rules Implementation Opportunities

With this domain model, new rules could be added to:

1. **Assignment System**: Add `assignee` field for team management
2. **Effort Estimation**: Add `estimated_hours` and `actual_hours` fields
3. **Dependency Tracking**: Add `blocked_by` or `blocks` relationships
4. **Time Tracking**: Add `time_entries` for detailed activity logging
5. **Priority Escalation**: Rules-based promotion over time in status
6. **Batch Operations**: Rule-based status transitions (e.g., auto-advance stale REVIEW tasks)
7. **Notifications**: Trigger rules based on score thresholds or status changes
8. **SLA Compliance**: Track breach rates by priority level

---

## Code Analysis: Junior Developer Mentoring Guide

### Your Current Understanding - Validation & Correction

**What You Got Right:**
✓ The system models task listing by status (and other dimensions)
✓ There is state management happening in `update_task_status`

**Where We Need to Clarify:**

**Misconception #1:** "list_tasks and update_task_status work one after another"
- **Reality:** These are independent operations. `list_tasks()` is a READ operation (retrieves data), while `update_task_status()` is a WRITE operation (modifies data). They don't depend on each other—you might update a task status, then later query tasks by that status.
- **Example:** A user completes a task (write), then views their dashboard showing all DONE tasks (read). These are separate operations.

**Misconception #2:** "update_task_status represents continuous update"
- **Reality:** It represents a **discrete state transition**—a one-time move from one workflow state to another (TODO→IN_PROGRESS→REVIEW→DONE). It's not continuous; it's event-driven.
- **The key insight:** Notice the special handling of DONE status—it calls `task.mark_as_done()` which captures a completion timestamp. This signals that reaching DONE is a significant business event, not just another status change.

**Clarification:** Why is `add_tag_to_task` necessary?
- **Tags are business signals.** While status tracks WHERE a task is in the workflow, tags provide contextual metadata about WHAT kind of work it is.
- **Business examples:**
  - Tag "blocker" = "This task blocks other work" → gets +8 priority score boost
  - Tag "critical" = "This is essential to system/business" → gets priority boost
  - Tag "documentation" = "This is overhead work" → might filter differently
- **They're flexible.** You can add tags dynamically without rewriting the system's core logic. Tags are a domain extensibility mechanism.

---

### Core Domain Concepts Represented in This Code

#### 1. **State Machine Pattern** (The Task Lifecycle)
The `update_task_status()` method reveals a **state machine**—tasks move through predefined states:

```
TODO → IN_PROGRESS → REVIEW → DONE
                ↓         ↓      ↓
           Business    Validation Complete
           begins      required
```

**Why this matters:** Each state represents a milestone in the task's lifecycle. Different business logic applies to each state:
- Tasks in REVIEW get score penalty (-15 points)
- Only DONE tasks cannot be overdue
- Only DONE tasks have a completion timestamp

#### 2. **Multi-Dimensional Filtering** (Different Views of Tasks)
`list_tasks()` reveals that the system allows querying from multiple perspectives:

```python
list_tasks(show_overdue=True)           # Time perspective
list_tasks(status_filter="in_progress") # Workflow perspective  
list_tasks(priority_filter=4)           # Importance perspective
```

**Why this matters:** Different stakeholders need different views:
- A manager sees overdue tasks (risk management)
- A developer sees IN_PROGRESS tasks (daily standup)
- A priority planner sees URGENT tasks (resource allocation)

#### 3. **Separation of Concerns: Status vs. Priority vs. Tags**
This is subtle but crucial:

| Dimension | What it Answers | Enforced Transition | Example |
|-----------|-----------------|-------------------|---------|
| **Status** | Where is the task? | TODO→DONE (ordered) | "This task is IN_PROGRESS" |
| **Priority** | How important is it? | No transition (can change anytime) | "This is URGENT" |
| **Tags** | What category/signal? | No transition (additive) | "This is a blocker" |

**Why this matters:** A task can change priority multiple times (urgent becomes low when conditions change), change tags dynamically (add "review-ready" tag), but status flows one direction only (can't go back from DONE).

#### 4. **Business Event: Completion** (The Special Case of DONE)
```python
if new_status == TaskStatus.DONE:
    task = self.storage.get_task(task_id)
    if task:
        task.mark_as_done()  # ← This is NOT just a status change
        self.storage.save()
        return True
```

**Why this is special:** 
- Transitioning to DONE triggers `mark_as_done()` which captures `completed_at` timestamp
- This is a **business event**—completion is significant enough to warrant its own method
- It's different from other status transitions which just call `storage.update_task()`

**Real-world analogy:** Submitting a job application (status change) vs. receiving an offer (completion event). One is progress; the other is achievement.

---

### How These Concepts Connect to Business Processes

#### Process 1: Daily Task Prioritization
1. Manager runs `list_tasks(show_overdue=True)` → Gets at-risk tasks
2. System calculates priority scores (considering status, due date, tags, recency)
3. Developer sees top 5 tasks via `get_top_priority_tasks(limit=5)`
4. Developer starts work: `update_task_status(task_id, "in_progress")`

**Domain insight:** The system doesn't just store tasks—it actively helps surface what matters now.

#### Process 2: Task Completion Workflow
1. Developer works on task (status in IN_PROGRESS)
2. Task complete → `update_task_status(task_id, "review")`
3. Reviewer examines → if approved: `update_task_status(task_id, "done")`
4. System records completion time + calculates velocity metrics

**Domain insight:** REVIEW is not just another state—it's a validation gate. The task isn't truly complete until it passes this gate.

#### Process 3: Ad-Hoc Categorization
1. New urgent production issue arises
2. PM creates task: `create_task(..., priority=4)`
3. PM adds context: `add_tag_to_task(task_id, "blocker")`
4. System immediately boosts its priority score
5. Developers see it in top priorities

**Domain insight:** Tags enable real-time business context without touching the core workflow. New tag types can be invented as business needs emerge.

---

### Domain-Specific Terminology Explained

| Term | What It Means | Business Significance |
|------|--------------|----------------------|
| **Overdue** | due_date < now AND status ≠ DONE | Task is at risk; needs immediate attention |
| **Mark as Done** | Transition to DONE + capture completion timestamp | Significant event; triggers completion tracking |
| **Priority Score** | Calculated ranking considering 5+ factors | Ranks importance beyond simple priority level |
| **Blocker Tag** | Metadata indicating task blocks other work | Other tasks cannot progress until resolved |
| **Status State** | Current position in TODO→DONE pipeline | Determines what business logic applies |

---

### Testing Your Understanding: Challenge Questions

**Question 1: State Machine Thinking**
> "A task was created with due_date = 2026-02-10 and priority = HIGH. It's now 2026-02-15 and still TODO. Is this task overdue? If it IS overdue, what does the system do about it automatically?"

**Expected answer insight:** Understanding whether the system AUTO-TRANSITIONS overdue tasks or just MARKS them as at-risk (different business models).

---

**Question 2: Filtering vs. Scoring**
> "Why would a manager run `list_tasks(show_overdue=True)` instead of just running `list_tasks()` and looking through all tasks visually? What does filtering provide that a complete list doesn't?"

**Expected answer insight:** Recognizing that filtering is a scalability/usability feature—it's how the system helps users see signal in noise.

---

**Question 3: Tags as Business Signals**
> "Consider two scenarios:
> - Scenario A: Hardcode a new status called 'ESCALATED' for emergency tasks
> - Scenario B: Allow any user to add an 'escalated' tag to any task
>
> Why does this system use tags instead of creating new statuses for every business concept?"

**Expected answer insight:** Understanding that statuses are rigid (they control workflow), while tags are flexible (they communicate context). Tags scale; fixed statuses don't.

---

**Question 4: Completion as a Business Event**
> "Why does the code have a special `mark_as_done()` method instead of just setting `status = DONE`? What information would be lost if we didn't capture `completed_at`?"

**Expected answer insight:** The difference between state (status) and event (completion). Recognizing that timestamps aren't just nice-to-have; they enable velocity tracking, SLA monitoring, and historical analysis.

---

**Question 5: Multi-Dimensional Ranking**
> "A task has priority=MEDIUM, is due today, has tag='blocker', and was just updated. Another task has priority=URGENT but is due next month. Why would the first task appear higher in the priority ranking despite lower raw priority?"

**Expected answer insight:** Understanding that the scoring algorithm reflects business reality: urgency (time) often trumps stated importance (priority level).

---

### Visualization Exercise: Sketch the Task Lifecycle

Here's a diagram you should be able to draw on paper in 5 minutes:

```
USER ACTIONS                    INTERNAL STATE                QUERY PATHS
─────────────                   ──────────────                ────────────

Create Task
    ↓
    └──→ Task Created
         (status: TODO)
              ↓
              └──→ list_tasks()
                   ├─ show_overdue?
                   ├─ status_filter?
                   ├─ priority_filter?
                   └─ get_all
                   
    ↓
Update Status: TODO→IN_PROGRESS
    ↓
    └──→ Task In Progress
         (status: IN_PROGRESS)
              ↓
    
    ↓
Add Tag: "blocker"
    ↓
    └──→ Task Properties Enriched
         (tags now includes "blocker")
         (priority score increases)
              ↓
    
    ↓
Update Status: IN_PROGRESS→REVIEW
    ↓
    └──→ Task Under Review
         (status: REVIEW)
              ↓
    
    ↓
Update Status: REVIEW→DONE
    ↓
    └──→ SPECIAL EVENT: mark_as_done()
         (status: DONE)
         (completed_at: captured)
         (can never be overdue now)
              ↓
         Task Removed from
         get_overdue_tasks() results
```

**Your Exercise:**
Draw this from memory, then add:
- What happens if a task's due_date passes while it's in TODO state?
- Why is completed_at important for statistics?
- How would you represent the priority score calculation on this diagram?

---

### Key Takeaway for Future Implementation

When you implement new business rules, ask yourself:

| Question | Tells You |
|----------|-----------|
| "Does this change WHERE tasks are in the workflow?" | → Implement as new **Status** |
| "Does this change HOW IMPORTANT a task is?" | → Modify **Priority** or affect **Score calculation** |
| "Does this provide context/metadata?" | → Implement as new **Tag** |
| "Does this trigger significant events?" | → Add new **Business method** (like `mark_as_done()`) |

This distinction will guide your design decisions and prevent scope creep.
