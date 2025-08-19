# utils/permissions.py
# Código en inglés; comentarios en español
from collections import defaultdict
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst

EXCLUDED_APP_LABELS = {"admin", "contenttypes", "sessions"}  # ignorar contrib
ACTION_ORDER = {"view": 1, "add": 2, "change": 3, "delete": 4}
ACTION_ES = {"view": "Ver", "add": "Crear", "change": "Editar", "delete": "Eliminar"}

def allowed_app_labels():
    """Devuelve app labels de proyecto (excluye django.contrib y excluidos)."""
    labels = set()
    for app in settings.INSTALLED_APPS:
        short = app.split(".")[-1]
        if app.startswith("django.contrib") or short in EXCLUDED_APP_LABELS:
            continue
        labels.add(short)
    # asegúrate de incluir tus apps principales
    labels.update({"users", "employees"})
    return labels

def filtered_permissions_qs():
    """Solo permisos de apps permitidas; excluye logentry."""
    apps_ok = allowed_app_labels()
    cts = ContentType.objects.filter(app_label__in=apps_ok).exclude(model="logentry")
    return (Permission.objects
            .filter(content_type__in=cts)
            .select_related("content_type")
            .order_by("content_type__app_label", "content_type__model", "codename"))

def group_permissions_by_model(perms):
    """Agrupa permisos por modelo para UI de checkboxes."""
    g = defaultdict(list)
    for p in perms:
        ct = p.content_type
        model_cls = ct.model_class()
        model_label = capfirst(str(model_cls._meta.verbose_name)) if model_cls else capfirst(ct.model.replace("", " "))
        action = p.codename.split("_", 1)[0]
        label = ACTION_ES.get(action, capfirst(p.name))
        g[(ct.app_label, model_label)].append({
            "id": p.id, "label": label, "codename": p.codename,
            "action_order": ACTION_ORDER.get(action, 99),
        })
    result = []
    for (app_label, model_label), items in sorted(g.items(), key=lambda x: (x[0][0], x[0][1].lower())):
        items.sort(key=lambda it: (it["action_order"], it["label"]))
        result.append({"app_label": app_label, "model_label": model_label, "items": items})
    return result
