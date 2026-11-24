# =============================================================================
# estoque/admin.py
# Registra os models no painel Admin com colunas e busca personalizadas (D23).
# list_display define as colunas da listagem; search_fields, a caixa de busca.
# =============================================================================
from django.contrib import admin

from .models import Categoria, Item, Movimentacao, Tecido


admin.site.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'prefixo']
    search_fields = ['nome', 'prefixo']

admin.site.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'categoria', 'tamanho', 'cor',
                    'preco', 'estoque_minimo', 'ativo']
    search_fields = ['nome', 'codigo']
    # O código é gerado pela categoria; no Admin ele só pode ser consultado
    readonly_fields = ['codigo']


admin.site.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ['item', 'tipo', 'quantidade', 'data']
    # item__nome busca no nome do item relacionado (atravessa a ForeignKey)
    search_fields = ['item__nome', 'item__codigo']

# Implementação "Tecido"  - Realização da Prova. #
admin.site.register(Tecido)
class TecidoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'prefixo']
    search_fields = ['nome', 'prefixo']
