# `merge_task_lists` — Documentation

## Summary

`merge_task_lists(local_tasks, remote_tasks)` merges two dictionaries of tasks (local and remote) into a single, conflict-resolved mapping and computes the minimal set of operations required to reconcile both sources. The function applies a deterministic conflict-resolution policy: most-recent-update wins for most fields, completion status wins when one side is completed, and tags are merged as a union.

## Description

This function accepts two task mappings (dictionaries keyed by `task_id`) and returns a 5-tuple containing the merged task set and four dictionaries describing the changes to apply to each side to bring them into sync:

- Tasks that should be created in the remote source.
- Tasks that should be updated in the remote source.
- Tasks that should be created in the local source.
- Tasks that should be updated in the local source.

The merging logic delegates per-task conflict resolution to `resolve_task_conflict(local_task, remote_task)`. That helper follows these rules:

- Use a deep copy of the local task as the base merged object.
- For most fields (`title`, `description`, `priority`, `due_date`), the task with the later `updated_at` wins.
- For `status`, `DONE` wins over any non-`DONE` status regardless of timestamp.
- When `status` differs and neither is `DONE`, the most-recent `updated_at` wins.
- Tags are merged by union; if tags changed on either side, both sides are scheduled for update.
- The merged `updated_at` is set to the maximum of both `updated_at` timestamps.

## Parameters

- `local_tasks` (dict[TaskID, Task]) — Mapping of tasks from the local source. `TaskID` is typically an `int` or `str`. Each `Task` object is expected to expose at least these attributes:
  - `title` (str)
  - `description` (str)
  - `priority` (int or str)
  - `due_date` (datetime or None)
  - `status` (enum, e.g., `TaskStatus`)
  - `tags` (Iterable[str])
  - `updated_at` (comparable timestamp, e.g., `datetime`)
  - `completed_at` (datetime or None)

- `remote_tasks` (dict[TaskID, Task]) — Mapping of tasks from the remote source. Same expectations as `local_tasks`.

Notes about types:

- The function treats `local_tasks` and `remote_tasks` as read-only; however, objects from one side are reused in the merged result for tasks that exist only on that side. If the caller requires complete isolation, pass deep-copied inputs or deep copy the returned structures.

## Return value

Returns a tuple (in this order):

1. `merged_tasks` (dict[TaskID, Task]) — The merged mapping of all tasks after applying conflict-resolution rules.
2. `to_create_remote` (dict[TaskID, Task]) — Tasks present locally but missing remotely; these should be created on the remote side.
3. `to_update_remote` (dict[TaskID, Task]) — Tasks that exist remotely but should be updated to match the merged state.
4. `to_create_local` (dict[TaskID, Task]) — Tasks present remotely but missing locally; these should be created locally.
5. `to_update_local` (dict[TaskID, Task]) — Tasks that exist locally but should be updated to match the merged state.

Each returned dictionary maps `task_id` to the task object representing the desired state.

## Exceptions / Errors

The function itself does not explicitly raise custom exceptions, but several runtime errors can occur if preconditions are not met:

- `TypeError` or `AttributeError`: If tasks are not objects with the expected attributes (for example, missing `updated_at`, `status`, or `tags`), operations like comparisons or attribute access will raise errors.
- `TypeError`: If `local_tasks` or `remote_tasks` are not mapping-like (e.g., not dict-like), the function may raise when calling `.keys()` or `.get()`.
- `TypeError` or `ValueError`: Comparing `updated_at` values requires comparable types (e.g., `datetime` objects). If `updated_at` is `None` or mixed types, comparisons may raise.

Recommendations:

- Validate task objects (presence and types of attributes) before calling the function.
- Normalize timestamp fields to timezone-aware `datetime` or a numeric epoch to avoid comparison errors.

## Example usage

The following example demonstrates how to use `merge_task_lists`. It includes a minimal `Task` dataclass and a `TaskStatus` enum to illustrate expected fields. Replace with your real `Task`/`TaskStatus` implementations.

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: int
    due_date: datetime | None
    status: TaskStatus
    tags: list[str]
    updated_at: datetime
    completed_at: datetime | None = None

# Example tasks
local = {
    "1": Task(
        id="1",
        title="Buy milk",
        description="Whole milk",
        priority=1,
        due_date=None,
        status=TaskStatus.TODO,
        tags=["shopping"],
        updated_at=datetime(2025, 1, 1, 12, 0)
    )
}

remote = {
    "1": Task(
        id="1",
        title="Buy milk and eggs",
        description="Whole milk + eggs",
        priority=1,
        due_date=None,
        status=TaskStatus.TODO,
        tags=["shopping", "groceries"],
        updated_at=datetime(2025, 1, 2, 9, 0)
    )
}

# Call the merge function
merged, to_create_remote, to_update_remote, to_create_local, to_update_local = merge_task_lists(local, remote)

# Interpret results
print("Merged:", merged)
print("Create remote:", to_create_remote)
print("Update remote:", to_update_remote)
print("Create local:", to_create_local)
print("Update local:", to_update_local)
```

## Important notes & edge cases

- Equal `updated_at` timestamps: The implementation treats the local version as the winner when `updated_at` timestamps are equal (the helper marks `should_update_remote = True` when local is not older than remote). If you prefer remote-on-equal behavior, alter the comparison logic in `resolve_task_conflict`.
- Completed status precedence: If one side reports `status == TaskStatus.DONE` and the other does not, the merged result will be `DONE` and the non-completed side will be scheduled for update. This ensures that completed tasks are not accidentally undone.
- Tags union: Tags are merged using a set union. This can reorder tags; if tag ordering matters, apply deterministic ordering (e.g., sorted) after merging.
- Reference / mutation behavior: For tasks that exist only on one side, the function reuses the original object in the merged output. If callers require full immutability, deep-copy inputs or post-process the returned dictionaries to copy objects.
- Missing attributes or unexpected types: The function assumes task objects implement the expected attributes and that `updated_at` values are comparable. Validate or normalize inputs to avoid runtime errors.
- Timezones: When using `datetime`, prefer timezone-aware `datetime` objects for `updated_at` and `completed_at` to avoid incorrect ordering. Convert all timestamps to a common timezone or epoch before merging.

## Suggested validations before calling

- Ensure both `local_tasks` and `remote_tasks` are dictionaries mapping `task_id` to task-like objects.
- Ensure `updated_at` fields are present and comparable (prefer timezone-aware `datetime`).
- Ensure `tags` are iterable of strings (empty list when none).

## Where this file lives

See the implementation alongside this documentation in the TaskManager folder.
