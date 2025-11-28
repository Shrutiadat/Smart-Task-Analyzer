from datetime import datetime, date
from typing import List, Dict, Any

class TaskScorer:
    """
    Core algorithm for calculating task priority scores
    
    This class implements a multi-factor scoring system that weighs:
    - Urgency (time until due date)
    - Importance (user-provided rating)
    - Effort (estimated hours to complete)
    - Dependencies (tasks that block other tasks)
    """
    
    # Weight configurations for different strategies
    STRATEGY_WEIGHTS = {
        'smart_balance': {
            'urgency': 0.35,
            'importance': 0.30,
            'effort': 0.15,
            'dependency': 0.20
        },
        'fastest_wins': {
            'urgency': 0.20,
            'importance': 0.20,
            'effort': 0.50,
            'dependency': 0.10
        },
        'high_impact': {
            'urgency': 0.15,
            'importance': 0.60,
            'effort': 0.10,
            'dependency': 0.15
        },
        'deadline_driven': {
            'urgency': 0.60,
            'importance': 0.20,
            'effort': 0.10,
            'dependency': 0.10
        }
    }

    @staticmethod
    def calculate_urgency_score(days_until_due: int) -> float:
        """
        Calculate urgency score based on days until due date
        
        Logic:
        - Overdue tasks: 100+ with exponential penalty
        - Due today: 100
        - Due tomorrow: 95
        - Due in 2-3 days: 85
        - Due in 4-7 days: 70
        - Due in 8-14 days: 50
        - Due in 15-30 days: 30
        - Due in 30+ days: Decreasing score
        """
        if days_until_due < 0:
            # Overdue tasks get exponentially higher scores
            return min(100, 100 + abs(days_until_due) * 5)
        elif days_until_due == 0:
            return 100.0
        elif days_until_due <= 1:
            return 95.0
        elif days_until_due <= 3:
            return 85.0
        elif days_until_due <= 7:
            return 70.0
        elif days_until_due <= 14:
            return 50.0
        elif days_until_due <= 30:
            return 30.0
        else:
            return max(10.0, 30.0 - (days_until_due - 30) / 10)

    @staticmethod
    def calculate_importance_score(importance: int) -> float:
        """
        Convert importance rating (1-10) to score (0-100)
        """
        return (importance / 10.0) * 100.0

    @staticmethod
    def calculate_effort_score(hours: float) -> float:
        """
        Calculate effort score - lower effort gets higher score (quick wins)
        
        Logic:
        - ≤1 hour: 90 (very quick win)
        - ≤2 hours: 80 (quick win)
        - ≤4 hours: 70 (moderate)
        - ≤8 hours: 50 (half day)
        - ≤16 hours: 30 (multiple days)
        - >16 hours: 20 (long project)
        """
        if hours <= 1:
            return 90.0
        elif hours <= 2:
            return 80.0
        elif hours <= 4:
            return 70.0
        elif hours <= 8:
            return 50.0
        elif hours <= 16:
            return 30.0
        else:
            return 20.0

    @staticmethod
    def calculate_dependency_score(task_id: Any, all_tasks: List[Dict]) -> float:
        """
        Calculate dependency score based on how many tasks depend on this one
        
        Logic:
        - 0 tasks blocked: 20 (not blocking anything)
        - 1 task blocked: 50
        - 2 tasks blocked: 75
        - 3+ tasks blocked: 75 + 10 per additional task (capped at 100)
        """
        blocking_count = sum(
            1 for task in all_tasks
            if task_id in task.get('dependencies', [])
        )
        
        if blocking_count == 0:
            return 20.0
        elif blocking_count == 1:
            return 50.0
        elif blocking_count == 2:
            return 75.0
        else:
            return min(100.0, 75.0 + (blocking_count - 2) * 10)

    @classmethod
    def calculate_priority_score(
        cls,
        task: Dict[str, Any],
        all_tasks: List[Dict[str, Any]],
        strategy: str = 'smart_balance'
    ) -> Dict[str, Any]:
        """
        Calculate the overall priority score for a task
        
        Args:
            task: Dictionary containing task data
            all_tasks: List of all tasks (needed for dependency calculation)
            strategy: Scoring strategy to use
            
        Returns:
            Dictionary with total score, breakdown, and explanation
        """
        # Parse due date
        if isinstance(task['due_date'], str):
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
        else:
            due_date = task['due_date']
        
        # Calculate days until due
        today = date.today()
        days_until_due = (due_date - today).days
        
        # Calculate individual factor scores
        urgency_score = cls.calculate_urgency_score(days_until_due)
        importance_score = cls.calculate_importance_score(task['importance'])
        effort_score = cls.calculate_effort_score(task['estimated_hours'])
        dependency_score = cls.calculate_dependency_score(
            task.get('id'),
            all_tasks
        )
        
        # Get weights for selected strategy
        weights = cls.STRATEGY_WEIGHTS.get(strategy, cls.STRATEGY_WEIGHTS['smart_balance'])
        
        # Calculate weighted total score
        total_score = (
            urgency_score * weights['urgency'] +
            importance_score * weights['importance'] +
            effort_score * weights['effort'] +
            dependency_score * weights['dependency']
        )
        
        # Generate explanation
        explanation = cls.generate_explanation(
            task,
            days_until_due,
            urgency_score,
            importance_score,
            effort_score,
            dependency_score
        )
        
        return {
            'total': round(total_score, 1),
            'breakdown': {
                'urgency': round(urgency_score, 1),
                'importance': round(importance_score, 1),
                'effort': round(effort_score, 1),
                'dependency': round(dependency_score, 1)
            },
            'explanation': explanation
        }

    @staticmethod
    def generate_explanation(
        task: Dict,
        days_until_due: int,
        urgency_score: float,
        importance_score: float,
        effort_score: float,
        dependency_score: float
    ) -> str:
        """Generate human-readable explanation for the score"""
        reasons = []
        
        if days_until_due < 0:
            reasons.append(f"⚠️ OVERDUE by {abs(days_until_due)} days")
        elif days_until_due == 0:
            reasons.append("🔥 Due TODAY")
        elif days_until_due <= 3:
            reasons.append(f"⏰ Due in {days_until_due} day{'s' if days_until_due > 1 else ''}")
        
        if importance_score >= 80:
            reasons.append("⭐ High importance")
        
        if effort_score >= 80:
            reasons.append("⚡ Quick win (low effort)")
        
        if dependency_score >= 75:
            reasons.append("🔗 Blocking other tasks")
        
        return " • ".join(reasons) if reasons else "Standard priority task"

    @staticmethod
    def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> bool:
        """
        Detect circular dependencies in task list using DFS
        
        Returns True if circular dependency exists
        """
        visited = set()
        recursion_stack = set()
        
        def has_cycle(task_id: Any, task_dict: Dict[Any, Dict]) -> bool:
            if task_id in recursion_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            recursion_stack.add(task_id)
            
            if task_id in task_dict:
                dependencies = task_dict[task_id].get('dependencies', [])
                for dep_id in dependencies:
                    if has_cycle(dep_id, task_dict):
                        return True
            
            recursion_stack.remove(task_id)
            return False
        
        # Create task lookup dictionary
        task_dict = {task.get('id'): task for task in tasks if task.get('id')}
        
        # Check each task for cycles
        for task in tasks:
            task_id = task.get('id')
            if task_id and has_cycle(task_id, task_dict):
                return True
        
        return False