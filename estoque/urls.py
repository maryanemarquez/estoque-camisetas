# ==============================================================
# estoque/urls.py
# Papel: rotas do app estoque. O projeto (loja/urls.py) inclui este
# arquivo com include('estoque.urls'). O name= é igual ao nome da view.
# ==============================================================
from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/novo/', views.criar_item, name='criar_item'),
    path('itens/<int:pk>/', views.detalhar_item, name='detalhar_item'),
    path('itens/<int:pk>/editar/', views.editar_item, name='editar_item'),
    path('itens/<int:pk>/excluir/', views.excluir_item, name='excluir_item'),
]
