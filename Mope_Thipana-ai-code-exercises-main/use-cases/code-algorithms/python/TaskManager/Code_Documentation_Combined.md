# `code documentation` — Comprehensive Documentation & Design Notes

## Overview

`merge_task_lists(local_tasks, remote_tasks)` reconciles two sources of task data (local and remote) into a single canonical task set and computes the minimal set of operations required to synchronize both sides.

The merge process is deterministic and policy-driven:

- **Most-recent update wins** for most fields
- **Completion (`DONE`) is terminal** and overrides timestamps
- **Tags are merged by union**
- Only the **necessary create/update operations** are returned

Per-task conflict resolution is delegated to `resolve_task_conflict(local_task, remote_task)`.

---

## High-level Intent

### Purpose

- Merge two task mappings into a single, conflict-resolved view
- Identify exactly what must be created or updated on each side
- Prevent accidental overwrites while preserving completed work

### Primary Outputs

The function returns five dictionaries:

1. Merged tasks
2. Tasks to create on the remote side
3. Tasks to update on the remote side
4. Tasks to create on the local side
5. Tasks to update on the local side

---

## Conflict Resolution Policy (Summary)

- **Field updates** (`title`, `description`, `priority`, `due_date`)
  - Task with later `updated_at` wins
- **Status**
  - `DONE` always wins over non-`DONE`, regardless of timestamp
  - If neither is `DONE`, most-recent update wins
- **Tags**
  - Union of local and remote tags
  - If tags change, affected sides are scheduled for update
- **Timestamps**
  - `merged.updated_at = max(local.updated_at, remote.updated_at)`

---

## Function Signatures

```python
merge_task_lists(
    local_tasks: dict[TaskID, Task],
    remote_tasks: dict[TaskID, Task]
) -> tuple[
    dict[TaskID, Task],  # merged_tasks
    dict[TaskID, Task],  # to_create_remote
    dict[TaskID, Task],  # to_update_remote
    dict[TaskID, Task],  # to_create_local
    dict[TaskID, Task],  # to_update_local
]
