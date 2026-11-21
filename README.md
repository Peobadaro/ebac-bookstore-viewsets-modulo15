# Bookstore

Projeto Bookstore do curso **Profissão: Desenvolvedor Full Stack Python** da EBAC (Django + Poetry).

Autor: **Pedro Badaró Ferreira** ([@Peobadaro](https://github.com/Peobadaro))

## Como rodar

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

## Rodar os testes

```bash
poetry run python manage.py test
```

## Estrutura

| App | Modelos | Serializers | Testes |
|---|---|---|---|
| `product` | `Category`, `Product` | `CategorySerializer`, `ProductSerializer` | `product/tests/` |
| `order` | `Order` | `OrderSerializer` | `order/tests/` |

- **Product → Category (N:N):** na leitura, as categorias aparecem completas dentro do produto (`category`). Na escrita, são informadas pelos ids (`categories_id`).
- **Order → Product (N:N) e Order → User:** na leitura, os produtos aparecem completos (com as categorias) e o pedido mostra o `total`. Na escrita, os produtos são informados pelos ids (`products_id`).

## API (ViewSets)

Os ViewSets usam `ModelViewSet`, então cada rota tem listar, criar, detalhar, atualizar e apagar.

| Rota | ViewSet |
|---|---|
| `/bookstore/v1/category/` e `/bookstore/v1/category/<id>/` | `CategoryViewSet` |
| `/bookstore/v1/product/` e `/bookstore/v1/product/<id>/` | `ProductViewSet` |
| `/bookstore/v1/order/` e `/bookstore/v1/order/<id>/` | `OrderViewSet` |

As rotas ficam em `product/urls.py` e `order/urls.py` e são incluídas em `bookstore/urls.py`. Para conferir todas:

```bash
poetry run python manage.py show_urls
```
