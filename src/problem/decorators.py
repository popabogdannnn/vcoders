from django.http import HttpResponse
from django.shortcuts import redirect

def authorized_users(authorized_roles):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            groups = None
            if request.user.groups.exists():
                groups = request.user.groups.all()
            
            ok = False
            if request.user.is_superuser:
                ok = True

            if groups != None:
                for group in groups:
                    if ok:
                        break
                    if group.name in authorized_roles: 
                        ok = True

            if(not ok):
                return HttpResponse("Nu ai acces la această resursă")
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator