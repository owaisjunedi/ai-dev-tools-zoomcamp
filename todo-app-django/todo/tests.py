from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo
from .forms import TodoForm


class TodoModelTest(TestCase):
    """Test the Todo model"""
    
    def setUp(self):
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test Description",
            due_date=timezone.now() + timedelta(days=1),
            is_resolved=False
        )
    
    def test_todo_creation(self):
        """Test that a todo is created correctly"""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test Description")
        self.assertFalse(self.todo.is_resolved)
        self.assertIsNotNone(self.todo.created_at)
    
    def test_todo_str_method(self):
        """Test the string representation of a todo"""
        self.assertEqual(str(self.todo), "Test Todo")
    
    def test_todo_default_values(self):
        """Test default values for optional fields"""
        todo = Todo.objects.create(title="Simple Todo")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.is_resolved)


class TodoViewTest(TestCase):
    """Test the Todo views"""
    
    def setUp(self):
        self.client = Client()
        self.todo1 = Todo.objects.create(
            title="Todo 1",
            description="First todo",
            is_resolved=False
        )
        self.todo2 = Todo.objects.create(
            title="Todo 2",
            description="Second todo",
            is_resolved=True
        )
    
    def test_todo_list_view(self):
        """Test that the list view displays all todos"""
        response = self.client.get(reverse('todo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todo 1")
        self.assertContains(response, "Todo 2")
        self.assertTemplateUsed(response, 'todo/todo_list.html')
    
    def test_todo_create_view_get(self):
        """Test GET request to create view"""
        response = self.client.get(reverse('todo-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_form.html')
    
    def test_todo_create_view_post(self):
        """Test POST request to create a new todo"""
        data = {
            'title': 'New Todo',
            'description': 'New Description',
            'is_resolved': False
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
    
    def test_todo_update_view_get(self):
        """Test GET request to update view"""
        response = self.client.get(reverse('todo-update', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_form.html')
        self.assertContains(response, "Todo 1")
    
    def test_todo_update_view_post(self):
        """Test POST request to update a todo"""
        data = {
            'title': 'Updated Todo',
            'description': 'Updated Description',
            'is_resolved': True
        }
        response = self.client.post(reverse('todo-update', args=[self.todo1.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated Todo')
        self.assertTrue(self.todo1.is_resolved)
    
    def test_todo_delete_view_get(self):
        """Test GET request to delete confirmation view"""
        response = self.client.get(reverse('todo-delete', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_confirm_delete.html')
    
    def test_todo_delete_view_post(self):
        """Test POST request to delete a todo"""
        todo_id = self.todo1.pk
        response = self.client.post(reverse('todo-delete', args=[todo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=todo_id).exists())


class TodoFormTest(TestCase):
    """Test the TodoForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        data = {
            'title': 'Test Todo',
            'description': 'Test Description',
            'is_resolved': False
        }
        form = TodoForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_missing_title(self):
        """Test form with missing required title field"""
        data = {
            'description': 'Test Description',
            'is_resolved': False
        }
        form = TodoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_widgets(self):
        """Test that form has correct widgets"""
        form = TodoForm()
        self.assertEqual(
            form.fields['due_date'].widget.input_type,
            'datetime-local'
        )
        self.assertIn('form-control', form.fields['title'].widget.attrs['class'])


class TodoURLTest(TestCase):
    """Test URL routing"""
    
    def test_todo_list_url(self):
        """Test that todo-list URL resolves correctly"""
        url = reverse('todo-list')
        self.assertEqual(url, '/')
    
    def test_todo_create_url(self):
        """Test that todo-create URL resolves correctly"""
        url = reverse('todo-create')
        self.assertEqual(url, '/create/')
    
    def test_todo_update_url(self):
        """Test that todo-update URL resolves correctly"""
        url = reverse('todo-update', args=[1])
        self.assertEqual(url, '/1/update/')
    
    def test_todo_delete_url(self):
        """Test that todo-delete URL resolves correctly"""
        url = reverse('todo-delete', args=[1])
        self.assertEqual(url, '/1/delete/')
