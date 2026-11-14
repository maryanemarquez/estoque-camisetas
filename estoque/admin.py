# =============================================================================
# estoque/admin.py
# Registra os models no painel Admin (sem personalização; ela vem na Etapa 5).
# =============================================================================
from django.contrib import admin

from .models import Categoria, Item, Movimentacao

admin.site.register(Categoria)
admin.site.register(Item)
admin.site.register(Movimentacao)
