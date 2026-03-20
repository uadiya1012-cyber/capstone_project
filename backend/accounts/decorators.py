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


# Энд код нь role_required нэртэй декоратор үүсгэж байна. Энэ декоратор нь allowed_roles гэсэн параметрийг авч, тухайн view-д зөвшөөрөгдсөн үүрэгтэй хэрэглэгчид л хандах боломжийг олгоно. Хэрэв хэрэглэгч нэвтэрсэн бөгөөд түүний үүрэг allowed_roles-д байгаа бол view-г ажиллуулна, эс тэгвээс HttpResponseForbidden-ыг буцаана.