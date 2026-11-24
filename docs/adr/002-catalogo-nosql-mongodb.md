# ADR-002: Catálogo Operacional e Custos Diretos em MongoDB

* **Status:** Aceito
* **Data:** 2026-11-24
* **Contexto:** O simulador IoT da AcmeTech gera telemetria enxuta (apenas IDs e medições), exigindo uma base cadastral rápida para armazenar metadados das máquinas, limites operacionais dos 4 sensores por máquina e custos diretos sintéticos por SKU (material, mão de obra direta e margem mínima).

## Decisão
Adotar **MongoDB** (banco orientado a documentos, perfil **CP/EC** no teorema CAP/PACELC) com duas coleções principais:
1. **`maquinas`:** aplica o padrão *Embedding*, mantendo o array `sensores` aninhado no documento da máquina (cardinalidade fixa 1:4 e leitura conjunta).
2. **`custos_sku`:** armazena parâmetros de custo direto por produto para integração futura com o motor de precificação.

Todas as cargas usam escrita idempotente (`upsert` por chave natural `maquina_id` e `sku`) e índices únicos/compostos para evitar `COLLSCAN`.

## Alternativas Consideradas
* **Guardar metadados fixos em arquivo JSON estático:** descartado por dificultar consultas filtradas, evolução de atributos heterogêneos por sensor e integração com serviços futuros.
* **Usar banco colunar (Cassandra) para o catálogo:** inadequado para baixa volumetria cadastral com buscas por atributos variados.

## Consequências
* **Positivas:** leitura única por máquina sem *joins*, flexibilidade para adicionar novos tipos de sensores e atualização segura via `upsert`.
* **Negativas:** exige validação de esquema na aplicação para evitar inconsistência de tipos entre documentos.
