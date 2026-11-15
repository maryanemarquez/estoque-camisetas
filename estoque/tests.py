# =============================================================================
# estoque/tests.py
# Testes automatizados (D24). Rodar com: python manage.py test
# Cada teste cria seus próprios dados em um banco temporário; o db.sqlite3
# de desenvolvimento não é afetado.
# =============================================================================
from django.test import TestCase
from django.urls import reverse

from .forms import MovimentacaoForm
from .models import Categoria, Item, Movimentacao


class BaseTestCase(TestCase):
    """Cria uma categoria e funções auxiliares usadas pelos testes."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Oversized')

    def criar_item(self, codigo='OVR-001', minimo=2, ativo=True):
        return Item.objects.create(
            nome='Oversized Teste', codigo=codigo, categoria=self.categoria,
            preco='139.90', estoque_minimo=minimo, ativo=ativo,
        )

    def mover(self, item, tipo, quantidade):
        return Movimentacao.objects.create(item=item, tipo=tipo, quantidade=quantidade)


class ModelTests(BaseTestCase):

    def test_saldo_soma_entradas_e_subtrai_saidas(self):
        item = self.criar_item()
        self.mover(item, 'E', 10)
        self.mover(item, 'S', 3)
        self.mover(item, 'E', 5)
        self.assertEqual(item.saldo, 12)

    def test_estoque_baixo_quando_saldo_menor_ou_igual_ao_minimo(self):
        item = self.criar_item(minimo=5)
        self.mover(item, 'E', 8)
        self.assertFalse(item.estoque_baixo)   # 8 > 5
        self.mover(item, 'S', 3)
        self.assertTrue(item.estoque_baixo)    # 5 == 5
        self.mover(item, 'S', 1)
        self.assertTrue(item.estoque_baixo)    # 4 < 5


class FormTests(BaseTestCase):

    def test_form_rejeita_saida_maior_que_o_saldo(self):
        item = self.criar_item()
        self.mover(item, 'E', 4)
        form = MovimentacaoForm({'item': item.pk, 'tipo': 'S', 'quantidade': 5})
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)

    def test_form_aceita_saida_dentro_do_saldo(self):
        item = self.criar_item()
        self.mover(item, 'E', 4)
        form = MovimentacaoForm({'item': item.pk, 'tipo': 'S', 'quantidade': 4})
        self.assertTrue(form.is_valid())

    def test_form_nao_lista_item_inativo(self):
        ativo = self.criar_item(codigo='OVR-001')
        inativo = self.criar_item(codigo='OVR-002', ativo=False)
        itens = MovimentacaoForm().fields['item'].queryset
        self.assertIn(ativo, itens)
        self.assertNotIn(inativo, itens)


class ViewTests(BaseTestCase):

    def test_lista_responde_200_e_busca_por_codigo(self):
        self.criar_item(codigo='OVR-001')
        outro = Item.objects.create(
            nome='Boxy Teste', codigo='BXY-001', categoria=self.categoria, preco='99.90',
        )
        resposta = self.client.get(reverse('lista_itens'))
        self.assertEqual(resposta.status_code, 200)
        resposta = self.client.get(reverse('lista_itens'), {'q': 'BXY'})
        self.assertEqual(list(resposta.context['itens']), [outro])

    def test_excluir_so_apaga_com_post(self):
        item = self.criar_item()
        url = reverse('excluir_item', args=[item.pk])
        self.client.get(url)
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())
        self.client.post(url)
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_criar_item_valido_redireciona_para_a_lista(self):
        dados = {
            'nome': 'Graphic Teste', 'codigo': 'GRF-001', 'categoria': self.categoria.pk,
            'tamanho': 'M', 'cor': 'Preto', 'preco': '159.90',
            'estoque_minimo': 3, 'ativo': 'on',
        }
        resposta = self.client.post(reverse('criar_item'), dados)
        self.assertRedirects(resposta, reverse('lista_itens'))
        self.assertTrue(Item.objects.filter(codigo='GRF-001').exists())
