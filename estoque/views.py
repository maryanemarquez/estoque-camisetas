# ==============================================================
# estoque/views.py
# Papel: lógica das telas (views em função). Etapa 2: CRUD de Item.
# Conceito novo: Q (importado de django.db.models) permite combinar
# condições com "ou" no filter(). Aqui, a busca acha o texto no
# nome OU no código da camiseta.
# ==============================================================
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm
from .models import Item


def inicio(request):
    """Página inicial: por enquanto redireciona para a lista (dashboard na Etapa 4)."""
    return redirect('lista_itens')


def lista_itens(request):
    """Lista as camisetas, com busca opcional por nome ou código."""
    itens = Item.objects.all().order_by('nome')
    busca = request.GET.get('q')
    if busca:
        # icontains ignora maiúsculas/minúsculas; Q liga as duas condições com "ou"
        itens = itens.filter(Q(nome__icontains=busca) | Q(codigo__icontains=busca))
    contexto = {'itens': itens, 'busca': busca}
    return render(request, 'estoque/item_lista.html', contexto)


def detalhar_item(request, pk):
    """Mostra os dados, o saldo e as movimentações de uma camiseta."""
    item = get_object_or_404(Item, pk=pk)
    contexto = {'item': item}
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
