from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class Task(models.Model):
    """
    Task model for storing task information
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField(validators=[MinValueValidator(0.1)])
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Importance rating from 1-10"
    )
    dependencies = models.TextField(
        blank=True,
        default='[]',
        help_text="JSON array of task IDs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Due: {self.due_date})"

    def get_dependencies(self):
        """Parse dependencies from JSON string"""
        try:
            return json.loads(self.dependencies)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_dependencies(self, dep_list):
        """Set dependencies as JSON string"""
        self.dependencies = json.dumps(dep_list)