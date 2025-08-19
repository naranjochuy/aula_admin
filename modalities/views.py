import unicodedata
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from utils.db_functions import Unaccent
from utils.mixins.crud import CreateMixin, DetailMixin, ListMixin, UpdateMixin
from .forms import CategoryForm, CategorySearchForm, SubCategoryForm, SubCategorySearchForm
from .models import Category, SubCategory


class CategoryListView(ListMixin):
    model = Category
    search_form = CategorySearchForm
    template_name = "modalities/categories/list.html"
    active_menu = "categories"
    permission_required = "auth.view_group"
    allowed_sort_fields = [
        'name',
        'is_active'
    ]
    default_ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        self.form = CategorySearchForm(self.request.GET)
        if self.form.is_valid():
            q = self.form.cleaned_data['q']
            is_active = self.form.cleaned_data['is_active']

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

            if is_active is not None:
                qs = qs.filter(is_active=is_active)

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


class CategoryCreateView(CreateMixin):
    model = Category
    form_class = CategoryForm
    template_name = "modalities/categories/form.html"
    active_menu = "categories"
    success_url = reverse_lazy("modalities:category_list")
    permission_required = "auth.add_group"
    success_message = "Categoría creada correctamente."
    error_message = "Error al crear la categoría."


class CategoryUpdateView(UpdateMixin):
    model = Category
    form_class = CategoryForm
    template_name = "modalities/categories/form.html"
    active_menu = "categories"
    success_url = reverse_lazy("modalities:category_list")
    permission_required = "auth.change_group"
    success_message = "Categoría actualizada correctamente."
    error_message = "Error al actualizar la categoría."


class CategoryDetailView(DetailMixin):
    model = Category
    template_name = 'modalities/categories/detail.html'
    active_menu = "categories"
    permission_required = "auth.delete_group"


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = "modalities/categories/confirm_delete.html"
    active_menu = "categories"
    context_object_name = 'item'
    success_url = reverse_lazy("modalities:category_list")
    permission_required = "auth.delete_group"

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Categoría eliminada correctamente.")
        except IntegrityError as e:
            messages.error(request, "No se pudo eliminar la categoría.")
        return redirect(self.success_url)


class SubCategoryListView(ListMixin):
    model = SubCategory
    search_form = SubCategorySearchForm
    template_name = "modalities/sub_categories/list.html"
    active_menu = "subcategories"
    permission_required = "auth.view_group"
    allowed_sort_fields = [
        'name',
        'is_active'
    ]
    default_ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        self.form = SubCategorySearchForm(self.request.GET)
        if self.form.is_valid():
            q = self.form.cleaned_data['q']
            is_active = self.form.cleaned_data['is_active']

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

            if is_active is not None:
                qs = qs.filter(is_active=is_active)

            ordering = self.request.GET.get('ordering')
            if ordering:
                raw = ordering.lstrip('-')
                if raw in self.allowed_sort_fields:
                    qs = qs.order_by(ordering)
                else:
                    qs = qs.order_by(*self.default_ordering)
            else:
                qs = qs.order_by(*self.default_ordering)

        return qs


class SubCategoryCreateView(CreateMixin):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "modalities/sub_categories/form.html"
    active_menu = "subcategories"
    success_url = reverse_lazy("modalities:sub_category_list")
    permission_required = "auth.add_group"
    success_message = "Sub categoría creada correctamente."
    error_message = "Error al crear la sub categoría."


class SubCategoryUpdateView(UpdateMixin):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "modalities/sub_categories/form.html"
    active_menu = "subcategories"
    success_url = reverse_lazy("modalities:sub_category_list")
    permission_required = "auth.change_group"
    success_message = "Sub categoría actualizada correctamente."
    error_message = "Error al actualizar la sub categoría."


class SubCategoryDetailView(DetailMixin):
    model = SubCategory
    template_name = 'modalities/sub_categories/detail.html'
    active_menu = "subcategories"
    permission_required = "auth.delete_group"


class SubCategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SubCategory
    template_name = "modalities/sub_categories/confirm_delete.html"
    active_menu = "subcategories"
    context_object_name = 'item'
    success_url = reverse_lazy("modalities:sub_category_list")
    permission_required = "auth.delete_group"

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Sub categoría eliminada correctamente.")
        except IntegrityError as e:
            messages.error(request, "No se pudo eliminar la sub categoría.")
        return redirect(self.success_url)
