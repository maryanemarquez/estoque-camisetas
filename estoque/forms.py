# ==============================================================
# estoque/forms.py
# Papel: formulários do app. Cada ModelForm gera os campos a partir
# do model. ItemForm e CategoriaForm servem para criar e editar.
# MovimentacaoForm só cria (histórico imutável) e valida o saldo
# no clean(): saída maior que o saldo é bloqueada. A camiseta é
# escolhida por busca (nome ou código), igual à tela de camisetas.
# ==============================================================
from django import forms
from django.db.models import Q

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

    # Em vez de um select, a camiseta é achada por texto (Etapa 7, D34).
    # Este campo não existe no model: o clean() converte o texto em Item.
    busca_item = forms.CharField(
        label='Camiseta',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nome ou código'}),
    )

    class Meta:
        model = Movimentacao
        fields = ['tipo', 'quantidade', 'observacao']
        labels = {
            'tipo': 'Tipo',
            'quantidade': 'Quantidade',
            'observacao': 'Observação',
        }
        widgets = {
            'quantidade': forms.NumberInput(attrs={'min': 1}),
        }

    # A busca vem primeiro, como o select vinha antes
    field_order = ['busca_item', 'tipo', 'quantidade', 'observacao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opção vazia em português (o padrão do Django é "---------")
        self.fields['tipo'].choices = [('', 'Selecione o tipo')] + Movimentacao.TIPOS

    def buscar_item(self, busca):
        """Acha a camiseta ativa pelo texto (nome ou código); erra se não for uma só."""
        # D14: só camisetas ativas. Mesma busca da lista de camisetas (D11)
        achados = Item.objects.filter(ativo=True).filter(
            Q(nome__icontains=busca) | Q(codigo__icontains=busca)
        ).order_by('codigo')
        # Código digitado por inteiro vale mesmo que o texto apareça em outras camisetas
        exatos = achados.filter(codigo__iexact=busca)
        if exatos.count() == 1:
            return exatos.first()
        if achados.count() == 1:
            return achados.first()
        if achados.count() == 0:
            self.add_error('busca_item', f'Nenhuma camiseta ativa encontrada para "{busca}".')
            return None
        codigos = [item.codigo for item in achados[:5]]
        resumo = ', '.join(codigos) + ('...' if achados.count() > 5 else '')
        self.add_error(
            'busca_item',
            f'Mais de uma camiseta encontrada ({resumo}). '
            'Informe o código ou mais letras do nome.',
        )
        return None

    def clean(self):
        """Acha a camiseta, valida a quantidade e impede saída maior que o saldo (D15)."""
        dados = super().clean()
        busca = dados.get('busca_item')
        tipo = dados.get('tipo')
        quantidade = dados.get('quantidade')
        # Se algum campo já falhou na validação própria, não há o que conferir aqui
        if not busca or tipo is None or quantidade is None:
            return dados
        item = self.buscar_item(busca)
        if item is None:
            return dados
        # O item não é campo do form: é ligado direto ao objeto que o save() grava
        self.instance.item = item
        if quantidade < 1:
            self.add_error('quantidade', 'A quantidade deve ser maior que zero.')
        elif tipo == 'S' and quantidade > item.saldo:
            self.add_error('quantidade', f'Saldo insuficiente: disponível {item.saldo}.')
        return dados
