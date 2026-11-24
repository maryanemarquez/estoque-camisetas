# ==============================================================
# estoque/urls.py
# Papel: rotas do app estoque. O projeto (loja/urls.py) inclui este
# arquivo com include('estoque.urls'). O name= é igual ao nome da view.
# ==============================================================
from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    # Item
    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/novo/', views.criar_item, name='criar_item'),
    path('itens/<int:pk>/', views.detalhar_item, name='detalhar_item'),
    path('itens/<int:pk>/editar/', views.editar_item, name='editar_item'),
    path('itens/<int:pk>/excluir/', views.excluir_item, name='excluir_item'),

    # Categoria
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nova/', views.criar_categoria, name='criar_categoria'),
    path('categorias/<int:pk>/', views.detalhar_categoria, name='detalhar_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.excluir_categoria, name='excluir_categoria'),

    # Movimentação (sem editar/excluir: histórico imutável)
    path('movimentacoes/', views.lista_movimentacoes, name='lista_movimentacoes'),
    path('movimentacoes/nova/', views.criar_movimentacao, name='criar_movimentacao'),
    path('movimentacoes/<int:pk>/', views.detalhar_movimentacao, name='detalhar_movimentacao'),

    # Implementação "Tecido"  - Realização da Prova. #
    path('tecidos/', views.lista_tecidos, name='lista_tecidos'),
    path('tecidos/<int:pk>/excluir/', views.excluir_tecido, name='excluir_tecido'),
    path('tecidos/nova/', views.criar_tecido, name='criar_tecido'),
    path('tecidos/<int:pk>/', views.detalhar_tecido, name='detalhar_tecido'),
    path('tecidos/<int:pk>/editar/', views.editar_tecido, name='editar_tecido'),

]
