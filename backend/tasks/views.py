from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .serializers import TaskAnalysisSerializer, TaskScoreSerializer
from .scoring import TaskScorer

@method_decorator(csrf_exempt, name='dispatch')
class TaskAnalyzeView(APIView):
    """
    POST /api/tasks/analyze/
    
    Accept a list of tasks and return them sorted by priority score
    """
    
    def post(self, request):
        # Extract tasks and strategy from request
        tasks_data = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart_balance')
        
        if not tasks_data:
            return Response(
                {'error': 'No tasks provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate tasks
        serializer = TaskAnalysisSerializer(data={
            'tasks': tasks_data,
            'strategy': strategy
        })
        
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for circular dependencies
        if TaskScorer.detect_circular_dependencies(tasks_data):
            return Response(
                {'error': 'Circular dependency detected in tasks'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate scores for all tasks
        analyzed_tasks = []
        for task in tasks_data:
            score = TaskScorer.calculate_priority_score(
                task,
                tasks_data,
                strategy
            )
            analyzed_tasks.append({
                **task,
                'score': score
            })
        
        # Sort by score (highest first)
        analyzed_tasks.sort(key=lambda x: x['score']['total'], reverse=True)
        
        return Response({
            'tasks': analyzed_tasks,
            'strategy': strategy,
            'total_tasks': len(analyzed_tasks)
        })


@method_decorator(csrf_exempt, name='dispatch')
class TaskSuggestView(APIView):
    """
    POST /api/tasks/suggest/
    
    Return the top 3 tasks the user should work on today with explanations
    """
    
    def post(self, request):
        tasks_data = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart_balance')
        
        if not tasks_data:
            return Response(
                {'error': 'No tasks provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for circular dependencies
        if TaskScorer.detect_circular_dependencies(tasks_data):
            return Response(
                {'error': 'Circular dependency detected in tasks'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate scores
        analyzed_tasks = []
        for task in tasks_data:
            score = TaskScorer.calculate_priority_score(
                task,
                tasks_data,
                strategy
            )
            analyzed_tasks.append({
                **task,
                'score': score
            })
        
        # Sort and get top 3
        analyzed_tasks.sort(key=lambda x: x['score']['total'], reverse=True)
        top_three = analyzed_tasks[:3]
        
        # Generate recommendations
        recommendations = []
        for idx, task in enumerate(top_three, 1):
            recommendations.append({
                'rank': idx,
                'task': {
                    'id': task.get('id'),
                    'title': task['title'],
                    'due_date': task['due_date'],
                    'estimated_hours': task['estimated_hours'],
                    'importance': task['importance']
                },
                'score': task['score']['total'],
                'reason': task['score']['explanation'],
                'breakdown': task['score']['breakdown']
            })
        
        return Response({
            'recommendations': recommendations,
            'strategy_used': strategy,
            'message': f"Here are your top {len(recommendations)} tasks to focus on today"
        })
