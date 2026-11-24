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
- Código da camiseta gerado automaticamente pela categoria (`PREFIXO-NNN`, ex.: `OVR-007`); se a categoria mudar, o código é gerado de novo
- Ordenação da lista de camisetas por nome, código e preço (crescente e decrescente)
- CRUD de categorias, cada uma com um prefixo de 3 letras (bloqueado depois que a categoria tem camisetas)
- Movimentações de estoque (entrada e saída): criar, listar e detalhar; histórico imutável
- Saída maior que o saldo é bloqueada com mensagem de erro
- Camiseta inativa não recebe movimentação
- Na movimentação, a camiseta é escolhida por um campo de busca (nome ou código, igual à tela de camisetas); se a busca achar mais de uma, o sistema pede o código ou mais letras do nome
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

`loaddata dados_exemplo` carrega 5 categorias (com prefixo), 30 camisetas e 137 movimentações de exemplo.
Use em banco novo; para recomeçar, apague o arquivo `db.sqlite3` e repita `migrate`, `createsuperuser` e `loaddata`.

## Como testar

```
python manage.py test
```

Executa 24 testes automatizados (saldo, estoque baixo, validação e busca da movimentação, código automático, prefixo da categoria, ordenação e views).

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
| Categoria | nome, prefixo (3 letras, único) | — |
| Item (Camiseta) | nome, código (único, gerado pela categoria), tamanho, cor, preço, estoque mínimo, ativo | FK → Categoria |
| Movimentacao | tipo (E/S), quantidade, data (automática), observação | FK → Item |

Todas as FKs usam `on_delete=CASCADE`.

### Código automático

- Formato `PREFIXO-NNN`: o prefixo vem da categoria e o número é o maior já usado nela mais 1 (ex.: `OVR-006` leva a `OVR-007`).
- O código não é digitado no formulário; na edição aparece só para leitura.
- Trocar a categoria de uma camiseta gera um novo código com o prefixo da nova categoria.
- Limitação: a sequência tem 3 dígitos; acima de 999 por categoria a ordenação por código deixa de seguir a ordem numérica.

### Ordenação

A lista de camisetas aceita `?ordem=` com `nome`, `codigo`, `-codigo`, `preco` ou `-preco` (o `-` inverte). Valores inválidos voltam para `nome`.

## Rotas

| URL | Tela |
|---|---|
| `/` | Início (dashboard) |
| `/itens/` (aceita `?q=`, `?categoria=`, `?alerta=1` e `?ordem=`) · `/itens/novo/` · `/itens/<id>/` · `/itens/<id>/editar/` · `/itens/<id>/excluir/` | Camisetas |
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
