# ADR-001: Arquitetura Lakehouse com Padrão Medalhão em SeaweedFS (S3)

* **Status:** Aceito
* **Data:** 2026-11-24
* **Contexto:** A AcmeTech precisa consolidar leituras de telemetria IoT industrial (3 máquinas, 4 sensores por máquina) com dados cadastrais e de custos diretos para sustentar análises operacionais e precificação B2B. Soluções puras de Data Warehouse elevam custos para dados brutos em lotes contínuos, enquanto Data Lakes sem organização em camadas dificultam reprocessamento e governança.

## Decisão
Adotar uma arquitetura **Lakehouse** estruturada no padrão **Medalhão (Bronze -> Silver -> Gold)** sobre Object Storage compatível com S3 (**SeaweedFS**), utilizando o bucket único `s3://acmetech-lake` organizado por prefixos de camada:

1. **Camada Bronze (`bronze/`):**
   * Armazena os lotes brutos de telemetria em formato **Parquet**, particionados por data (`bronze/sensores/ano=YYYY/mes=MM/dia=DD/`).
   * Preserva integralmente os eventos gerados (incluindo anomalias simuladas) e adiciona metadados técnicos de rastreabilidade (`lote_id`, `ingerido_em` e `origem`).
2. **Camada Silver (`silver/`):**
   * Destinada a dados limpos, validados contra os limites operacionais cadastrados no MongoDB e enriquecidos com metadados das máquinas.
3. **Camada Gold (`gold/`):**
   * Destinada a agregações analíticas e indicadores prontos para consumo por BI e pelo motor experimental de precificação B2B.

## Alternativas Consideradas
* **Gravar apenas CSV/JSON solto em sistema de arquivos local:** descartado por falta de padronização colunar, baixa eficiência analítica e ausência de interface compatível com S3.
* **Ingerir telemetria diretamente em banco relacional:** descartado por acoplar armazenamento histórico de alta frequência ao banco transacional.

## Consequências
* **Positivas:** reprocessamento histórico garantido a partir da camada Bronze imutável, uso de formato Parquet desde a ingestão e portabilidade via API S3.
* **Negativas:** exige disciplina de particionamento e etapas adicionais de transformação até a camada Gold.
