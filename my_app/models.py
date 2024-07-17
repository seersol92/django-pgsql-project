from django.db import models
from django.contrib.auth.models import User


# Create your models here.

def todo_upload_path(instance, filename):
    return f'uploads/{instance.created_by.username}/{filename}'

class TodoItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, null=True, default=None)
    file = models.FileField(upload_to=todo_upload_path, blank=True, null=True)

    def __str__(self):
        return self.title