from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import Task

@shared_task
def send_task_assigned_email(user_email, task_title):
    subject = "New Task Assigned"
    message = f"You have been assigned a new task: {task_title}. Please check your dashboard."
    send_mail(subject, message, 'noreply@mytask.com', [user_email])

@shared_task
def send_due_date_reminders():
    tasks_due_soon = Task.objects.filter(due_date__lte=now() + timedelta(days=1), status="Pending")

    for task in tasks_due_soon:
        subject = "Task Due Soon!"
        message = f"Reminder: Your task '{task.title}' is due soon. Please complete it before {task.due_date}."
        send_mail(subject, message, 'noreply@mytask.com', [task.user.email])