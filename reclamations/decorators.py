from django.shortcuts import redirect
from django.contrib import messages

def role_required(*roles):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login_reclamation')

            if not request.user.groups.filter(name__in=roles).exists():

                messages.error(
                    request,
                    "⛔ Accès non autorisé."
                )

                return redirect('login_reclamation')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator