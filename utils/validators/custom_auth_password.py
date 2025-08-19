# users/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordComplexityValidator:
    """
    Valida que el password cumpla:
      - longitud mínima
      - al menos 1 mayúscula
      - al menos 1 dígito
      - al menos 1 carácter especial (punctuation; no incluye espacios)
    Puedes ajustar opciones desde settings AUTH_PASSWORD_VALIDATORS.
    """

    def __init__(
        self,
        min_length: int = 8,
        require_upper: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        special_chars: str | None = None,  # ej: "!@#$%^&*"
    ):
        self.min_length = int(min_length)
        self.require_upper = require_upper
        self.require_digit = require_digit
        self.require_special = require_special
        self.special_chars = special_chars

        # Si defines special_chars en settings, se usará exactamente ese set.
        # Por defecto usamos "cualquier símbolo de puntuación" (sin espacios).
        if special_chars:
            self._special_re = re.compile(f"[{re.escape(special_chars)}]")
        else:
            self._special_re = re.compile(r"[^\w\s]")  # no alfanumérico y no espacio

    def validate(self, password: str, user=None) -> None:
        pwd = password or ""
        errors: list[str] = []

        if len(pwd) < self.min_length:
            errors.append(_("La contraseña debe tener al menos %(min)d caracteres.") % {"min": self.min_length})

        if self.require_upper and not re.search(r"[A-Z]", pwd):
            errors.append(_("La contraseña debe incluir al menos una letra mayúscula."))

        if self.require_digit and not re.search(r"\d", pwd):
            errors.append(_("La contraseña debe incluir al menos un número."))

        if self.require_special and not self._special_re.search(pwd):
            if self.special_chars:
                errors.append(
                    _("La contraseña debe incluir al menos uno de estos caracteres especiales: %(chars)s.")
                    % {"chars": self.special_chars}
                )
            else:
                errors.append(_("La contraseña debe incluir al menos un carácter especial (p. ej. !, @, #, $, %...)."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self) -> str:
        if self.special_chars:
            return _(
                "Debe tener al menos %(min)d caracteres, e incluir una mayúscula, un número y un carácter especial de %(chars)s."
            ) % {"min": self.min_length, "chars": self.special_chars}
        return _(
            "Debe tener al menos %(min)d caracteres, e incluir una mayúscula, un número y un carácter especial."
        ) % {"min": self.min_length}
