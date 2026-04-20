# HR Mock WMS API

Static JSON fixtures for a HackerRank REST API coding question.

## Endpoints

- `GET /api/purchase_orders/page/<n>.json` — paginated purchase orders (n = 1..4)
- `GET /api/inventory/<itemId>.json` — on-hand for a single item

## Regenerating

Edit `gen.py` and run `python3 gen.py`.
