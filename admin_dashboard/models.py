from django.db import models

# Additional admin-specific models can be added here if needed
# For now, we'll use hostel_app models
from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    """
    Model to log admin activities.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who performed the action")
    action = models.CharField(max_length=100, help_text="Action performed (e.g., Added Resident)")
    details = models.TextField(help_text="Additional details about the action")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Time of the action")
    model_name = models.CharField(max_length=50, help_text="Model affected by the action")

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"