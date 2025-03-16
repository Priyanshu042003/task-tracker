from django.urls import path
from .views import create_task, list_tasks, task_detail, generate_report
from .consumers import TaskConsumer

urlpatterns = [
    path('create/', create_task, name='create_task'),
    path('list/', list_tasks, name='list_tasks'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('report/', generate_report, name='generate_report'),
    path("ws/tasks/", TaskConsumer.as_asgi()),
]