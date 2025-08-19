# utils/db_functions.py
from django.db.models import Func, TextField

class Unaccent(Func):
    """
    Funcion UNACCENT de PostgreSQL para quitar acentos.
    Uso: annotate(field_unaccent=Unaccent('campo'))
    """
    function = 'unaccent'
    output_field = TextField()
