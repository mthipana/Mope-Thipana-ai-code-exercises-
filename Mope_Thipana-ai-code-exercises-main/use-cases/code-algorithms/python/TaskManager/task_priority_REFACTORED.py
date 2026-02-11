"""
REFACTORED VERSION: Same functionality, clearer intent
This demonstrates better code organization without changing behavior
"""

from datetime import datetime
from models import TaskStatus, TaskPriority


# REFACTORING #1: Extract due date logic into separate function
def calculate_due_date_bonus(task_due_date):
    """
    Calculate urgency bonus based on how soon a task is due.
    
    Returns bonus points (0 if no due date):
        +35 for overdue
        +20 for due today
        +15 for due in 1-2 days
        +10 for due within a week
        +0 for 8+ days away
    """
    if not task_due_date:
        return 0
    
    days_until_due = (task_due_date - datetime.now()).days
    
    # Use a lookup table instead of nested ifs
    due_date_bonuses = [
        (-1, 35),        # If days < 0 (overdue)
        (0, 20),         # If days == 0 (today)
        (2, 15),         # If days <= 2
        (7, 10),         # If days <= 7
    ]
    
    for threshold_days, bonus_points in due_date_bonuses:
        if days_until_due <= threshold_days:
            return bonus_points
    
    return 0  # 8+ days away gets no bonus


# REFACTORING #2: Extract status penalties
def calculate_status_penalty(task_status):
    """
    Calculate score reduction for non-active task statuses.
    
    Returns penalty (negative value):
        -50 for DONE (task is already complete)
        -15 for REVIEW (in progress but under review)
        0 for other statuses (TODO, IN_PROGRESS)
    """
    status_penalties = {
        TaskStatus.DONE: -50,
        TaskStatus.REVIEW: -15,
    }
    return status_penalties.get(task_status, 0)


# REFACTORING #3: Extract tag boost logic
def has_urgent_tag(task_tags):
    """
    Check if task has any high-urgency tags.
    
    Urgent tags: 'blocker', 'critical', 'urgent'
    """
    URGENT_TAGS = {"blocker", "critical", "urgent"}
    return any(tag in URGENT_TAGS for tag in task_tags)


def calculate_tag_bonus(task_tags):
    """
    Calculate score boost for special priority tags.
    
    Returns bonus points:
        +8 if task has urgent tags (blocker/critical/urgent)
        +0 otherwise
    """
    return 8 if has_urgent_tag(task_tags) else 0


# REFACTORING #4: Extract recency bonus
def calculate_recency_bonus(task_updated_at):
    """
    Calculate score boost for recently updated tasks.
    
    Returns bonus points:
        +5 if updated within last 24 hours
        +0 if not updated recently
    """
    days_since_update = (datetime.now() - task_updated_at).days
    return 5 if days_since_update < 1 else 0


# ORIGINAL (for comparison)
def calculate_task_score_original(task):
    """Original version with nested conditionals."""
    priority_weights = {
        TaskPriority.LOW: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.HIGH: 4,
        TaskPriority.URGENT: 6
    }

    score = priority_weights.get(task.priority, 0) * 10

    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:
            score += 35
        elif days_until_due == 0:
            score += 20
        elif days_until_due <= 2:
            score += 15
        elif days_until_due <= 7:
            score += 10

    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15

    if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
        score += 8

    days_since_update = (datetime.now() - task.updated_at).days
    if days_since_update < 1:
        score += 5

    return score


# REFACTORED (CLEANER)
def calculate_task_score_refactored(task):
    """
    Refactored version: same logic, organized by responsibility.
    
    Score = Base Priority + Due Date Urgency + Status Adjustment + Tags + Recency
    """
    # COMPONENT 1: Base priority score
    priority_weights = {
        TaskPriority.LOW: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.HIGH: 4,
        TaskPriority.URGENT: 6
    }
    base_score = priority_weights.get(task.priority, 0) * 10

    # COMPONENT 2: Due date urgency bonus
    due_date_bonus = calculate_due_date_bonus(task.due_date)

    # COMPONENT 3: Status penalty (negative adjustment)
    status_penalty = calculate_status_penalty(task.status)

    # COMPONENT 4: Tag-based boost
    tag_bonus = calculate_tag_bonus(task.tags)

    # COMPONENT 5: Recency bonus
    recency_bonus = calculate_recency_bonus(task.updated_at)

    # FINAL SCORE: Sum all components
    final_score = base_score + due_date_bonus + status_penalty + tag_bonus + recency_bonus

    return final_score


# ULTRA-COMPACT REFACTORING (functional style)
def calculate_task_score_compact(task):
    """Concise version using helper functions."""
    PRIORITY_WEIGHTS = {TaskPriority.LOW: 1, TaskPriority.MEDIUM: 2, TaskPriority.HIGH: 4, TaskPriority.URGENT: 6}
    
    return (
        PRIORITY_WEIGHTS.get(task.priority, 0) * 10
        + calculate_due_date_bonus(task.due_date)
        + calculate_status_penalty(task.status)
        + calculate_tag_bonus(task.tags)
        + calculate_recency_bonus(task.updated_at)
    )


if __name__ == "__main__":
    print("Refactored functions available for comparison and testing")
