from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Case, When, Value, IntegerField
from .models import Todo
from .forms import TodoForm

class TodoListView(ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    # ordering = ['is_resolved', '-priority', 'due_date']  # Unresolved first, then by priority (critical first), then by due date
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter', 'all')
        search_query = self.request.GET.get('search', '')
        priority_filter = self.request.GET.get('priority', '')
        tag_filter = self.request.GET.get('tag', '')
        
        # Search by title
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        # Filter by priority
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by tag
        if tag_filter:
            queryset = queryset.filter(tags__icontains=tag_filter)
        
        # Status filters
        if filter_type == 'pending':
            queryset = queryset.filter(is_resolved=False)
        elif filter_type == 'completed':
            queryset = queryset.filter(is_resolved=True)
        elif filter_type == 'urgent':
            # Urgent: unresolved and due within 2 days or overdue
            from django.utils import timezone
            from datetime import timedelta
            urgent_date = timezone.now() + timedelta(days=2)
            queryset = queryset.filter(
                is_resolved=False,
                due_date__lte=urgent_date,
                due_date__isnull=False
            )
        
        # Add custom sorting logic at the end of the method
        queryset = queryset.annotate(
            priority_order=Case(
                When(priority='critical', then=Value(1)),
                When(priority='high', then=Value(2)),
                When(priority='medium', then=Value(3)),
                When(priority='low', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
        ).order_by('is_resolved', 'priority_order', 'due_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get('filter', 'all')
        context['current_view'] = self.request.GET.get('view', 'list')
        context['search_query'] = self.request.GET.get('search', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['tag_filter'] = self.request.GET.get('tag', '')
        
        # Get all unique tags for the filter dropdown
        all_tags = set()
        for todo in Todo.objects.all():
            all_tags.update(todo.get_tags_list())
        context['all_tags'] = sorted(all_tags)
        
        return context

class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo-list')

class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo-list')

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ['todo/todo_form_partial.html']
        return [self.template_name]

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'status': 'success'})
        return super().form_valid(form)

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo-list')

class TodoToggleStatusView(View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk)
        todo.is_resolved = not todo.is_resolved
        todo.save()
        return redirect('todo-list')

class TodoCalendarView(ListView):
    model = Todo
    template_name = 'todo/todo_calendar.html'
    context_object_name = 'todos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from datetime import datetime
        import calendar
        
        # Get year and month from query params or use current
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        
        # Create calendar
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Get todos for this month
        todos_by_date = {}
        for todo in self.get_queryset():
            if todo.due_date:
                if todo.due_date.year == year and todo.due_date.month == month:
                    day = todo.due_date.day
                    if day not in todos_by_date:
                        todos_by_date[day] = []
                    todos_by_date[day].append(todo)
        
        # Calculate previous and next month
        if month == 1:
            prev_month, prev_year = 12, year - 1
        else:
            prev_month, prev_year = month - 1, year
            
        if month == 12:
            next_month, next_year = 1, year + 1
        else:
            next_month, next_year = month + 1, year
        
        context.update({
            'calendar': cal,
            'year': year,
            'month': month,
            'month_name': month_name,
            'todos_by_date': todos_by_date,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
        })
        
        return context
