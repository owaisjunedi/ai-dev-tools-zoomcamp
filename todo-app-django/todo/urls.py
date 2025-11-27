from django.urls import path
from .views import TodoListView, TodoCreateView, TodoUpdateView, TodoDeleteView, TodoToggleStatusView, TodoCalendarView

urlpatterns = [
    path('', TodoListView.as_view(), name='todo-list'),
    path('calendar/', TodoCalendarView.as_view(), name='todo-calendar'),
    path('create/', TodoCreateView.as_view(), name='todo-create'),
    path('<int:pk>/update/', TodoUpdateView.as_view(), name='todo-update'),
    path('<int:pk>/delete/', TodoDeleteView.as_view(), name='todo-delete'),
    path('<int:pk>/toggle/', TodoToggleStatusView.as_view(), name='todo-toggle'),
]
