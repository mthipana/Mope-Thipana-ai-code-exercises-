# merge_task_lists — Intent & implementation notes

This document explains the intent and internal logic of the `merge_task_lists` and `resolve_task_conflict` functions, breaks down the steps, calls out assumptions and edge cases, suggests inline comments for the source, and proposes small, non-functional improvements developers can apply while preserving behavior.

## 1) High-level intent

- Purpose: Reconcile two sources of task data (local and remote) into a single canonical set and produce the minimal set of operations required to synchronize both sides.
- Primary outputs: a merged tasks dictionary and four change-sets: create/update for remote and create/update for local.
- Conflict policy in brief:
  - For most fields, the task with the later `updated_at` wins.
  - If one side is `DONE` and the other is not, `DONE` wins regardless of timestamp.
  - Tags are merged as a union and, if changed, both sides are scheduled for update.

## 2) Step-by-step logic breakdown

- merge_task_lists(local_tasks, remote_tasks)
  1. Initialize empty containers: `merged_tasks`, `to_create_remote`, `to_update_remote`, `to_create_local`, `to_update_local`.
  2. Compute `all_task_ids = set(local_tasks.keys()) | set(remote_tasks.keys())` to iterate every task present in either source.
  3. For each `task_id`:
     - If the task exists only locally:
         - Add local task to `merged_tasks` and schedule creation on remote (`to_create_remote`).
     - Else if the task exists only remotely:
         - Add remote task to `merged_tasks` and schedule creation locally (`to_create_local`).
     - Else (task exists in both):
         - Call `resolve_task_conflict(local_task, remote_task)` which returns a `(merged_task, should_update_local, should_update_remote)` triple.
         - Add `merged_task` to `merged_tasks`.
         - If `should_update_local` is true, add `merged_task` to `to_update_local`.
         - If `should_update_remote` is true, add `merged_task` to `to_update_remote`.
  4. Return the 5-tuple in the function’s declared order.

- resolve_task_conflict(local_task, remote_task)
  1. Start with a deep copy of `local_task` as `merged_task` to preserve local values by default and avoid mutating caller objects.
  2. Initialize `should_update_local = False` and `should_update_remote = False`.
  3. Compare `updated_at` timestamps:
     - If `remote.updated_at > local.updated_at`: copy `title`, `description`, `priority`, `due_date` from `remote` into `merged_task` and mark `should_update_local = True` (local should be updated to reflect remote).
     - Else: mark `should_update_remote = True` (local is newer or equal; remote should be updated).
  4. Handle `status` specially:
     - If remote is `DONE` and local is not: set `merged_task.status = DONE`, copy `completed_at` from remote, and mark `should_update_local = True`.
     - Else if local is `DONE` and remote is not: keep local (already in `merged_task`) and mark `should_update_remote = True`.
     - Else if statuses differ (neither is `DONE`): use the most recent `updated_at` to choose the winner and mark the opposite side for update.
  5. Merge `tags` as the union of both sides: `merged_task.tags = list(set(local.tags) | set(remote.tags))`.
     - If the merged tag set differs from either source, mark that side for update.
  6. Set `merged_task.updated_at = max(local.updated_at, remote.updated_at)`.
  7. Return `(merged_task, should_update_local, should_update_remote)`.

## 3) Assumptions & edge cases

- Type and shape assumptions:
  - Each `task` is an object with attributes used in the code (`title`, `description`, `priority`, `due_date`, `status`, `tags`, `updated_at`, `completed_at`). Missing attributes will raise `AttributeError` at runtime.
  - `local_tasks` and `remote_tasks` are mapping-like (support `.keys()` and `.get()`).
  - `updated_at` values are comparable (e.g., `datetime` instances). Mixed or `None` values will raise errors during comparisons.

- Semantic assumptions:
  - `TaskStatus.DONE` is the enum/state used to represent completion.
  - `updated_at` reflects true, monotonic last-modified times (if clocks are skewed, ordering may be incorrect).

- Edge cases:
  - Equal `updated_at` timestamps: current code treats local as at least as recent as remote (remote wins only when strictly greater), so the tie favors local (since `else` sets `should_update_remote = True`). If tie-breaking should prefer remote, change the comparison to `>=` or adjust logic.
  - `tags` union reorders tags and deduplicates; if tag order matters, this may be undesirable.
  - If `updated_at` is `None` on one side, the `>` comparison may raise; caller should normalize timestamps.
  - If a task object is a plain dict rather than an object with attributes, attribute access will fail—adapt code to support both shapes if needed.
  - Timezone differences: naive datetimes from different timezones may compare incorrectly.

## 4) Suggested inline comments (drop-in snippets)

Place these short comments in the source near the indicated lines to help future readers.

- At start of `merge_task_lists`:

```python
# Build a superset of IDs so we process tasks present in either source exactly once.
all_task_ids = set(local_tasks.keys()) | set(remote_tasks.keys())
```

- For the local-only branch:

```python
# Local-only: local is authoritative for this id; schedule remote creation.
```
```

- Before calling `resolve_task_conflict`:

```python
# Task exists in both places: resolve field-level conflicts and compute minimal updates.
```
```

- At start of `resolve_task_conflict`:

```python
# Use a deep copy of local as the base merged object to avoid mutating inputs.
```
```

- When comparing `updated_at`:

```python
# Most-recent wins for mutable fields; mark the older side for update.
```
```

- For completed-status handling:

```python
# Completion is a terminal state: completed tasks should not be reverted.
```
```

## 5) Potential improvements (preserve behavior unless noted)

- Input validation & normalization (recommended):
  - Validate that `task` objects have expected attributes and that `updated_at` is a comparable timestamp. Fail early with a clear error message rather than raising deep inside comparisons.
  - Normalize `updated_at` to timezone-aware `datetime` or epoch integers before merging to avoid timezone/naive-datetime bugs.

- Make conflict policy pluggable:
  - Accept an optional `conflict_resolver` strategy or a small policy object so callers can choose different tie-breakers (e.g., remote-wins-on-equal, local-wins-on-equal, or field-level policies).

- Improve immutability guarantees:
  - Return deep-copied task objects for all outputs (or provide an option) so callers cannot accidentally mutate returned tasks and affect internal state.

- Tag ordering determinism:
  - Sort merged tags (e.g., `sorted(all_tags)`) to provide deterministic output and easier tests.

- Clearer return ordering or named structure:
  - Consider returning a small dataclass or namedtuple instead of a positional 5-tuple to reduce caller confusion about the tuple order.

- Logging & telemetry:
  - Add optional debug logging to record why a decision was made for a task (e.g., "remote newer -> updated title/description"), useful when diagnosing sync issues.

- Unit tests:
  - Add focused tests for these scenarios: local-only, remote-only, remote newer, local newer, equal timestamps, DONE vs non-DONE, tags merging, missing attributes, and timestamps with different timezones.

## Quick checklist for callers

- Ensure both sides' `updated_at` fields are normalized and comparable.
- Decide tie-breaker policy for equal timestamps and update `resolve_task_conflict` if necessary.
- If task objects are dicts, adapt the function or wrap dicts in small adapters that expose attributes used by the code.

---

If you'd like, I can:
- Update the source with the suggested inline comments and an optional `policy` parameter, or
- Convert the function to accept both dict- and object-shaped tasks and add unit tests.
