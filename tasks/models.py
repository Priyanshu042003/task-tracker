from django.db import models
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=50, choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")])
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=[("Pending", "Pending"), ("Completed", "Completed")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Notify WebSocket Clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "task_updates",
            {
                "type": "task_update",
                "message": {
                    "id": self.id,
                    "title": self.title,
                    "status": self.status,
                    "priority": self.priority,
                    "due_date": self.due_date.strftime("%Y-%m-%d"),
                    "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        )