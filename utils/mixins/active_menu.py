class ActiveMenuMixin:
    """Inyecta 'active_menu' al contexto para resaltar el ítem del menú."""
    active_menu: str | None = None

    # def get_active_menu(self):
    #     return self.active_menu

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_menu"] = self.active_menu
        return ctx