# employees/views.py
import logging
import unicodedata

from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction, IntegrityError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.db.models.functions import Lower
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Employee
from .forms import (
    # EmployeeForm,
    EmployeeCreationForm,
    EmployeeUpdateForm,
    EmployeeSearchForm
)
from utils.db_functions import Unaccent

from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.contrib.auth.models import Permission
from utils.permissions import filtered_permissions_qs, group_permissions_by_model
from .forms import UserPermissionsForm
from utils.mixins.crud import CreateMixin, DetailMixin, ListMixin, UpdateMixin
from utils.db_functions import Unaccent


logger = logging.getLogger(__name__)


class LoggingMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            logger.exception("Unhandled exception in %s", self.__class__.__name__)
            raise


class EmployeeListView(LoginRequiredMixin, LoggingMixin, ListView):
    model               = Employee
    template_name       = 'employees/list.html'
    context_object_name = 'employees'
    paginate_by         = 2
    allowed_sort_fields = [
        'user__first_name',
        'user__last_name',
        'user__is_active',
        'user__email',
        'reference',
        'phone_number',
        'commission_general_public'
    ]
    default_ordering = ['user__email']

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')
        self.form = EmployeeSearchForm(self.request.GET)
        if self.form.is_valid():
            q   = self.form.cleaned_data['q']
            com = self.form.cleaned_data['commission_general_public']
            act = self.form.cleaned_data['is_active']

            def normalize(text):
                txt = unicodedata.normalize('NFKD', text or '')
                return ''.join(c for c in txt if not unicodedata.combining(c)).lower()

            q_norm = normalize(q)

            # Anotamos campos sin acentos y en minúsculas
            qs = qs.annotate(
                email_norm=Lower(Unaccent('user__email')),
                fn_norm   =Lower(Unaccent('user__first_name')),
                ln_norm   =Lower(Unaccent('user__last_name')),
                pn1_norm  =Lower(Unaccent('phone_number')),
                pn2_norm  =Lower(Unaccent('phone_number_2')),
                ref_norm  =Lower(Unaccent('reference')),
            )

            if q_norm:
                qs = qs.filter(
                    Q(email_norm__contains=q_norm) |
                    Q(fn_norm__contains=q_norm)    |
                    Q(ln_norm__contains=q_norm)    |
                    Q(pn1_norm__contains=q_norm)   |
                    Q(pn2_norm__contains=q_norm)   |
                    Q(ref_norm__contains=q_norm)
                )

            if com is not None:
                qs = qs.filter(commission_general_public=com)
            if act is not None:
                qs = qs.filter(user__is_active=act)

            ordering = self.request.GET.get('ordering')
            if ordering:
                # permitimos "-campo" o "campo"
                raw = ordering.lstrip('-')
                if raw in self.allowed_sort_fields:
                    qs = qs.order_by(ordering)
                else:
                    qs = qs.order_by(*self.default_ordering)
            else:
                qs = qs.order_by(*self.default_ordering)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = getattr(self, 'form', EmployeeSearchForm())

        # Tomamos TODOS los GET params excepto 'page'
        params = self.request.GET.copy()
        params.pop('page', None)

        # Lo guardamos en el contexto como string ya codificado
        ctx['querystring'] = params.urlencode()

        # Para saber en la plantilla cuál es el orden actual
        ctx['current_order'] = self.request.GET.get('ordering', '')
        return ctx


class EmployeeCreateView(LoginRequiredMixin, LoggingMixin, CreateView):
    model         = Employee
    form_class    = EmployeeCreationForm
    template_name = 'employees/form.html'
    success_url   = reverse_lazy('employees:list')

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Empleado creado correctamente.")
        return response

    def form_invalid(self, form):
        logger.error("Create form errors: %s", form.errors)
        messages.error(self.request, "Error al crear al empleado.")
        return super().form_invalid(form)


class EmployeeUpdateView(LoginRequiredMixin, LoggingMixin, UpdateView):
    model         = Employee
    form_class    = EmployeeUpdateForm
    template_name = 'employees/form.html'
    success_url   = reverse_lazy('employees:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Empleado actualizado correctamente.")
        return response

    def form_invalid(self, form):
        logger.error("Update form errors: %s", form.errors)
        messages.error(self.request, "Error al actualizar el empleado.")
        return super().form_invalid(form)


class EmployeeDeleteView(LoginRequiredMixin, LoggingMixin, DeleteView):
    model         = Employee
    template_name = 'employees/confirm_delete.html'
    success_url   = reverse_lazy('employees:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 'object' es el Employee; le añadimos también su CustomUser
        context['user'] = self.object.user
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Empleado eliminado correctamente.")
        except IntegrityError as e:
            logger.error("Error al eliminar empleado")
            messages.error(request, "No se pudo eliminar el empleado.")
        return redirect(self.success_url)


class EmployeeDetailView(LoginRequiredMixin, LoggingMixin, DetailView):
    model           = Employee
    template_name   = 'employees/detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Añadimos el usuario en contexto (opcionalmente)
        ctx['user'] = self.object.user
        return ctx

class DashboardView(LoginRequiredMixin, LoggingMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_empleados'] = Employee.objects.count()
        return ctx


class EmployeePermissionsUpdateView(LoginRequiredMixin, LoggingMixin, FormView):
    template_name = 'employees/permissions.html'
    form_class = UserPermissionsForm
    success_url = reverse_lazy('employees:list')

    def dispatch(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        perms_qs = filtered_permissions_qs()
        kwargs["permissions_qs"] = perms_qs
        if self.request.method == "GET":
            current_ids = list(self.employee.user.user_permissions.values_list("id", flat=True))
            kwargs["initial"] = {"permissions": current_ids}
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perms_qs = filtered_permissions_qs()
        ctx["employee"] = self.employee
        ctx["perms_by_model"] = group_permissions_by_model(perms_qs)
        # seleccionados (para marcar checks)
        if self.request.method == "POST":
            selected = set(map(int, self.request.POST.getlist("permissions")))
        else:
            selected = set(self.employee.user.user_permissions.values_list("id", flat=True))
        ctx["selected_perm_ids"] = selected
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        perms = form.cleaned_data.get("permissions") or []
        user = self.employee.user
        user.user_permissions.set(perms)  # atómico: reemplaza con lo seleccionado
        messages.success(self.request, "Permisos del empleado actualizados correctamente.")
        return redirect(self.get_success_url())