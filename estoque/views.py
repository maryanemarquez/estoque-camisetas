# ==============================================================
# estoque/views.py
# Papel: lógica das telas (views em função).
# Etapa 2: CRUD de Item. Etapa 3: CRUD de Categoria e Movimentação
# (esta última sem editar/excluir: o histórico não é alterado).
# Etapa 4: dashboard na página inicial e filtros na lista de itens.
# Etapa 7: ordenação da lista de itens por código e preço e busca da
# camiseta na movimentação (o form converte o texto em Item).
# Conceito novo: Q (importado de django.db.models) permite combinar
# condições com "ou" no filter(). Aqui, a busca acha o texto no
# nome OU no código da camiseta.
# ==============================================================
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, ItemForm, MovimentacaoForm
from .models import Categoria, Item, Movimentacao

# Ordenações permitidas na lista de camisetas (o '-' inverte a ordem)
ORDENACOES = ['nome', 'codigo', '-codigo', 'preco', '-preco']


def inicio(request):
    """Página inicial: totais, camisetas em alerta e últimas movimentações."""
    # Só itens ativos entram no alerta; o saldo é calculado em Python (D17)
    itens_em_alerta = []
    for item in Item.objects.filter(ativo=True).order_by('nome'):
        if item.estoque_baixo:
            itens_em_alerta.append(item)
    contexto = {
        'total_itens': Item.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_movimentacoes': Movimentacao.objects.count(),
        'itens_em_alerta': itens_em_alerta,
        'ultimas': Movimentacao.objects.order_by('-data')[:5],
    }
    return render(request, 'estoque/inicio.html', contexto)


# ----------------------------- Item -----------------------------

def lista_itens(request):
    """Lista as camisetas, com busca por nome/código, filtros e ordenação."""
    # Só estes valores são aceitos em ?ordem=; qualquer outro volta para 'nome' (D30)
    ordem = request.GET.get('ordem')
    if ordem not in ORDENACOES:
        ordem = 'nome'
    # O código desempata itens com o mesmo nome ou preço
    itens = Item.objects.all().order_by(ordem, 'codigo')
    busca = request.GET.get('q')
    if busca:
        # icontains ignora maiúsculas/minúsculas; Q liga as duas condições com "ou"
        itens = itens.filter(Q(nome__icontains=busca) | Q(codigo__icontains=busca))
    categoria = request.GET.get('categoria')
    if categoria:
        itens = itens.filter(categoria_id=categoria)
    alerta = request.GET.get('alerta')
    if alerta:
        # Por último: estoque_baixo é propriedade (não existe no banco),
        # então o resultado passa a ser uma lista Python, não um queryset
        itens_em_alerta = []
        for item in itens:
            if item.estoque_baixo:
                itens_em_alerta.append(item)
        itens = itens_em_alerta
    contexto = {
        'itens': itens,
        'busca': busca,
        'categorias': Categoria.objects.all().order_by('nome'),
        'categoria': categoria or '',
        'alerta': alerta,
        'ordem': ordem,
    }
    return render(request, 'estoque/item_lista.html', contexto)


def detalhar_item(request, pk):
    """Mostra os dados, o saldo e as movimentações de uma camiseta."""
    item = get_object_or_404(Item, pk=pk)
    # Mais recentes primeiro
    movimentacoes = item.movimentacoes.order_by('-data')
    contexto = {'item': item, 'movimentacoes': movimentacoes}
    return render(request, 'estoque/item_detalhe.html', contexto)


def criar_item(request):
    """Cadastra uma camiseta (GET: form vazio; POST: valida e salva)."""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_itens')
    else:
        form = ItemForm()
    contexto = {'form': form}
    return render(request, 'estoque/item_form.html', contexto)


def editar_item(request, pk):
    """Edita uma camiseta (GET: form preenchido; POST: valida e salva)."""
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('detalhar_item', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    contexto = {'form': form, 'item': item}
    return render(request, 'estoque/item_form.html', contexto)


def excluir_item(request, pk):
    """Exclui uma camiseta (GET: pede confirmação; só o POST apaga)."""
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('lista_itens')
    contexto = {'item': item}
    return render(request, 'estoque/item_confirmar_exclusao.html', contexto)


# --------------------------- Categoria --------------------------

def lista_categorias(request):
    """Lista as categorias em ordem alfabética."""
    categorias = Categoria.objects.all().order_by('nome')
    contexto = {'categorias': categorias}
    return render(request, 'estoque/categoria_lista.html', contexto)


def detalhar_categoria(request, pk):
    """Mostra uma categoria e as camisetas que pertencem a ela."""
    categoria = get_object_or_404(Categoria, pk=pk)
    contexto = {'categoria': categoria}
    return render(request, 'estoque/categoria_detalhe.html', contexto)


def criar_categoria(request):
    """Cadastra uma categoria (GET: form vazio; POST: valida e salva)."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    contexto = {'form': form}
    return render(request, 'estoque/categoria_form.html', contexto)


def editar_categoria(request, pk):
    """Edita uma categoria (GET: form preenchido; POST: valida e salva)."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('detalhar_categoria', pk=categoria.pk)
    else:
        form = CategoriaForm(instance=categoria)
    contexto = {'form': form, 'categoria': categoria}
    return render(request, 'estoque/categoria_form.html', contexto)


def excluir_categoria(request, pk):
    """Exclui uma categoria (GET: confirma e avisa do CASCADE; só o POST apaga)."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')
    contexto = {'categoria': categoria}
    return render(request, 'estoque/categoria_confirmar_exclusao.html', contexto)


# ------------------------- Movimentação -------------------------

def lista_movimentacoes(request):
    """Lista o histórico de movimentações, da mais recente para a mais antiga."""
    movimentacoes = Movimentacao.objects.all().order_by('-data')
    contexto = {'movimentacoes': movimentacoes}
    return render(request, 'estoque/movimentacao_lista.html', contexto)


def detalhar_movimentacao(request, pk):
    """Mostra todos os dados de uma movimentação."""
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    contexto = {'movimentacao': movimentacao}
    return render(request, 'estoque/movimentacao_detalhe.html', contexto)


def criar_movimentacao(request):
    """Registra uma entrada ou saída (GET: form; POST: valida o saldo e salva)."""
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            movimentacao = form.save()
            # Vai para o item para mostrar o saldo já atualizado
            return redirect('detalhar_item', pk=movimentacao.item.pk)
    else:
        # ?item=<pk> (atalho do detalhe do item) já deixa o código no campo de busca
        inicial = {}
        item_pk = request.GET.get('item', '')
        if item_pk.isdigit():
            item = Item.objects.filter(pk=item_pk).first()
            if item:
                inicial['busca_item'] = item.codigo
        form = MovimentacaoForm(initial=inicial)
    contexto = {'form': form}
    return render(request, 'estoque/movimentacao_form.html', contexto)
