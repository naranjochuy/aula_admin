from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


class SuccessErrorMessageMixin(SuccessMessageMixin):
    """
    Extiende SuccessMessageMixin para también mostrar mensajes de error en form_invalid.
    Usa 'success_message' (ya nativo en Django) y 'error_message' (nuevo).
    """
    error_message = None

    def form_invalid(self, form):
        if self.error_message:
            messages.error(self.request, self.error_message)
        return super().form_invalid(form)
