from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import messages module
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import TodoItem
from .forms import TodoItemForm


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



def login(request):
    return render(request, 'auth/login.html')

def register(request):
    return render(request, 'auth/register.html')


def todo_list(request):
    send_welcome_email(['hssan@gmail.com', 'amir@gmail.com'])
    todos = TodoItem.objects.all();
    todos_count = todos.count()
    return render(request, 'todos/index.html', {'todos': todos, 'todos_count': todos_count})


def todo_create(request):
    if request.method == 'POST':
        form = TodoItemForm(request.POST)
        print(form.data)
        if form.is_valid():
            form.save()
            send_welcome_email(['hssan@gmail.com'])
            messages.success(request, 'Todo item created successfully!')  # Add success message
            return redirect('todo_list')
    else:
        form = TodoItemForm()
    return render(request, 'todos/create_todo.html', {'form': form})


def send_welcome_email(user_email):
    subject = 'Welcome to !'
    html_message = render_to_string('emails/welcome_email.html', {'user': 'hadi mughal'})
    plain_message = strip_tags(html_message)  # Strip HTML tags for the plain text message
    from_email = 'seersol@gmail.com'  # Replace with your email address or use DEFAULT_FROM_EMAIL
    to_email = user_email  # List of recipient(s) email addresses

    send_mail(
        subject='Your Website - HTML Email',
        message=plain_message,  # Plain text message (fallback for email clients that don't support HTML)
        from_email='your_email@gmail.com',  # Replace with your email address
        recipient_list=user_email,
        html_message=html_message,  # HTML content of the email
    )


def todo_update(request, pk):
    todo = get_object_or_404(TodoItem, pk=pk)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoItemForm(instance=todo)
    return render(request, 'todos/create_todo.html', {'form': form})


def todo_delete(request, pk):
    todo = get_object_or_404(TodoItem, pk=pk)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo item deleted successfully!')  # Add success message
    return redirect('todo_list')
