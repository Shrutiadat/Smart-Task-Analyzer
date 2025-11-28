from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies']

    def to_representation(self, instance):
        """Convert dependencies from JSON string to list"""
        data = super().to_representation(instance)
        data['dependencies'] = instance.get_dependencies()
        return data

    def create(self, validated_data):
        """Handle dependencies conversion on create"""
        dependencies = validated_data.pop('dependencies', [])
        task = Task.objects.create(**validated_data)
        task.set_dependencies(dependencies)
        task.save()
        return task


class TaskAnalysisSerializer(serializers.Serializer):
    """Serializer for task analysis input"""
    tasks = TaskSerializer(many=True)
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        default='smart_balance'
    )


class TaskScoreSerializer(serializers.Serializer):
    """Serializer for task with score output"""
    id = serializers.IntegerField(required=False)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.CharField())
    score = serializers.DictField()