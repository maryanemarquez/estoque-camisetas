# =============================================================================
# estoque/models.py
# Define as tabelas do sistema: Categoria, Item e Movimentacao.
# Relação em cadeia: Categoria -> Item -> Movimentacao (ForeignKey).
# =============================================================================
from django.db import models


class Categoria(models.Model):
    """Agrupa os itens (ex.: Camisetas básicas, Estampadas)."""
    nome = models.CharField(max_length=60)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class Item(models.Model):
    """Produto do estoque. Rótulo visível: Camiseta."""
    nome = models.CharField(max_length=100)
    # unique=True: não permite dois itens com o mesmo código (D7)
    codigo = models.CharField(max_length=20, unique=True)
    # CASCADE: apagar a categoria apaga seus itens (D1)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='itens'
    )
    tamanho = models.CharField(max_length=10, blank=True)
    cor = models.CharField(max_length=30, blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    estoque_minimo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Camiseta'
        verbose_name_plural = 'Camisetas'

    def __str__(self):
        return f'{self.nome} ({self.codigo})'

    @property
    def saldo(self):
        """Entradas menos saídas, calculado em Python (não é gravado no banco)."""
        total = 0
        for mov in self.movimentacoes.all():
            if mov.tipo == 'E':
                total += mov.quantidade
            else:
                total -= mov.quantidade
        return total

    @property
    def estoque_baixo(self):
        """True quando o saldo é menor ou igual ao estoque mínimo (D18)."""
        return self.saldo <= self.estoque_minimo


class Movimentacao(models.Model):
    """Registro de entrada ou saída de um item."""
    TIPOS = [('E', 'Entrada'), ('S', 'Saída')]

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='movimentacoes'
    )
    tipo = models.CharField(max_length=1, choices=TIPOS)
    quantidade = models.PositiveIntegerField()
    # auto_now_add: a data é preenchida sozinha ao criar (D16)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.quantidade} - {self.item}'
