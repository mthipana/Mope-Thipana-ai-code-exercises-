# Task Priority Module Documentation

This document provides comprehensive documentation for the task priority sorting functions used in the TaskManager application.

---

## Function: `sort_tasks_by_importance`

### Description
Sorts a list of tasks by their calculated importance score in descending order (highest priority first). Tasks are ranked based on multiple factors including priority level, due date, status, special tags, and update recency.

### Signature
```python
def sort_tasks_by_importance(tasks: list[Task]) -> list[Task]:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tasks` | `list[Task]` | A list of Task objects to be sorted. Each task should be an instance of the Task class with attributes: `priority` (TaskPriority), `status` (TaskStatus), `due_date` (datetime), `tags` (list), and `updated_at` (datetime). |

### Return Value

| Type | Description |
|------|-------------|
| `list[Task]` | A new list of Task objects sorted by importance score in descending order (highest priority/importance first). The original list is not modified. |

### Exceptions

| Exception | Condition | Description |
|-----------|-----------|-------------|
| `AttributeError` | Invalid Task objects | Raised if any task in the input list lacks required attributes (e.g., `priority`, `status`, `due_date`, `tags`, `updated_at`). |
| `TypeError` | Non-Task objects in list | Raised if the input list contains objects that don't have the expected Task attributes/methods. |

### How It Works

The function uses the following algorithm:

1. **Score Calculation**: For each task, `calculate_task_score()` computes an importance score based on:
   - **Priority Weight**: Base multiplier (1-6x) applied to the priority level (LOW=1, MEDIUM=2, HIGH=4, URGENT=6), multiplied by 10
   - **Due Date Factor**: Additional points based on task urgency:
     - Overdue tasks: +35 points
     - Due today: +20 points
     - Due within 2 days: +15 points
     - Due within 7 days: +10 points
   - **Status Adjustment**: Penalty for completed/review tasks:
     - DONE status: -50 points
     - REVIEW status: -15 points
   - **Tag Boost**: +8 points for tasks with "blocker", "critical", or "urgent" tags
   - **Recency Boost**: +5 points for tasks updated within the last 24 hours

2. **Tuple Creation**: Creates tuples of `(score, task)` for efficient sorting
3. **Sorting**: Sorts tuples by score in reverse order (highest first)
4. **Extraction**: Returns only the task objects in sorted order

### Example Usage

```python
from datetime import datetime, timedelta
from models import Task, TaskPriority, TaskStatus

# Create sample tasks
task1 = Task(
    title="Fix critical bug",
    priority=TaskPriority.HIGH,
    due_date=datetime.now() + timedelta(days=1),
    tags=["critical", "blocker"]
)

task2 = Task(
    title="Update documentation",
    priority=TaskPriority.LOW,
    due_date=datetime.now() + timedelta(days=30)
)

task3 = Task(
    title="Code review",
    priority=TaskPriority.MEDIUM,
    due_date=datetime.now() + timedelta(hours=2)
)

# Sort tasks by importance
tasks = [task1, task2, task3]
sorted_tasks = sort_tasks_by_importance(tasks)

# Iterate through sorted tasks
for i, task in enumerate(sorted_tasks, 1):
    print(f"{i}. {task.title} (Priority: {task.priority.name})")
```

### Important Notes and Edge Cases

1. **Empty Lists**: If an empty list is passed, the function returns an empty list.
   ```python
   result = sort_tasks_by_importance([])
   # result = []
   ```

2. **Single Task**: If the list contains only one task, that task is returned in a list.
   ```python
   result = sort_tasks_by_importance([task])
   # result = [task]
   ```

3. **Completed Tasks**: Tasks with `DONE` status receive a -50 point penalty and will typically appear at the end of the sorted list. However, if they were originally very high priority and updated recently, they might still appear higher than low-priority pending tasks.

4. **Ties in Scores**: When multiple tasks have the same importance score, the sorting is stable—the original order is preserved for tied elements (Python's `sorted()` function is stable).
   ```python
   # If two tasks have identical scores, their relative order is preserved
   ```

5. **None/Missing Due Dates**: Tasks without a due date (`due_date=None`) do not receive any due date bonus points but are still sorted normally based on other factors.

6. **Score Calculation Timing**: The function recalculates scores each time it's called (it doesn't cache results). This means the scores can vary if tasks are updated or due dates change between calls.

7. **Timezone Considerations**: The function uses `datetime.now()` internally (via `calculate_task_score()`). Ensure all datetime objects in tasks use consistent timezone handling, or results may be unexpected.

8. **Recent Updates**: Tasks updated within 24 hours get a +5 boost. This bonus can affect the final rank, especially for similarly-scored tasks.

---

## Function: `get_top_priority_tasks`

### Description
Returns the top N tasks from the list, sorted by priority using the `sort_tasks_by_importance()` function. This is a convenience function for retrieving only the most important tasks.

### Signature
```python
def get_top_priority_tasks(tasks: list[Task], limit: int = 5) -> list[Task]:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tasks` | `list[Task]` | — | A list of Task objects to be evaluated. Each task should be a valid Task instance with the same attributes required by `sort_tasks_by_importance()`. |
| `limit` | `int` | `5` | The maximum number of top priority tasks to return. Must be a positive integer. If the limit exceeds the number of tasks available, all tasks are returned. |

### Return Value

| Type | Description |
|------|-------------|
| `list[Task]` | A list containing up to `limit` task objects, sorted by importance score in descending order. The length of the returned list will be `min(limit, len(tasks))`. |

### Exceptions

| Exception | Condition | Description |
|-----------|-----------|-------------|
| `AttributeError` | Invalid Task objects | Inherited from `sort_tasks_by_importance()`. Raised if any task lacks required attributes. |
| `TypeError` | Non-Task objects or invalid limit | Raised if tasks contain non-Task objects or if `limit` is not an integer. |

### How It Works

1. **Sorts Tasks**: Calls `sort_tasks_by_importance(tasks)` to get all tasks ranked by importance
2. **Slices List**: Returns the first `limit` items from the sorted list using Python's list slicing
3. **Returns Result**: Returns a new list containing the top N tasks

### Example Usage

```python
from datetime import datetime, timedelta
from models import Task, TaskPriority

# Create a list of multiple tasks
tasks = [
    Task("Bug fix", priority=TaskPriority.HIGH, 
         due_date=datetime.now() + timedelta(days=1)),
    Task("Feature request", priority=TaskPriority.LOW,
         due_date=datetime.now() + timedelta(days=30)),
    Task("Security patch", priority=TaskPriority.URGENT,
         due_date=datetime.now(), tags=["critical"]),
    Task("Refactor code", priority=TaskPriority.MEDIUM,
         due_date=datetime.now() + timedelta(days=7)),
    Task("Write tests", priority=TaskPriority.MEDIUM,
         due_date=datetime.now() + timedelta(days=5)),
    Task("Update deps", priority=TaskPriority.LOW,
         due_date=datetime.now() + timedelta(days=60)),
]

# Get the top 3 most important tasks
top_tasks = get_top_priority_tasks(tasks, limit=3)

print(f"Top {len(top_tasks)} priority tasks:")
for i, task in enumerate(top_tasks, 1):
    print(f"{i}. {task.title}")

# Use with default limit (returns top 5)
top_five = get_top_priority_tasks(tasks)

# Get all tasks sorted (using a very large limit)
all_sorted = get_top_priority_tasks(tasks, limit=len(tasks))
```

### Important Notes and Edge Cases

1. **Limit Greater Than Available Tasks**: If the `limit` parameter exceeds the number of tasks in the input list, all tasks are returned sorted by importance.
   ```python
   tasks = [task1, task2]  # 2 tasks
   result = get_top_priority_tasks(tasks, limit=10)
   # result = [task1, task2]  (sorted by importance)
   ```

2. **Zero or Negative Limits**: If `limit` is 0 or negative, an empty list is returned due to Python's slicing behavior.
   ```python
   result = get_top_priority_tasks(tasks, limit=0)
   # result = []
   
   result = get_top_priority_tasks(tasks, limit=-1)
   # result = []
   ```

3. **Empty Task List**: If the input list is empty, an empty list is returned regardless of the limit.
   ```python
   result = get_top_priority_tasks([], limit=5)
   # result = []
   ```

4. **Default Limit**: The default limit is 5. If you don't specify a limit, you'll get up to 5 tasks.
   ```python
   # These are equivalent for lists with 5+ tasks:
   result1 = get_top_priority_tasks(tasks)
   result2 = get_top_priority_tasks(tasks, limit=5)
   ```

5. **Performance Consideration**: For very large task lists, the function sorts the entire list but only returns the top N items. If you frequently need only the top tasks from a massive dataset, consider using a heap-based approach for better performance.

6. **Non-Mutating**: The function does not modify the original task list; it returns a new list with the top priority tasks.

7. **Task Ordering Stability**: Within the top N results, tasks are still ordered by their importance score. The first item in the returned list is always the single most important task.

---

## Common Usage Patterns

### Pattern 1: Daily Task Review
```python
# Get the top 5 most important tasks for the day
daily_tasks = get_top_priority_tasks(all_tasks, limit=5)

for task in daily_tasks:
    print(f"📌 {task.title} (Status: {task.status.value})")
```

### Pattern 2: Batch Task Management
```python
# Sort all tasks and process them in priority order
sorted_tasks = sort_tasks_by_importance(tasks)

for task in sorted_tasks:
    if task.status != TaskStatus.DONE:
        process_task(task)
```

### Pattern 3: Priority Alert System
```python
# Get critical/urgent tasks
urgent_tasks = get_top_priority_tasks(tasks, limit=10)

if urgent_tasks:
    send_notification(f"You have {len(urgent_tasks)} urgent tasks")
```

### Pattern 4: Workload Distribution
```python
# Get top N tasks per team member
for team_member in team:
    assigned_tasks = get_top_priority_tasks(
        [t for t in all_tasks if t.assigned_to == team_member],
        limit=3
    )
    assign_to_dashboard(team_member, assigned_tasks)
```

---

## Related Functions

- **`calculate_task_score(task)`**: Computes the importance score for a single task. This is called internally by both functions.
- **`Task.is_overdue()`**: Checks if a task is overdue. Used indirectly in importance calculations.
- **`Task.mark_as_done()`**: Marks a task as completed. Completed tasks receive lower scores.

---

## Dependencies

- `datetime`: Used for date and time comparisons
- `models.py`: Provides Task, TaskPriority, and TaskStatus classes

---

## Version History

- **v1.0** (Current): Initial implementation with multi-factor scoring algorithm
  - Priority-based scoring
  - Due date urgency calculation
  - Status penalties for completed/review tasks
  - Tag-based boosting
  - Recency-based boosting

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| `sort_tasks_by_importance()` | O(n log n) | O(n) |
| `get_top_priority_tasks()` | O(n log n) | O(n) |

Both functions are dominated by the sorting operation. For n tasks:
- Creating scores: O(n)
- Sorting: O(n log n)
- Returning results: O(1) for sort, O(k) for get_top_priority_tasks (where k = limit)

---

## Testing Recommendations

When testing these functions, consider the following scenarios:

1. **Empty lists**: Ensure both functions return empty lists
2. **Single task**: Verify correct behavior with minimal input
3. **Equal priority scores**: Test stable sorting with identical scores
4. **Mixed statuses**: Include DONE, IN_PROGRESS, REVIEW, and TODO tasks
5. **Extreme limits**: Test with limit=0, negative limits, and limit > task count
6. **None values**: Verify handling of None due_dates and empty tag lists
7. **Date boundaries**: Test with tasks due today, overdue, and far in future
8. **Timezone handling**: Ensure consistent datetime handling across different timezones
