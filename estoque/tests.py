# =============================================================================
# estoque/tests.py
# Testes automatizados (D24). Rodar com: python manage.py test
# Cada teste cria seus próprios dados em um banco temporário; o db.sqlite3
# de desenvolvimento não é afetado.
# =============================================================================
from django.test import TestCase
from django.urls import reverse

from .forms import CategoriaForm, MovimentacaoForm
from .models import Categoria, Item, Movimentacao


class BaseTestCase(TestCase):
    """Cria uma categoria e funções auxiliares usadas pelos testes."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Oversized', prefixo='OVR')

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

    def dados(self, item, tipo='S', quantidade=1):
        # A camiseta é enviada como texto de busca (código), não como id
        return {'busca_item': item.codigo, 'tipo': tipo, 'quantidade': quantidade}

    def test_form_rejeita_saida_maior_que_o_saldo(self):
        item = self.criar_item()
        self.mover(item, 'E', 4)
        form = MovimentacaoForm(self.dados(item, 'S', 5))
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)

    def test_form_aceita_saida_dentro_do_saldo(self):
        item = self.criar_item()
        self.mover(item, 'E', 4)
        form = MovimentacaoForm(self.dados(item, 'S', 4))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().item, item)

    def test_busca_por_nome_acha_a_camiseta(self):
        item = Item.objects.create(nome='Camiseta Lunar', categoria=self.categoria, preco='99.90')
        form = MovimentacaoForm({'busca_item': 'lunar', 'tipo': 'E', 'quantidade': 2})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().item, item)

    def test_busca_com_varios_resultados_pede_mais_detalhe(self):
        self.criar_item(codigo='OVR-001')
        self.criar_item(codigo='OVR-002')
        form = MovimentacaoForm({'busca_item': 'Oversized', 'tipo': 'E', 'quantidade': 1})
        self.assertFalse(form.is_valid())
        self.assertIn('Mais de uma', form.errors['busca_item'][0])
        # O código completo resolve a ambiguidade
        form = MovimentacaoForm({'busca_item': 'ovr-002', 'tipo': 'E', 'quantidade': 1})
        self.assertTrue(form.is_valid())

    def test_busca_nao_acha_item_inativo_nem_inexistente(self):
        inativo = self.criar_item(codigo='OVR-001', ativo=False)
        for texto in [inativo.codigo, 'xyz']:
            form = MovimentacaoForm({'busca_item': texto, 'tipo': 'E', 'quantidade': 1})
            self.assertFalse(form.is_valid(), texto)
            self.assertIn('Nenhuma camiseta ativa', form.errors['busca_item'][0])


class ViewTests(BaseTestCase):

    def test_lista_responde_200_e_busca_por_codigo(self):
        self.criar_item(codigo='OVR-001')
        # D28: o código acompanha a categoria, então o BXY-001 precisa de categoria BXY
        boxy = Categoria.objects.create(nome='Boxy', prefixo='BXY')
        outro = Item.objects.create(
            nome='Boxy Teste', codigo='BXY-001', categoria=boxy, preco='99.90',
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
            'nome': 'Graphic Teste', 'categoria': self.categoria.pk,
            'tamanho': 'M', 'cor': 'Preto', 'preco': '159.90',
            'estoque_minimo': 3, 'ativo': 'on',
        }
        resposta = self.client.post(reverse('criar_item'), dados)
        self.assertRedirects(resposta, reverse('lista_itens'))
        # O código não é digitado: nasce do prefixo da categoria (OVR)
        self.assertTrue(Item.objects.filter(codigo='OVR-001').exists())


class MovimentacaoViewTests(BaseTestCase):

    def test_atalho_item_preenche_a_busca_com_o_codigo(self):
        item = self.criar_item()
        resposta = self.client.get(reverse('criar_movimentacao'), {'item': item.pk})
        self.assertEqual(resposta.context['form'].initial['busca_item'], 'OVR-001')

    def test_atalho_item_invalido_nao_quebra(self):
        resposta = self.client.get(reverse('criar_movimentacao'), {'item': 'abc'})
        self.assertEqual(resposta.status_code, 200)

    def test_registrar_pela_tela_redireciona_para_a_camiseta(self):
        item = self.criar_item()
        dados = {'busca_item': 'OVR-001', 'tipo': 'E', 'quantidade': 6}
        resposta = self.client.post(reverse('criar_movimentacao'), dados)
        self.assertRedirects(resposta, reverse('detalhar_item', args=[item.pk]))
        self.assertEqual(item.saldo, 6)


class CodigoAutomaticoTests(BaseTestCase):
    """Código PREFIXO-NNN gerado pela categoria (D26 a D29)."""

    def novo(self, categoria=None):
        return Item.objects.create(
            nome='Teste', categoria=categoria or self.categoria, preco='99.90',
        )

    def test_primeiro_codigo_da_categoria(self):
        self.assertEqual(self.novo().codigo, 'OVR-001')

    def test_gera_o_maior_mais_um_mesmo_com_lacuna(self):
        self.criar_item(codigo='OVR-001')
        self.criar_item(codigo='OVR-003')
        self.assertEqual(self.novo().codigo, 'OVR-004')

    def test_categorias_tem_sequencias_independentes(self):
        boxy = Categoria.objects.create(nome='Boxy', prefixo='BXY')
        self.assertEqual(self.novo().codigo, 'OVR-001')
        self.assertEqual(self.novo(boxy).codigo, 'BXY-001')
        self.assertEqual(self.novo().codigo, 'OVR-002')

    def test_trocar_a_categoria_gera_novo_codigo(self):
        boxy = Categoria.objects.create(nome='Boxy', prefixo='BXY')
        item = self.novo()
        item.categoria = boxy
        item.save()
        self.assertEqual(item.codigo, 'BXY-001')

    def test_editar_sem_trocar_a_categoria_mantem_o_codigo(self):
        item = self.novo()
        item.nome = 'Outro nome'
        item.save()
        self.assertEqual(Item.objects.get(pk=item.pk).codigo, 'OVR-001')


class CategoriaFormTests(BaseTestCase):

    def test_prefixo_vira_maiusculo(self):
        form = CategoriaForm({'nome': 'Boxy', 'prefixo': ' bxy '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['prefixo'], 'BXY')

    def test_prefixo_invalido_ou_repetido_e_rejeitado(self):
        for prefixo in ['AB', 'ABCD', 'A1C', 'ÁBC', 'OVR']:
            form = CategoriaForm({'nome': 'Teste', 'prefixo': prefixo})
            self.assertFalse(form.is_valid(), prefixo)
            self.assertIn('prefixo', form.errors, prefixo)

    def test_prefixo_bloqueado_quando_a_categoria_tem_camisetas(self):
        self.criar_item()
        form = CategoriaForm(instance=self.categoria)
        self.assertTrue(form.fields['prefixo'].disabled)
        # Mesmo que alguém envie outro valor, o prefixo original é mantido
        form = CategoriaForm({'nome': 'Oversized', 'prefixo': 'XYZ'}, instance=self.categoria)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().prefixo, 'OVR')


class OrdenacaoTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Preços escolhidos para que a ordem por preço difira da ordem por código
        for preco in ['150.00', '90.00', '120.00']:
            Item.objects.create(nome='Teste', categoria=self.categoria, preco=preco)

    def codigos(self, ordem):
        resposta = self.client.get(reverse('lista_itens'), {'ordem': ordem})
        return [item.codigo for item in resposta.context['itens']]

    def test_codigo_decrescente(self):
        self.assertEqual(self.codigos('-codigo'), ['OVR-003', 'OVR-002', 'OVR-001'])

    def test_preco_crescente(self):
        self.assertEqual(self.codigos('preco'), ['OVR-002', 'OVR-003', 'OVR-001'])

    def test_ordem_invalida_volta_para_nome(self):
        resposta = self.client.get(reverse('lista_itens'), {'ordem': 'inventada'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['ordem'], 'nome')

