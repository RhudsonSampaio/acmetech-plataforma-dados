# Runbook Operacional — Fundação AcmeTech (Entrega 1)

## 1. Pré-requisitos
* Docker e Docker Compose v2 instalados (com acesso ao daemon sem `sudo` via grupo `docker`).
* `make` instalado.
* Portas livres na máquina local:
  * `27017` — MongoDB
  * `8081` — Mongo Express (interface web do MongoDB)
  * `8333` — API S3 do SeaweedFS
  * `8888` — SeaweedFS Filer UI (navegação de buckets e arquivos)
  * `9333` — SeaweedFS Master UI (status e volumes do cluster)

## 2. Subida e Execução do Pipeline
1. Configurar variáveis de ambiente (sem sobrescrever caso `.env` já exista):
   ```bash
   cp -n .env.example .env
   ```
2. Construir a imagem de pipelines e subir MongoDB, SeaweedFS, Mongo Express e a ingestão inicial:
   ```bash
   make subir
   ```
3. Acompanhar os logs da sincronização do catálogo e da gravação na camada Bronze:
   ```bash
   make logs
   ```
   Saída esperada:
   * `[catalogo] Sincronizado: 3 máquinas, 3 SKUs.`
   * `[bronze] Lote 1/3`, `2/3` e `3/3` gravados em `s3://acmetech-lake/bronze/sensores/ano=YYYY/mes=MM/dia=DD/`.

## 3. Verificação, Testes e Inspeção
1. Executar os testes automatizados dentro do container:
   ```bash
   make testar
   ```
   Saída esperada: `1 passed`.
2. Inspecionar os objetos Parquet gravados na Bronze e visualizar amostra tabular no terminal:
   ```bash
   make inspecionar
   ```
3. Conferir visualmente no navegador:
   * **SeaweedFS Filer UI:** http://localhost:8888 *(caminho `buckets/acmetech-lake/bronze/sensores/`)*
   * **SeaweedFS Master UI:** http://localhost:9333
   * **Mongo Express:** http://localhost:8081 *(banco `acmetech`, coleções `maquinas` e `custos_sku`)*
4. (Opcional) Consultar o MongoDB diretamente via `mongosh`:
   ```bash
   docker compose exec mongodb mongosh -u acmetech -p acmetech123 --authenticationDatabase admin acmetech
   ```

## 4. Reexecução, Carga Customizada e Reset
* **Reexecução (`make subir`):** `popular_catalogo.py` realiza `upsert` idempotente por `maquina_id` e `sku` (sem duplicar documentos), enquanto `ingestao_bronze.py` grava novos lotes em modo *append-only* na Bronze.
* **Execução manual com parâmetros personalizados:**
  ```bash
  docker compose run --rm ingestao python ingestao_bronze.py --lotes 5 --intervalo 1 --amostras 20
  ```
* **Encerrar e apagar todos os volumes locais (`dados_mongo` e `dados_seaweedfs`):**
  ```bash
  make derrubar
  ```

## 5. Solução de Problemas Comuns
* **`permission denied` em `/var/run/docker.sock`:** adicione seu usuário ao grupo `docker` (`sudo usermod -aG docker "$USER"`) e recarregue a sessão com `newgrp docker` ou abrindo um novo terminal.
* **`acmetech-seaweedfs is unhealthy`:** consulte `docker logs acmetech-seaweedfs` e verifique se as portas `8333`, `8888` e `9333` estão livres no host.
* **Erro de autenticação S3:** confirme que `CHAVE_ACESSO_S3` e `CHAVE_SECRETA_S3` no `.env` correspondem às credenciais configuradas em `infra/seaweedfs/s3.json`.
