# utils/forms.py
from django import forms

class ErrorClassMixin:
    """
    Añade 'error_class' al atributo 'class' de los widgets con error.
    - No agrega clases base ni data-*.
    - Respeta las clases que ya tengas en cada widget.
    """
    error_class = "error"
    error_attr  = "class"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound:
            return

        # Fuerza validación una vez
        _ = self.errors

        for name, field in self.fields.items():
            if name not in self.errors:
                continue

            w = field.widget
            existing = w.attrs.get(self.error_attr, "")
            classes = existing.split()
            # if isinstance(existing, str):
            #     classes = existing.split()
            # elif isinstance(existing, (list, tuple, set)):
            #     classes = [str(x) for x in existing]
            # else:
            #     classes = [str(existing)] if existing else []

            if self.error_class not in classes:
                classes.append(self.error_class)

            w.attrs[self.error_attr] = " ".join(
                c for c in classes if isinstance(c, str) and c
            )

class ErrorForm(ErrorClassMixin, forms.Form):
    pass

class ErrorModelForm(ErrorClassMixin, forms.ModelForm):
    pass



# from django import forms
# from django.utils.html import strip_tags

# class ErrorClassMixin:
#     """
#     - En _init_, si el form está ligado, valida y:
#       * añade 'error' a la clase del widget si el campo tiene errores
#       * expone el mensaje en data-error y crea soporte ARIA
#     - No añade clases base; respeta lo que ya exista en cada widget.
#     """
#     error_class = "error"          # Clase CSS a añadir en campos con error
#     error_attr  = "class"          # Atributo donde se agregará la clase
#     error_data_attr = "data-error" # Atributo con el texto del error
#     error_id_prefix = "err"        # Prefijo del id del contenedor de error (para ARIA)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if not self.is_bound:
#             return

#         # Dispara validación una vez
#         _ = self.errors

#         # Marca campos con error
#         for name, field in self.fields.items():
#             if name not in self.errors:
#                 continue

#             w = field.widget

#             # 1) Añadir clase 'error' sin pisar clases existentes
#             current = w.attrs.get(self.error_attr, "")
#             tokens = current.split()
#             if self.error_class and self.error_class not in tokens:
#                 tokens.append(self.error_class)
#                 w.attrs[self.error_attr] = " ".join(t for t in tokens if t)

#             # 2) Adjuntar mensaje en data-error (texto plano)
#             msg = " ".join(strip_tags(e) for e in self.errors.get(name, []))
#             w.attrs[self.error_data_attr] = msg

#             # 3) Accesibilidad: aria-invalid y aria-describedby apuntando al id del error
#             err_id = f"{self.error_id_prefix}-{self._class_._name_}-{name}"
#             w.attrs["data-error-id"] = err_id
#             w.attrs["aria-invalid"] = "true"
#             if "aria-describedby" in w.attrs:
#                 w.attrs["aria-describedby"] += f" {err_id}"
#             else:
#                 w.attrs["aria-describedby"] = err_id


# class ErrorsForm(ErrorClassMixin, forms.Form):
#     """Form base que añade 'error' y data-error en _init_."""
#     pass


# class ErrorsModelForm(ErrorClassMixin, forms.ModelForm):
#     """ModelForm base que añade 'error' y data-error en _init_."""
#     pass
