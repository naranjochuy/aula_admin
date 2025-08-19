import unicodedata
from collections import defaultdict
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.text import capfirst
from django.views.generic import DeleteView
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Lower
from django.db.models import Q

from utils.db_functions import Unaccent
from utils.mixins.crud import CreateMixin, DetailMixin, ListMixin, UpdateMixin
from .forms import GroupForm, GroupSearchForm


EXCLUDED_APP_LABELS = {"admin", "contenttypes", "sessions", "users"}  # ignorar lo pedido: session, contente, log (admin/logentry cae en 'admin')

# Orden sugerido de acciones
ACTION_ORDER = {"view": 1, "add": 2, "change": 3, "delete": 4}

# Etiquetas en español para acciones conocidas
ACTION_ES = {
    "view": "Ver",
    "add": "Crear",
    "change": "Editar",
    "delete": "Eliminar",
}

def allowed_app_labels():
    """
    Devuelve el conjunto de app_labels permitidos, excluyendo los contrib/EXCLUDED.
    """
    labels = set()
    for app in settings.INSTALLED_APPS:
        short = app.split(".")[-1]
        if app.startswith("django.contrib") or short in EXCLUDED_APP_LABELS:
            continue
        labels.add(short)
    # También permitimos 'users' explícitamente por si el proyecto lo requiere
    # labels.add("users")
    # labels.add("employees")
    return labels

def filtered_permissions_qs():
    """
    QS de permisos solo para los modelos de apps permitidas y excluyendo logentry.
    """
    apps_ok = allowed_app_labels()
    cts = ContentType.objects.filter(app_label__in=apps_ok).exclude(model="logentry")
    return Permission.objects.filter(content_type__in=cts).select_related("content_type").order_by(
        "content_type__app_label", "content_type__model", "codename"
    )

def group_permissions_by_model(permissions):
    """
    Agrupa permisos por modelo y devuelve una lista de items:
    [
      {
        "model_label": "Empleado",
        "items": [ {"id": 1, "label": "Ver", "codename": "view_employee"}, ...]
      },
      ...
    ]
    """
    g = defaultdict(list)
    for p in permissions:
        ct = p.content_type
        # Intentar nombre de modelo legible
        model_cls = ct.model_class()
        if model_cls is not None:
            model_label = capfirst(str(model_cls._meta.verbose_name))
        else:
            model_label = capfirst(ct.model.replace("_", " "))

        # Derivar la acción desde el codename (view/add/change/delete/otro)
        action = p.codename.split("_", 1)[0]
        label = ACTION_ES.get(action, capfirst(p.name))

        g[(ct.app_label, model_label)].append({
            "id": p.id,
            "label": label,
            "codename": p.codename,
            "action_order": ACTION_ORDER.get(action, 99),
        })

    # Ordenar por app -> modelo, y dentro por acción
    result = []
    for (app_label, model_label), items in sorted(g.items(), key=lambda x: (x[0][0], x[0][1].lower())):
        items.sort(key=lambda it: (it["action_order"], it["label"]))
        result.append({
            "app_label": app_label,
            "model_label": model_label,
            "items": items
        })
    return result

class GroupListView(ListMixin):
    model = Group
    search_form = GroupSearchForm
    template_name = "users/groups/list.html"
    active_menu = "groups"
    permission_required = "auth.view_group"
    allowed_sort_fields = [
        'name',
    ]
    default_ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        self.form = GroupSearchForm(self.request.GET)
        if self.form.is_valid():
            q = self.form.cleaned_data['q']

            def normalize(text):
                txt = unicodedata.normalize('NFKD', text or '')
                return ''.join(c for c in txt if not unicodedata.combining(c)).lower()

            q_norm = normalize(q)

            # Anotamos campos sin acentos y en minúsculas
            qs = qs.annotate(
                name_norm=Lower(Unaccent('name')),
            )

            if q_norm:
                qs = qs.filter(
                    Q(name_norm__contains=q_norm)
                )

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


class GroupCreateView(CreateMixin):
    model = Group
    form_class = GroupForm
    template_name = "users/groups/form.html"
    active_menu = "groups"
    success_url = reverse_lazy("users:group_list")
    permission_required = "auth.add_group"
    success_message = "Grupo creado correctamente."
    error_message = "Error al crear el grupo."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["permissions_qs"] = filtered_permissions_qs()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perms_qs = self.get_form().fields["permissions"].queryset
        ctx["perms_by_model"] = group_permissions_by_model(perms_qs)

        # IDs seleccionados (para mantener checks tras validación)
        if self.request.method == "POST":
            selected = set(map(int, self.request.POST.getlist("permissions")))
        else:
            selected = set()
        ctx["selected_perm_ids"] = selected
        ctx["mode"] = "create"
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        resp = super().form_valid(form)
        perms = form.cleaned_data.get("permissions") or []
        self.object.permissions.set(perms)
        return resp


class GroupUpdateView(UpdateMixin):
    model = Group
    form_class = GroupForm
    template_name = "users/groups/form.html"
    active_menu = "groups"
    success_url = reverse_lazy("users:group_list")
    permission_required = "auth.change_group"
    success_message = "Grupo actualizado correctamente."
    error_message = "Error al actualizar el grupo."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["permissions_qs"] = filtered_permissions_qs()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        perms_qs = self.get_form().fields["permissions"].queryset
        ctx["perms_by_model"] = group_permissions_by_model(perms_qs)

        if self.request.method == "POST":
            selected = set(map(int, self.request.POST.getlist("permissions")))
        else:
            selected = set(self.object.permissions.values_list("id", flat=True))
        ctx["selected_perm_ids"] = selected
        ctx["mode"] = "update"
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        resp = super().form_valid(form)
        perms = form.cleaned_data.get("permissions") or []
        self.object.permissions.set(perms)
        return resp


class GroupDetailView(DetailMixin):
    model = Group
    template_name = 'users/groups/detail.html'
    active_menu = "groups"
    permission_required = "auth.delete_group"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Todos los permisos filtrados como en create/update
        perms_qs = filtered_permissions_qs()

        # Agrupados por modelo (igual que en create/update)
        ctx["perms_by_model"] = group_permissions_by_model(perms_qs)

        # IDs de los permisos asignados a este grupo
        ctx["selected_perm_ids"] = set(
            self.object.permissions.values_list("id", flat=True)
        )

        return ctx


class GroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Group
    template_name = "users/groups/confirm_delete.html"
    active_menu = "groups"
    success_url = reverse_lazy("users:group_list")
    permission_required = "auth.delete_group"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Todos los permisos filtrados como en create/update
        perms_qs = filtered_permissions_qs()

        # Agrupados por modelo (igual que en create/update)
        ctx["perms_by_model"] = group_permissions_by_model(perms_qs)

        # IDs de los permisos asignados a este grupo
        ctx["selected_perm_ids"] = set(
            self.object.permissions.values_list("id", flat=True)
        )

        return ctx

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Grupo eliminado correctamente.")
        except IntegrityError as e:
            messages.error(request, "No se pudo eliminar el grupo.")
        return redirect(self.success_url)
