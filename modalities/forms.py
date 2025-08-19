from django import forms
from .models import Category, SubCategory


class CategoryForm(forms.ModelForm):
    """
    Form para crear/editar categorías.
    """

    class Meta:
        model = Category
        fields = ["name", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "is_active": forms.CheckboxInput(attrs={"data-plugin-ios-switch": ""}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(self.instance, "pk", None):
            self.fields["is_active"].initial = True


class CategorySearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre...',
            'autocomplete': 'off'
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

    def clean_is_active(self):
        val = self.cleaned_data.get('is_active')
        if val == '':
            return None
        return val == 'True'


class SubCategoryForm(forms.ModelForm):
    """
    Form para crear/editar sub categorías.
    """

    class Meta:
        model = SubCategory
        fields = [
            "category",
            "name",
            "price",
            "registration_price",
            "tuition_price",
            "certification_price",
            "exam_price",
            "opening_commission_amount",
            "closing_commission_amount",
            "new_opening_commission_amount",
            "threshold_sales_amount",
            "commission_amount_general_public",
            "is_general_public",
            "is_active"
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off", "maxlength": 50}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "registration_price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "tuition_price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "certification_price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "exam_price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "opening_commission_amount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "closing_commission_amount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "new_opening_commission_amount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "threshold_sales_amount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "commission_amount_general_public": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "is_general_public": forms.CheckboxInput(attrs={"class": "form-check-input", "data-plugin-ios-switch": ""}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input", "data-plugin-ios-switch": ""}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("name")
        if not getattr(self.instance, "pk", None):
            self.fields["is_active"].initial = True


class SubCategorySearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre...',
            'autocomplete': 'off'
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

    def clean_is_active(self):
        val = self.cleaned_data.get('is_active')
        if val == '':
            return None
        return val == 'True'