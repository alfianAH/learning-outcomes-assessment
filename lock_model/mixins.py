from django.shortcuts import redirect
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages


class LockedObjectPermissionMixin:
    access_denied_message: str = ''

    def get_locked_object_model(self):
        raise NotImplementedError
    
    def get_locked_object_parent_model(self):
        raise NotImplementedError
    
    def get_access_denied_url(self):
        if self.success_url:
            return self.success_url
        
        raise ImproperlyConfigured(
            "No Access Denied URL to redirect to. Either provide a url or define")

    def dispatch(self, request, *args, **kwargs):
        parent_model = self.get_locked_object_parent_model()
        child_model = self.get_locked_object_model()

        if parent_model is not None:
            is_locked: bool = getattr(parent_model, 'is_{}_locked'.format(child_model.__name__.lower()))
            if is_locked:
                messages.error(request, self.access_denied_message)
                return redirect(self.get_access_denied_url())

        return super().dispatch(request, *args, **kwargs)
