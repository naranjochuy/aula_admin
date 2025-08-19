from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from utils.mixins.active_menu import ActiveMenuMixin
from utils.mixins.message import SuccessErrorMessageMixin


class ListMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ActiveMenuMixin,
    ListView
):
    """
    Vista base para lista de objetos con login y permisos
    """
    context_object_name = "objects"
    paginate_by = 2

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = getattr(self, 'form', self.search_form)

        # Tomamos TODOS los GET params excepto 'page'
        params = self.request.GET.copy()
        params.pop('page', None)

        # Lo guardamos en el contexto como string ya codificado
        ctx['querystring'] = params.urlencode()

        params_no_order = params.copy()
        params_no_order.pop('ordering', None)
        ctx['querystring_no_ordering'] = params_no_order.urlencode()

        # Para saber en la plantilla cuál es el orden actual
        ctx['current_order'] = self.request.GET.get('ordering', '')
        return ctx

class CreateMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessErrorMessageMixin,
    ActiveMenuMixin,
    CreateView
):
    """
    Vista base para crear objetos con login, permisos y mensajes de éxito y error
    """
    pass


class UpdateMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessErrorMessageMixin,
    ActiveMenuMixin,
    UpdateView
):
    """
    Vista base para editar objetos con login, permisos y mensajes de éxito y error
    """
    pass


class DetailMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ActiveMenuMixin,
    DetailView
):
    """
    Vista base para ver detalle de un objeto con login y permisos
    """
    context_object_name = 'item'
