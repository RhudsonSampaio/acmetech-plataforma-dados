# Plataforma de Dados Industriais AcmeTech — Integração de Dados II

Protótipo de engenharia de dados para ingestão de telemetria IoT (3 máquinas, 4 sensores) e catálogo operacional, estruturado em arquitetura Lakehouse (`Bronze -> Silver -> Gold`) como base experimental para apoio à precificação B2B.

## Arquitetura da Fundação (Entrega 1)
* **MongoDB:** catálogo operacional de máquinas/sensores (padrão *embedding*) e custos diretos sintéticos por SKU.
* **SeaweedFS (API S3):** armazenamento de objetos local para o *lakehouse* (`s3://acmetech-lake`).
* **Pipeline de Ingestão (Python):** popula o catálogo de forma idempotente (`popular_catalogo.py`), simula leituras IoT com injeção controlada de anomalias e grava lotes **Parquet** particionados por data na camada **Bronze** (`ingestao_bronze.py`).

## Como Executar

1. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```

2. Suba os serviços e execute a carga inicial:
   ```bash
   make subir
   ```

3. Acompanhe os logs da ingestão:
   ```bash
   make logs
   ```

4. Execute os testes automatizados:
   ```bash
   make testar
   ```

5. Para encerrar e limpar os volumes:
   ```bash
   make derrubar
   ```

## Documentação e Decisões Arquiteturais

* [docs/adr/001-lakehouse-medalhao.md](docs/adr/001-lakehouse-medalhao.md) — Armazenamento analítico em SeaweedFS e camadas Bronze/Silver/Gold.
* [docs/adr/002-catalogo-nosql-mongodb.md](docs/adr/002-catalogo-nosql-mongodb.md) — Modelagem NoSQL do catálogo de máquinas e custos diretos.
