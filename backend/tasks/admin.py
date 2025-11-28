from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Task model
    """
    list_display = ['title', 'due_date', 'importance', 'estimated_hours', 'created_at']
    list_filter = ['due_date', 'importance', 'created_at']
    search_fields = ['title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'due_date', 'estimated_hours', 'importance')
        }),
        ('Dependencies', {
            'fields': ('dependencies',),
            'description': 'JSON array of task IDs, e.g., ["task_1", "task_2"]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )