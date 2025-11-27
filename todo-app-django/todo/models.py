from django.db import models
from django.utils import timezone
from datetime import timedelta

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Default is medium, but save() will overwrite this if due_date exists
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags (e.g., work, personal, urgent)")

    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def save(self, *args, **kwargs):
        # Automatically set priority based on due date
        if self.due_date:
            now = timezone.now()
            time_remaining = self.due_date - now
            
            # Less than 1 day (or overdue) = Critical
            if time_remaining <= timedelta(days=1):
                self.priority = 'critical'
            # Less than 3 days = High
            elif time_remaining <= timedelta(days=3):
                self.priority = 'high'
            # Less than 7 days = Medium
            elif time_remaining <= timedelta(days=7):
                self.priority = 'medium'
            # More than a week = Low
            else:
                self.priority = 'low'
        else:
            # No due date = Low
            self.priority = 'low'
            
        super().save(*args, **kwargs)