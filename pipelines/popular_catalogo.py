import os
from datetime import datetime, timezone
from pymongo import ASCENDING, MongoClient

URI_MONGO = os.getenv("URI_MONGO", "mongodb://acmetech:acmetech123@localhost:27017/?authSource=admin")
BANCO_MONGO = os.getenv("BANCO_MONGO", "acmetech")

MAQUINAS = [
    {
        "maquina_id": "M-01",
        "nome": "Extrusora Linha A",
        "linha_id": "L-01",
        "capacidade_unid_hora": 120,
        "tarifa_energia_brl_kwh": 0.85,
        "status": "ativo",
        "sensores": [
            {"sensor_id": "S-01-TEMP", "tipo": "temperatura", "unidade": "C", "min_valido": 20.0, "max_valido": 140.0},
            {"sensor_id": "S-01-VIB", "tipo": "vibracao", "unidade": "mm/s", "min_valido": 0.0, "max_valido": 12.0},
            {"sensor_id": "S-01-PRES", "tipo": "pressao", "unidade": "bar", "min_valido": 1.0, "max_valido": 15.0},
            {"sensor_id": "S-01-POT", "tipo": "potencia", "unidade": "kW", "min_valido": 0.0, "max_valido": 90.0},
        ],
    },
    {
        "maquina_id": "M-02",
        "nome": "Misturador Industrial B",
        "linha_id": "L-01",
        "capacidade_unid_hora": 200,
        "tarifa_energia_brl_kwh": 0.85,
        "status": "ativo",
        "sensores": [
            {"sensor_id": "S-02-TEMP", "tipo": "temperatura", "unidade": "C", "min_valido": 15.0, "max_valido": 110.0},
            {"sensor_id": "S-02-VIB", "tipo": "vibracao", "unidade": "mm/s", "min_valido": 0.0, "max_valido": 10.0},
            {"sensor_id": "S-02-PRES", "tipo": "pressao", "unidade": "bar", "min_valido": 1.0, "max_valido": 12.0},
            {"sensor_id": "S-02-POT", "tipo": "potencia", "unidade": "kW", "min_valido": 0.0, "max_valido": 75.0},
        ],
    },
    {
        "maquina_id": "M-03",
        "nome": "Envasadora Automática C",
        "linha_id": "L-02",
        "capacidade_unid_hora": 350,
        "tarifa_energia_brl_kwh": 0.82,
        "status": "ativo",
        "sensores": [
            {"sensor_id": "S-03-TEMP", "tipo": "temperatura", "unidade": "C", "min_valido": 10.0, "max_valido": 85.0},
            {"sensor_id": "S-03-VIB", "tipo": "vibracao", "unidade": "mm/s", "min_valido": 0.0, "max_valido": 8.0},
            {"sensor_id": "S-03-PRES", "tipo": "pressao", "unidade": "bar", "min_valido": 2.0, "max_valido": 10.0},
            {"sensor_id": "S-03-POT", "tipo": "potencia", "unidade": "kW", "min_valido": 0.0, "max_valido": 50.0},
        ],
    },
]

CUSTOS_SKU = [
    {
        "sku": "SKU-100",
        "descricao": "Resina Base Tipo A",
        "maquina_id": "M-01",
        "custo_material_brl": 12.40,
        "mao_obra_direta_brl": 2.10,
        "margem_minima_pct": 0.18,
    },
    {
        "sku": "SKU-200",
        "descricao": "Composto Polimérico B",
        "maquina_id": "M-02",
        "custo_material_brl": 18.90,
        "mao_obra_direta_brl": 1.75,
        "margem_minima_pct": 0.20,
    },
    {
        "sku": "SKU-300",
        "descricao": "Solvente Técnico C",
        "maquina_id": "M-03",
        "custo_material_brl": 7.80,
        "mao_obra_direta_brl": 0.95,
        "margem_minima_pct": 0.15,
    },
]


def popular() -> None:
    cliente = MongoClient(URI_MONGO)
    banco = cliente[BANCO_MONGO]

    banco.maquinas.create_index([("maquina_id", ASCENDING)], unique=True)
    banco.maquinas.create_index([("linha_id", ASCENDING), ("status", ASCENDING)])
    banco.custos_sku.create_index([("sku", ASCENDING)], unique=True)

    agora = datetime.now(timezone.utc)
    for maquina in MAQUINAS:
        banco.maquinas.update_one(
            {"maquina_id": maquina["maquina_id"]},
            {"$set": {**maquina, "atualizado_em": agora}},
            upsert=True,
        )

    for sku in CUSTOS_SKU:
        banco.custos_sku.update_one(
            {"sku": sku["sku"]},
            {"$set": {**sku, "atualizado_em": agora}},
            upsert=True,
        )

    print(
        f"[catalogo] Sincronizado: {banco.maquinas.count_documents({})} máquinas, "
        f"{banco.custos_sku.count_documents({})} SKUs."
    )


if __name__ == "__main__":
    popular()