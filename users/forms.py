from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.models import Group, Permission
from utils.forms import ErrorForm


class LoginForm(ErrorForm, AuthenticationForm):
    username = UsernameField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'autocomplete': 'off',
            'autofocus': True
        })
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'autocomplete': 'off'
        })
    )


class GroupForm(forms.ModelForm):
    """
    Form para crear/editar grupos y asignar permisos.
    Nota: el campo 'permissions' lo vamos a renderizar manualmente (checkboxes agrupados).
    """
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]

    def __init__(self, *args, **kwargs):
        # permissions_qs: queryset filtrado que llega desde la vista
        permissions_qs = kwargs.pop("permissions_qs", Permission.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control", "autocomplete": "off"})
        self.fields["permissions"].queryset = permissions_qs


class GroupSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre...',
            'autocomplete': 'off'
        })
    )
