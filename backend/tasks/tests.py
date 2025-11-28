from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer

class TaskScorerTestCase(TestCase):
    """
    Comprehensive test suite for the TaskScorer algorithm
    """
    
    def setUp(self):
        """Set up common test data"""
        self.today = date.today()
        self.sample_tasks = [
            {
                'id': 'task_1',
                'title': 'Fix critical bug',
                'due_date': (self.today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            },
            {
                'id': 'task_2',
                'title': 'Write documentation',
                'due_date': (self.today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'estimated_hours': 8,
                'importance': 5,
                'dependencies': ['task_1']
            },
            {
                'id': 'task_3',
                'title': 'Quick CSS fix',
                'due_date': (self.today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'estimated_hours': 0.5,
                'importance': 6,
                'dependencies': []
            }
        ]