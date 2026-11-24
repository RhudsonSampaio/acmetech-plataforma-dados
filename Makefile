subir:
	docker compose up --build -d

logs:
	docker compose logs -f ingestao

testar:
	docker compose run --rm --no-deps ingestao python -m pytest -v

derrubar:
	docker compose down -v