# Estoque de Camisetas

Aplicação web em Django (padrão MTV) para controle de estoque de uma loja de camisetas streetwear.
Projeto acadêmico da disciplina de Desenvolvimento Web com Python e Django.

- Autoria: individual
- Repositório: https://github.com/maryanemarquez/estoque-camisetas
- Versão: 1.0

## Tecnologias

- Python 3.12+
- Django 6.1
- SQLite
- HTML e CSS próprio (sem Bootstrap)

## Funcionalidades

- CRUD de camisetas (listar, detalhar, criar, editar, excluir), com busca por nome/código e filtros por categoria e "só em alerta"
- CRUD de categorias
- Movimentações de estoque (entrada e saída): criar, listar e detalhar; histórico imutável
- Saída maior que o saldo é bloqueada com mensagem de erro
- Camiseta inativa não recebe movimentação
- Saldo calculado a partir das movimentações; alerta quando saldo ≤ estoque mínimo
- Página inicial com totais, camisetas em alerta e últimas movimentações
- Painel Admin com colunas e busca personalizadas

## Como rodar (Windows)

```
git clone https://github.com/maryanemarquez/estoque-camisetas.git
cd estoque-camisetas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata dados_exemplo
python manage.py runserver
```

- Sistema: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

`loaddata dados_exemplo` carrega 5 categorias, 30 camisetas e 137 movimentações de exemplo.
Use em banco novo; para recomeçar, rode `python manage.py flush` e depois `createsuperuser` e `loaddata` de novo.

## Como testar

```
python manage.py test
```

Executa 8 testes automatizados (saldo, estoque baixo, validação da movimentação e views).

## Estrutura

```
estoque-camisetas/
├── manage.py
├── requirements.txt
├── loja/                  # configurações do projeto
├── templates/base.html    # layout base
└── estoque/               # app
    ├── models.py  forms.py  views.py  urls.py  admin.py  tests.py
    ├── fixtures/dados_exemplo.json
    ├── migrations/
    ├── static/estoque/estilo.css
    └── templates/estoque/
```

## Modelagem

| Model | Campos principais | Relação |
|---|---|---|
| Categoria | nome | — |
| Item (Camiseta) | nome, código (único), tamanho, cor, preço, estoque mínimo, ativo | FK → Categoria |
| Movimentacao | tipo (E/S), quantidade, data (automática), observação | FK → Item |

Todas as FKs usam `on_delete=CASCADE`.

## Rotas

| URL | Tela |
|---|---|
| `/` | Início (dashboard) |
| `/itens/` · `/itens/novo/` · `/itens/<id>/` · `/itens/<id>/editar/` · `/itens/<id>/excluir/` | Camisetas |
| `/categorias/` · `/categorias/nova/` · `/categorias/<id>/` · `/categorias/<id>/editar/` · `/categorias/<id>/excluir/` | Categorias |
| `/movimentacoes/` · `/movimentacoes/nova/` · `/movimentacoes/<id>/` | Movimentações |
| `/admin/` | Painel Admin |

## Requisitos do professor × entrega

| Requisito | Entrega |
|---|---|
| Aplicação MTV com Django | App `estoque` |
| Mínimo de 3 models relacionados | Categoria → Item → Movimentacao |
| Administração pelo Admin | 3 models registrados e personalizados |
| Templates: listar, detalhar, editar, criar | `*_lista`, `*_detalhe`, `*_form` |
| GitHub | Este repositório |

## Fluxo Git

Uma branch por etapa, mesclada em `main` com `--no-ff`, commits em Conventional Commits e tags `etapa-1` a `etapa-5` e `v1.0`.

| Etapa | Branch |
|---|---|
| 1 Fundação | `etapa-1-fundacao` |
| 2 CRUD de Item | `etapa-2-crud-item` |
| 3 Categoria e Movimentação | `etapa-3-categoria-movimentacao` |
| 4 Regras de estoque | `etapa-4-regras-estoque` |
| 5 Acabamento | `etapa-5-acabamento` |
