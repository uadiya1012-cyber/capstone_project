from django.http import HttpResponseForbidden
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('Танд энэ үйлдлийг хийх эрх байхгүй байна.')
            
        return wrap
    return decorator