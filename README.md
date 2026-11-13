# Estoque de Camisetas

Aplicação web em Django (padrão MTV) para controle de estoque de uma loja de camisetas.
Projeto acadêmico da disciplina de Desenvolvimento Web com Python e Django.

- Autoria: individual
- Repositório: https://github.com/maryanemarquez/estoque-camisetas
- Status: em desenvolvimento (Etapa 1: fundação)

## Tecnologias

- Python 3.12+
- Django
- SQLite

## Estrutura

- `loja/`: configurações do projeto Django
- `estoque/`: app com models, views, forms e templates

## Models

| Model | Descrição |
|---|---|
| Categoria | Agrupa as camisetas |
| Item (Camiseta) | Produto com código único, preço e estoque mínimo |
| Movimentacao | Entradas e saídas de estoque de um item |

## Como rodar (Windows)

```
git clone https://github.com/maryanemarquez/estoque-camisetas.git
cd estoque-camisetas
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/admin/`.
