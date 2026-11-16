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
        # O código não está aqui: é gerado pela categoria no save() (D27)
        fields = ['nome', 'categoria', 'tamanho', 'cor',
                  'preco', 'estoque_minimo', 'ativo']
        labels = {
            'nome': 'Nome',
            'categoria': 'Categoria',
            'tamanho': 'Tamanho',
            'cor': 'Cor',
            'preco': 'Preço (R$)',
            'estoque_minimo': 'Estoque mínimo',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Camiseta Oversized'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Texto da opção vazia do select (o padrão do Django é "---------")
        self.fields['categoria'].empty_label = 'Selecione a categoria'


class CategoriaForm(forms.ModelForm):
    """Formulário de categoria (usado em criar e editar)."""

    class Meta:
        model = Categoria
        fields = ['nome', 'prefixo']
        labels = {
            'nome': 'Nome da categoria',
            'prefixo': 'Prefixo do código (3 letras)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Camisetas básicas'}),
            'prefixo': forms.TextInput(attrs={'placeholder': 'Ex.: BSC', 'maxlength': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # D29: com camisetas já cadastradas, o prefixo fica bloqueado; trocá-lo
        # deixaria os códigos existentes fora do padrão da categoria
        if self.instance.pk and self.instance.itens.exists():
            self.fields['prefixo'].disabled = True

    def clean_prefixo(self):
        """Exige 3 letras (A-Z) e grava em maiúsculas."""
        prefixo = self.cleaned_data['prefixo'].strip().upper()
        if len(prefixo) != 3 or not prefixo.isascii() or not prefixo.isalpha():
            raise forms.ValidationError('Informe exatamente 3 letras, sem números ou acentos.')
        return prefixo


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
        # Opções vazias em português (o padrão do Django é "---------")
        self.fields['item'].empty_label = 'Selecione a camiseta'
        self.fields['tipo'].choices = [('', 'Selecione o tipo')] + Movimentacao.TIPOS

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
