# Code Documentation: Task Sorting and Priority Functions

## Overview

This documentation covers two functions that work together to sort and filter tasks based on calculated importance scores. The code is designed to help prioritize work by ranking tasks and returning the most important ones.

---

## 1. High-Level Intent

### Purpose
These functions implement a **task prioritization system** that:
- Calculates an importance/priority score for each task
- Ranks tasks from highest to lowest priority
- Returns the top N priority tasks for focused work management

### Use Case
Ideal for task management systems where you need to identify "must-do" items first, helping users focus on what matters most instead of working on tasks in arbitrary order.

---

## 2. Function-by-Function Breakdown

### `sort_tasks_by_importance(tasks)`

**What it does:** Sorts all tasks by their calculated importance score in descending order (highest priority first).

**Step-by-step logic:**

```python
def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    
    # Step 1: Create a list of tuples combining each task with its calculated importance score
    # Structure: [(score1, task1), (score2, task2), ...]
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    
    # Step 2: Sort the list of tuples by the score (first element)
    # The lambda function extracts only the score for comparison
    # reverse=True ensures highest scores appear first
    # Use key parameter to tell sorted() to only compare the scores (first element of tuple)
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    
    # Step 3: Extract just the tasks from the sorted tuples (discarding scores)
    # The underscore (_) is a convention for ignoring the score after sorting
    return sorted_tasks
```

**Key Technical Points:**
- **Tuple approach:** Pairs each task with its score to keep them together during sorting
- **Lambda function:** `lambda x: x[0]` extracts the score (first element) for comparison
- **reverse=True:** Puts highest scores first (descending order)
- **List comprehension unpacking:** `[task for _, task in ...]` extracts tasks and discards scores

---

### `get_top_priority_tasks(tasks, limit=5)`

**What it does:** Returns the top N most important tasks (default: top 5).

**Step-by-step logic:**

```python
def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    
    # Step 1: Use the sorting function to get all tasks ranked by importance
    sorted_tasks = sort_tasks_by_importance(tasks)
    
    # Step 2: Use list slicing to return only the top 'limit' number of tasks
    # If fewer tasks exist than the limit, Python returns all available tasks
    return sorted_tasks[:limit]
```

**Key Technical Points:**
- **Default parameter:** `limit=5` provides sensible default but is customizable
- **Slice notation:** `[:limit]` safely returns up to `limit` items (won't error if fewer items exist)

---

## 3. Assumptions and Edge Cases

### Assumptions Made:
1. **`calculate_task_score()` exists:** The code assumes a function named `calculate_task_score()` is defined elsewhere
2. **Scores are numeric:** Assumes `calculate_task_score()` returns comparable numbers (int, float)
3. **Higher scores = higher priority:** Interprets larger numbers as more important

### Edge Cases to Consider:

| Edge Case | Current Behavior | Potential Issue |
|-----------|------------------|-----------------|
| **Empty task list** | Returns empty list | ✓ Works correctly |
| **Single task** | Returns list with one task | ✓ Works correctly |
| **Equal importance scores** | Maintains arbitrary order from original sort | ⚠️ No tie-breaking logic |
| **limit > total tasks** | Returns all available tasks | ✓ Works correctly (Python slicing is safe) |
| **limit = 0** | Returns empty list | ✓ Works correctly |
| **Negative scores** | Sorts correctly (higher negative is less important) | ✓ Works correctly |
| **NaN or None scores** | Will cause TypeError during comparison | ❌ No validation |

---

## 4. Suggested Inline Comments for Complex Parts

Here's how the code could be annotated for better clarity:

```python
def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    
    # Create (score, task) tuples to keep scores aligned with their tasks during sorting
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    
    # Sort by score only (key extracts first tuple element), highest scores first (reverse=True)
    # Lambda tells sorted() to compare only the numeric score, not the entire tuple
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    
    return sorted_tasks

def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    
    sorted_tasks = sort_tasks_by_importance(tasks)
    
    # Python slicing safely returns fewer items if fewer tasks exist than limit
    return sorted_tasks[:limit]
```

---

## 5. Potential Improvements

While maintaining original functionality, consider these enhancements:

### A. Add Input Validation
```python
def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    if not tasks:  # Handle empty list gracefully
        return []
    
    # Ensure all scores are valid before processing
    task_scores = []
    for task in tasks:
        score = calculate_task_score(task)
        if score is None or not isinstance(score, (int, float)):
            raise ValueError(f"Invalid score for task: {task}")
        task_scores.append((score, task))
    
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks
```

### B. Use `operator.itemgetter()` for Cleaner Sorting
```python
from operator import itemgetter

def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    # operator.itemgetter is potentially faster than lambda for simple index access
    sorted_tasks = [task for _, task in sorted(task_scores, key=itemgetter(0), reverse=True)]
    return sorted_tasks
```

### C. Add Tie-Breaking Logic
```python
def sort_tasks_by_importance(tasks, secondary_key=None):
    """Sort tasks by importance score, with optional tie-breaking criteria."""
    # If two tasks have equal importance, use secondary_key to break ties
    # Example: sort by due_date, task_id, or task name
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(
        task_scores, 
        key=lambda x: (x[0], secondary_key(x[1]) if secondary_key else 0),
        reverse=True
    )]
    return sorted_tasks
```

### D. Cache Results for Repeated Calls
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks (cached for performance)."""
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
```

### E. Use Immediate Slicing to Reduce Memory
```python
def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks (more memory-efficient)."""
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    # Use heapq.nlargest() for better performance with large lists and small limits
    from heapq import nlargest
    top_tasks = [task for _, task in nlargest(limit, task_scores, key=lambda x: x[0])]
    return top_tasks
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Main Goal** | Rank tasks by importance and return top priorities |
| **Current Complexity** | O(n log n) due to sorting |
| **Strengths** | Simple, readable, handles edge cases well |
| **Limitations** | No validation, no tie-breaking, recreates sorted list each time |
| **Best Use** | Small to medium task lists with infrequent sorting |

