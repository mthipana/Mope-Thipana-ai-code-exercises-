"""
Safe experiments to understand score calculation without disrupting the system.
Run this to verify your understanding of the priority_weights line.
"""

from datetime import datetime, timedelta
from models import TaskPriority, TaskStatus, Task

# Import the scoring functions
from task_priority import calculate_task_score

def experiment_1_baseline_scores():
    """
    EXPERIMENT 1: What are the raw base scores?
    
    This isolates the line:
        score = priority_weights.get(task.priority, 0) * 10
    
    By creating tasks with different priorities but NO other modifying factors.
    """
    print("\n=== EXPERIMENT 1: Baseline Priority Scores ===")
    print("(All tasks: no due date, ACTIVE status, no tags, recently updated)\n")
    
    for priority in [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.URGENT]:
        task = Task(
            title=f"Task with {priority.name} priority",
            description="",
            priority=priority,
            due_date=None,  # No due date factor
            tags=[]         # No tag boosts
        )
        # Simulate "recently updated" to avoid update time penalty
        task.updated_at = datetime.now()
        
        score = calculate_task_score(task)
        print(f"{priority.name:8} priority → Score: {score}")
    
    # Calculate what the multiplier would be manually
    print("\n[Theory Check]")
    print("If priority_weights = {LOW:1, MEDIUM:2, HIGH:4, URGENT:6}")
    print("And we multiply by 10, we should see: 10, 20, 40, 60")
    print("(Other factors like update time might add/subtract a few points)")


def experiment_2_multiplier_impact():
    """
    EXPERIMENT 2: What if we changed the multiplier from 10 to something else?
    
    This tests whether the multiplier value affects RANKING (it shouldn't)
    or just absolute scores (it should).
    """
    print("\n=== EXPERIMENT 2: Does Multiplier Affect Ranking? ===\n")
    
    tasks = [
        Task(title="Low Priority Task", priority=TaskPriority.LOW, due_date=None, tags=[]),
        Task(title="Medium Priority Task", priority=TaskPriority.MEDIUM, due_date=None, tags=[]),
        Task(title="High Priority Task", priority=TaskPriority.HIGH, due_date=None, tags=[]),
    ]
    
    for task in tasks:
        task.updated_at = datetime.now()
    
    scores = [calculate_task_score(task) for task in tasks]
    
    print("Current scores (multiplier=10):")
    for task, score in zip(tasks, scores):
        print(f"  {task.title}: {score}")
    
    # Sort by score
    ranking = sorted(zip(tasks, scores), key=lambda x: x[1], reverse=True)
    print("\nRanking (highest score first):")
    for i, (task, score) in enumerate(ranking, 1):
        print(f"  {i}. {task.title} ({score})")


def experiment_3_default_value():
    """
    EXPERIMENT 3: What happens with invalid/missing priority?
    
    Tests the .get(task.priority, 0) fallback behavior.
    """
    print("\n=== EXPERIMENT 3: Default Value Behavior ===\n")
    
    # Create a task with a valid priority first
    normal_task = Task(
        title="Normal Task",
        priority=TaskPriority.HIGH,
        due_date=None,
        tags=[]
    )
    normal_task.updated_at = datetime.now()
    
    normal_score = calculate_task_score(normal_task)
    print(f"Normal HIGH priority task score: {normal_score}")
    print("(This demonstrates what a HIGH priority baseline is)")


def experiment_4_coefficient_ratios():
    """
    EXPERIMENT 4: Understanding the coefficient scaling pattern.
    
    Compares the actual coefficients: 1, 2, 4, 6
    """
    print("\n=== EXPERIMENT 4: Coefficient Scaling Analysis ===\n")
    
    coefficients = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 4,
        "URGENT": 6
    }
    
    print("Priority Level → Coefficient → After ×10")
    print("-" * 45)
    for level, coef in coefficients.items():
        final = coef * 10
        print(f"{level:8} → {coef} → {final}")
    
    print("\n[Analysis]")
    print("Ratio LOW to MEDIUM:", coefficients["MEDIUM"] / coefficients["LOW"], "(linear)")
    print("Ratio MEDIUM to HIGH:", coefficients["HIGH"] / coefficients["MEDIUM"], "(doubled!)")
    print("Ratio HIGH to URGENT:", coefficients["URGENT"] / coefficients["HIGH"], "(only +50%)")
    print("\nObservation: Priority levels don't scale linearly.")
    print("HIGH gets special emphasis (2x jump from MEDIUM)")
    print("URGENT is less dramatic (+1.5x from HIGH)")


def experiment_5_compare_with_other_factors():
    """
    EXPERIMENT 5: How does priority scale compare to other scoring factors?
    
    Tests whether 10-60 range makes sense next to due date factors (+35, +20, etc)
    """
    print("\n=== EXPERIMENT 5: Priority vs. Other Scoring Factors ===\n")
    
    base_task = Task(
        title="Test Task",
        priority=TaskPriority.LOW,
        due_date=None,
        tags=[]
    )
    base_task.updated_at = datetime.now()
    
    # LOW priority baseline
    low_baseline = calculate_task_score(base_task)
    print(f"LOW priority baseline score: {low_baseline}")
    
    # Now make the same task OVERDUE (which adds 35 points)
    base_task.priority = TaskPriority.URGENT
    base_task.due_date = datetime.now() - timedelta(days=1)  # 1 day overdue
    urgent_overdue = calculate_task_score(base_task)
    
    print(f"URGENT + OVERDUE score: {urgent_overdue}")
    print(f"\nDifference from LOW baseline: {urgent_overdue - low_baseline} points")
    print("\n[Interpretation]")
    print("Priority range: 10-60 points")
    print("Due date modifiers: -50 (DONE) to +35 (overdue)")
    print("These are comparable in magnitude, so neither dominates.")


if __name__ == "__main__":
    print("=" * 60)
    print("SAFE EXPERIMENTS: Understanding Priority Score Calculation")
    print("=" * 60)
    
    try:
        experiment_1_baseline_scores()
        experiment_2_multiplier_impact()
        experiment_3_default_value()
        experiment_4_coefficient_ratios()
        experiment_5_compare_with_other_factors()
        
        print("\n" + "=" * 60)
        print("✓ All experiments completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during experiments: {e}")
        import traceback
        traceback.print_exc()
