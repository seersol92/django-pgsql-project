from django.urls import path
from . import views

urlpatterns = [
    path('', views.todo_list, name="todo_list"),
    path('create/', views.todo_create, name='todo_create'),
    path('update/<int:pk>/', views.todo_update, name='todo_update'),
    path('delete/<int:pk>/', views.todo_delete, name='todo_delete'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
]
