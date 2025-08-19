from datetime import date

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.forms import ModelForm

from .models import Employee
from users.models import CustomUser


def copy_group_permissions(user: CustomUser, group: Group) -> None:
    """
    Copia TODOS los permisos del grupo al usuario (sin asignar el grupo).
    Nota: set() reemplaza cualquier permiso previo del usuario.
    """
    if group is None:
        return
    perms = group.permissions.all()
    user.user_permissions.set(perms)
    user.save(update_fields=[])

class BaseEmployeeForm(ModelForm):
    """
    - Apaga required HTML y autocomplete en todos los widgets.
    - Valida referencia única (respetando edición).
    - Valida birthdate no futura.
    - Ajusta phone_number_2 como opcional.
    """
    class Meta:
        model = Employee
        fields = [
            "address",
            "birthdate",
            "commission_general_public",
            "phone_number",
            "phone_number_2",
            "picture",
            "reference",
        ]
        widgets = {
            "birthdate": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-control", "data-plugin-datepicker": ""}),
            "address": forms.Textarea(attrs={"class": "form-control", "autocomplete": "off", "rows": 5}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "phone_number_2": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "reference": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "commission_general_public": forms.CheckboxInput(attrs={"data-plugin-ios-switch": ""}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Desactivar HTML required y autocomplete en todos los campos del form
        for field in self.fields.values():
            field.widget.attrs.pop("required", None)
            field.widget.attrs["autocomplete"] = "off"

        # phone_number_2 opcional
        if "phone_number_2" in self.fields:
            self.fields["phone_number_2"].required = False

        self.fields["birthdate"].input_format = ("%Y-%m-%d")

        if self.instance and self.instance.pk and self.instance.birthdate:
            self.initial["birthdate"] = self.instance.birthdate.strftime("%Y-%m-%d")

    # --- Validaciones de Employee ---
    def clean_reference(self):
        ref = (self.cleaned_data.get("reference") or "").strip()
        if not ref:
            return ref
        qs = Employee.objects.filter(reference=ref)
        # Si es edición, excluir la instancia actual
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Esta referencia ya existe.")
        return ref

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        if birthdate and birthdate > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return birthdate


class UserFieldsMixin(forms.Form):
    """
    Campos y validaciones para el usuario enlazado al Employee.
    - Reutilizable en create/update.
    - Valida unicidad de email respetando la edición.
    """
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "off", "autofocus": True}),
    )
    first_name = forms.CharField(
        label="Nombre(s)",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    is_active = forms.BooleanField(
        label="Activo",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"data-plugin-ios-switch": ""}),
    )

    def __init__(self, *args, **kwargs):
        # Primero deja que ModelForm/Padres construyan fields/instance
        super().__init__(*args, **kwargs)

        # Si hay instancia de Employee con user, precargar iniciales
        instance = getattr(self, "instance", None)
        if instance and getattr(instance, "user", None):
            user = instance.user
            self.fields["email"].initial = user.email
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["is_active"].initial = user.is_active

        # Apagar required HTML & autocomplete para estos campos (consistencia)
        for name in ("email", "first_name", "last_name"):
            self.fields[name].widget.attrs.pop("required", None)
            self.fields[name].widget.attrs["autocomplete"] = "off"

    def clean_email(self):
        # Normalizar y validar unicidad respetando edición
        email = (self.cleaned_data.get("email") or "").strip().lower()
        qs = CustomUser.objects.filter(email=email)
        instance = getattr(self, "instance", None)
        # Si estamos editando y el employee tiene user, excluirlo
        if instance and getattr(instance, "user_id", None):
            qs = qs.exclude(pk=instance.user_id)
        if qs.exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


class PasswordAndGroupMixin(forms.Form):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    group = forms.ModelChoiceField(
        label="Grupo",
        queryset=Group.objects.all(),
        required=True,
        help_text="Selecciona un grupo para copiar sus permisos al usuario",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            # raise forms.ValidationError("Las contraseñas no coinciden.")
            self.add_error(None, "Las contraseñas no coinciden.")
        # Validaciones de robustez de Django (producción)
        if p1:
            validate_password(p1)  # Si falla, lanza ValidationError con mensajes adecuados
        return p2


class EmployeeCreationForm(UserFieldsMixin, PasswordAndGroupMixin, BaseEmployeeForm):
    """
    Crea CustomUser + Employee y copia permisos del grupo (NO asigna el grupo).
    Todo ocurre en una transacción atómica.
    """
    class Meta(BaseEmployeeForm.Meta):
        # Importante: Meta.fields solo debe contener campos del modelo Employee
        # fields = BaseEmployeeForm.Meta.fields
        fields = [
            "email",
            "group",
            "first_name",
            "last_name",
            "reference",
            "address",
            "birthdate",
            "phone_number",
            "phone_number_2",
            "password1",
            "password2",
            "picture",
            "commission_general_public",
            "is_active"
        ]

    @transaction.atomic
    def save(self, commit: bool = True):
        # 1) Crear el usuario
        email = self.cleaned_data["email"]  # ya normalizado en clean_email
        pwd = self.cleaned_data["password1"]
        is_active = self.cleaned_data.get("is_active", True)

        user = CustomUser.objects.create_user(email=email, password=pwd, is_active=is_active)
        user.first_name = (self.cleaned_data.get("first_name") or "").strip()
        user.last_name = (self.cleaned_data.get("last_name") or "").strip()
        user.save()

        # 2) Crear el empleado asociado (aún sin commitear si commit=False)
        emp = super().save(commit=False)  # ModelForm.save(commit=False)
        emp.user = user
        if commit:
            emp.save()

        # 3) Copiar permisos desde el grupo seleccionado
        selected_group = self.cleaned_data.get("group")
        copy_group_permissions(user, selected_group)

        return emp


class EmployeeUpdateForm(UserFieldsMixin, BaseEmployeeForm):
    """
    Edita Employee + actualiza datos del CustomUser relacionado.
    """
    class Meta(BaseEmployeeForm.Meta):
        # Importante: Meta.fields solo debe contener campos del modelo Employee
        # fields = BaseEmployeeForm.Meta.fields
        fields = [
            "email",
            "first_name",
            "last_name",
            "reference",
            "address",
            "birthdate",
            "phone_number",
            "phone_number_2",
            "picture",
            "commission_general_public",
            "is_active"
        ]

    @transaction.atomic
    def save(self, commit: bool = True):
        # 1) Preparar Employee sin guardar
        emp = super().save(commit=False)

        # 2) Actualizar el User relacionado
        user = emp.user
        user.email = self.cleaned_data["email"]  # ya normalizado en clean_email
        user.first_name = (self.cleaned_data.get("first_name") or "").strip()
        user.last_name = (self.cleaned_data.get("last_name") or "").strip()
        user.is_active = self.cleaned_data.get("is_active", True)
        user.full_clean()  # valida campos del User
        user.save()

        # 3) Guardar Employee
        if commit:
            emp.save()

        return emp


class EmployeeSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo, nombre, apellido, referencia, tel...',
            'autocomplete': 'off'
        })
    )
    commission_general_public = forms.ChoiceField(
        required=False,
        label='Recibe comisión',
        choices=[
            ('', '-----'),
            ('True', 'Sí'),
            ('False', 'No'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control mb-3'
        })
    )
    is_active = forms.ChoiceField(
        required=False,
        label='Activo',
        choices=[
            ('', '-----'),
            ('True', 'Sí'),
            ('False', 'No'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control mb-3'
        })
    )

    def clean_commission_general_public(self):
        val = self.cleaned_data.get('commission_general_public')
        if val == '':
            return None
        return val == 'True'

    def clean_is_active(self):
        val = self.cleaned_data.get('is_active')
        if val == '':
            return None
        return val == 'True'


class UserPermissionsForm(forms.Form):
    """Form simple para asignar permisos directos a un usuario."""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        permissions_qs = kwargs.pop("permissions_qs", Permission.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["permissions"].queryset = permissions_qs
