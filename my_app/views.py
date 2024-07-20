from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import messages module
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import TodoItem
from .forms import TodoItemForm
from django.contrib.auth import authenticate, login as login_user, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .decorators import anonymous_required
import redis
from django.core.cache import cache


@anonymous_required
def login(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password)
         
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid User Name!')
            return redirect('/login/')
         
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
         
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login_user(request, user)
            # Log in the user and redirect to the home page upon successful login
            return redirect('/')
    return render(request, 'auth/login.html')


@anonymous_required
def register(request):
     if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
         # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)
        if user.exists():
            # Display an information message if the username is taken
            messages.error(request, "Username already taken!")
            return redirect('/register/')
        
        # Create a new User object with the provided information
        user = User.objects.create_user(
            email=email,
            username=username
        )         
        # Set the user's password and save the user object
        user.set_password(password)
        user.save()
         
        # Display an information message indicating successful account creation
        messages.success(request, "User created Successfully!")
        send_welcome_email(email, username)
        return redirect('/register/')
     return render(request, 'auth/register.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('/login/')


def fetch_and_cache_todos(request, filter_option):
    # Fetch todos based on filter option and update the cached list
    if filter_option == 'my_todos':
        todos = TodoItem.objects.filter(created_by=request.user)
    elif filter_option == 'completed':
        todos = TodoItem.objects.filter(completed=True)
    elif filter_option == 'pending':
        todos = TodoItem.objects.filter(completed=False)
    else:
        todos = TodoItem.objects.all()

    todos = todos.order_by('-created_at')

     # Cache the entire queryset with a specific key
    cache_key = f'cached_todo_list_{filter_option}'

     # Store in cache for subsequent requests (expire in x seconds)
    cache.set(cache_key, todos, timeout=600)
    return todos


@login_required
def todo_list(request):
     # Fetch filter option from query parameters
    filter_option = request.GET.get('filter', 'all')

    # Fetch todos from cache if available
    todos = cache.get(f'cached_todo_list_{filter_option}')

    # If cache is not available or needs to be updated
    if not todos:
        print("fetching from DB")
        todos = fetch_and_cache_todos(request, filter_option)
    else:
        print("fetched cache todos")

    todos_count = todos.count()

    context = {
        'todos': todos,
        'todos_count': todos_count,
        'filter_option': filter_option,
    }

    return render(request, 'todos/index.html', context)


@login_required
def todo_create(request):
    if request.method == 'POST':
        form = TodoItemForm(request.POST, request.FILES)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.created_by = request.user  # Assign the current logged-in user
            todo_item.save()

             # Update or invalidate the cache
            cache.delete_pattern('cached_todo_list_*')

            messages.success(request, 'Todo item created successfully!')  # Add success message
            return redirect('todo_list')
    else:
        form = TodoItemForm()
    return render(request, 'todos/create_todo.html', {'form': form})


@login_required
def todo_update(request, pk):
    todo = get_object_or_404(TodoItem, pk=pk)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            
             # Update or invalidate the cache
            cache.delete_pattern('cached_todo_list_*')

            return redirect('todo_list')
    else:
        form = TodoItemForm(instance=todo)
    return render(request, 'todos/create_todo.html', {'form': form})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(TodoItem, pk=pk)
    if request.method == 'POST':
        todo.delete()
         # Update or invalidate the cache
        cache.delete_pattern('cached_todo_list_*')
        messages.success(request, 'Todo item deleted successfully!')  # Add success message
    return redirect('todo_list')

def send_welcome_email(user_email, username):
    html_message = render_to_string('emails/welcome_email.html', {'user': username})
    plain_message = strip_tags(html_message)  # Strip HTML tags for the plain text message
    send_mail(
        subject='Account Registered',
        message=plain_message,  # Plain text message (fallback for email clients that don't support HTML)
        from_email='seersol@gmail.com',  # Replace with your email address
        recipient_list=[user_email],
        html_message=html_message,  # HTML content of the email
    )


def print_redis_version():
    try:
        # Connect to Redis
        client = redis.Redis(host='redis', port=6379, decode_responses=True)
        # Get Redis server info
        info = client.info()
        # Print Redis server version
        print("Redis server version:", info['redis_version'])
    except redis.ConnectionError as e:
        print("Error connecting to Redis:", e)
