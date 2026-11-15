# ==============================================================
# estoque/forms.py
# Papel: formulários do app. Cada ModelForm gera os campos a partir
# do model. ItemForm e CategoriaForm servem para criar e editar.
# MovimentacaoForm só cria (histórico imutável) e valida o saldo
# no clean(): saída maior que o saldo é bloqueada.
# ==============================================================
from django import forms

from .models import Categoria, Item, Movimentacao


class ItemForm(forms.ModelForm):
    """Formulário de camiseta (usado em criar e editar)."""

    class Meta:
        model = Item
        fields = ['nome', 'codigo', 'categoria', 'tamanho', 'cor',
                  'preco', 'estoque_minimo', 'ativo']
        labels = {
            'nome': 'Nome',
            'codigo': 'Código',
            'categoria': 'Categoria',
            'tamanho': 'Tamanho',
            'cor': 'Cor',
            'preco': 'Preço (R$)',
            'estoque_minimo': 'Estoque mínimo',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Camiseta Oversized'}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Ex.: MAS-001'}),
        }


class CategoriaForm(forms.ModelForm):
    """Formulário de categoria (usado em criar e editar)."""

    class Meta:
        model = Categoria
        fields = ['nome']
        labels = {
            'nome': 'Nome da categoria',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Camisetas básicas'}),
        }


class MovimentacaoForm(forms.ModelForm):
    """Formulário de movimentação (só criar). A data é automática."""

    class Meta:
        model = Movimentacao
        fields = ['item', 'tipo', 'quantidade', 'observacao']
        labels = {
            'item': 'Camiseta',
            'tipo': 'Tipo',
            'quantidade': 'Quantidade',
            'observacao': 'Observação',
        }
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # D14: item inativo não recebe movimentação, então o select lista só ativos
        self.fields['item'].queryset = Item.objects.filter(ativo=True).order_by('nome')

    def clean(self):
        """Valida a quantidade e impede saída maior que o saldo (D15)."""
        dados = super().clean()
        item = dados.get('item')
        tipo = dados.get('tipo')
        quantidade = dados.get('quantidade')
        # Se algum campo já falhou na validação própria, não há o que conferir aqui
        if item is None or tipo is None or quantidade is None:
            return dados
        if quantidade < 1:
            self.add_error('quantidade', 'A quantidade deve ser maior que zero.')
        elif tipo == 'S' and quantidade > item.saldo:
            self.add_error('quantidade', f'Saldo insuficiente: disponível {item.saldo}.')
        return dados
