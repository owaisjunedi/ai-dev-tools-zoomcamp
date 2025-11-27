from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        # Removed 'priority' from fields
        fields = ['title', 'description', 'due_date', 'tags', 'is_resolved']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter todo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., work, personal, urgent'}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }