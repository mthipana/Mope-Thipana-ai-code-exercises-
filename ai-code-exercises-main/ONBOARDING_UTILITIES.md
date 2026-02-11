# Utility Modules - Additional Components

These utility modules extend the core TaskManager functionality. **Note:** They are currently defined but not yet integrated into the main entry points (`cli.py` and `task_manager.py`). They represent examples of features you might add or refactor as part of the learning exercises.

---

## Utility Module Overview

### `task_parser.py` — Free-Form Text Parser
Converts shorthand text into structured Task objects. Users can type quick task descriptions with embedded shortcuts instead of verbose CLI flags.

**Supports shortcuts:**
- `@tag` — adds tags (e.g., `"Buy milk @shopping"`)
- `!1/!2/!3/!4` or `!low/!medium/!high/!urgent` — sets priority
- `#tomorrow`, `#next_week`, `#monday`, `#2026-02-15` — sets due date

**Example:** `"Finish report @work !3 #friday"` parses to: title="Finish report", tags=["work"], priority=HIGH, due_date=next Friday.

---

### `task_priority.py` — Smart Importance Scorer
Calculates task importance by considering multiple factors beyond the simple priority number: due date urgency, task status, special tags, and update recency.

**Scoring logic:**
- Overdue tasks: +35 points
- Due today: +20 points
- Tags like "blocker", "critical", "urgent": +8 points
- Completed tasks: -50 points
- In review: -15 points

**Functions:**
- `calculate_task_score(task)` — returns numeric importance score
- `sort_tasks_by_importance(tasks)` — sorts by calculated score (highest first)
- `get_top_priority_tasks(tasks, limit=5)` — returns top N tasks

---

### `task_list_merge.py` — Conflict Resolution & Sync
Merges task lists from different sources (e.g., local device and remote server) with intelligent conflict resolution. Most recent update wins; completed status is never reversed.

**Returns sync instructions:**
- Tasks to create in remote
- Tasks to update in remote
- Tasks to create locally
- Tasks to update locally
- Merged task list (canonical source)

**Use case:** Future feature for syncing between desktop and cloud versions of the TaskManager.

---

## Integration Status

| Module | Imported | Used | Status |
|---|---|---|---|
| `task_parser.py` | ❌ | ❌ | Available for integration |
| `task_priority.py` | ❌ | ❌ | Available for integration |
| `task_list_merge.py` | ❌ | ❌ | Available for future features |

These modules are intentionally standalone to encourage learning and refactoring as part of the code exercises.
