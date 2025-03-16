from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'send_task_reminders_every_hour': {
        'task': 'tasks.tasks.send_due_date_reminders',
        'schedule': crontab(minute=0, hour='*'),
    },
}