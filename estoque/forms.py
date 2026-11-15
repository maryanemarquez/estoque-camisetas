# ==============================================================
# estoque/forms.py
# Papel: formulários do app. O ItemForm é um ModelForm: o Django
# gera os campos a partir do model Item. O mesmo form serve para
# criar e para editar.
# ==============================================================
from django import forms

from .models import Item


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
