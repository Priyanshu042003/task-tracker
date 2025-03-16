from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Count
from concurrent.futures import ThreadPoolExecutor
from .celeryTask import send_task_assigned_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Task
from django.db import connection
import json
import redis

redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, decode_responses=True)

# Create Task
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        data = json.loads(request.body)

        task = Task.objects.create(
            user=request.user,
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'Low'),
            due_date=data['due_date'],
            status=data.get('status', 'Pending')
        )

        send_task_assigned_email.delay(request.user.email, data['title'])

        return JsonResponse({'message': 'Task created successfully', 'task_id': task.id}, status=201)
    
    except KeyError:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

# List Tasks with Filtering & Pagination
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    due_date = request.GET.get('due_date', '')
    page_number = request.GET.get('page', '1')

    cache_key = f"tasks_{request.user.id}_pr{priority}_st{status}_dd{due_date}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return JsonResponse(json.loads(cached_data), status=200) 

    tasks = Task.objects.filter(user=request.user)

    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    if due_date:
        tasks = tasks.filter(due_date=due_date)

    paginator = Paginator(tasks, 10)
    page_obj = paginator.get_page(page_number)

    task_list = [
        {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'status': task.status,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        } for task in page_obj
    ]

    response_data = {
        'tasks': task_list,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number
    }

    redis_client.setex(cache_key, 60, json.dumps(response_data))

    return JsonResponse(response_data, status=200)

# Retrieve, Update, and Delete Task
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'GET':
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'status': task.status,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse(task_data, status=200)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.priority = data.get('priority', task.priority)
            task.due_date = data.get('due_date', task.due_date)
            task.status = data.get('status', task.status)
            task.save()
            return JsonResponse({'message': 'Task updated successfully'}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully'}, status=200)

# Report for all Tasks
def count_completed_tasks():
    connection.close()
    return Task.objects.filter(status="Completed").count()

def count_pending_tasks():
    connection.close()
    return Task.objects.filter(status="Pending").count()

def group_tasks_by_priority():
    connection.close()
    return list(Task.objects.values('priority').annotate(count=Count('priority')))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    with ThreadPoolExecutor() as executor:
        future_completed = executor.submit(count_completed_tasks)
        future_pending = executor.submit(count_pending_tasks)
        future_priority = executor.submit(group_tasks_by_priority)

        completed_tasks = future_completed.result()
        pending_tasks = future_pending.result()
        priority_distribution = future_priority.result()

    report_data = {
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "tasks_by_priority": priority_distribution,
    }

    return JsonResponse(report_data, status=200)