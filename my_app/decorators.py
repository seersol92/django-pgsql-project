from django.shortcuts import redirect

#if user if authenticated then prevent accessing login/register urls
def anonymous_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')  
        return view_func(request, *args, **kwargs)
    return wrapper
