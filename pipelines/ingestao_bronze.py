import argparse
import io
import os
import random
import time
import uuid
from datetime import datetime, timezone

import boto3
import pandas as pd
from botocore.config import Config
from botocore.exceptions import ClientError
from pymongo import MongoClient

URI_MONGO = os.getenv("URI_MONGO", "mongodb://acmetech:acmetech123@localhost:27017/?authSource=admin")
BANCO_MONGO = os.getenv("BANCO_MONGO", "acmetech")
ENDPOINT_S3 = os.getenv("ENDPOINT_S3", "http://localhost:8333")
BUCKET_S3 = os.getenv("BUCKET_S3", "acmetech-lake")


def criar_cliente_s3():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_S3,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "acmetech"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "acmetech123"),
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )


def garantir_bucket(s3) -> None:
    try:
        s3.head_bucket(Bucket=BUCKET_S3)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET_S3)


def gerar_leituras(maquinas: list[dict], amostras_por_maquina: int = 10) -> list[dict]:
    registros = []
    for maquina in maquinas:
        for _ in range(amostras_por_maquina):
            agora = datetime.now(timezone.utc)
            # Simula leituras normais com ~5% de chance de anomalia bruta (filtrada depois na Silver)
            anomalia = random.random() < 0.05
            registros.append(
                {
                    "evento_id": str(uuid.uuid4()),
                    "maquina_id": maquina["maquina_id"],
                    "timestamp_evento": agora.isoformat(),
                    "temp_c": round(random.uniform(65.0, 95.0) * (1.6 if anomalia else 1.0), 2),
                    "vibracao_mms": round(random.uniform(1.5, 5.5) * (2.2 if anomalia else 1.0), 2),
                    "pressao_bar": round(random.uniform(4.5, 8.5), 2),
                    "consumo_kw": round(random.uniform(25.0, 65.0), 2),
                    "origem": "simulador-iot-acmetech",
                }
            )
    return registros


def gravar_parquet_bronze(s3, registros: list[dict], lote_id: str) -> str:
    agora = datetime.now(timezone.utc)
    ingerido_em = agora.isoformat()
    for reg in registros:
        reg["lote_id"] = lote_id
        reg["ingerido_em"] = ingerido_em

    df = pd.DataFrame(registros)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    caminho = (
        f"bronze/sensores/"
        f"ano={agora.strftime('%Y')}/mes={agora.strftime('%m')}/dia={agora.strftime('%d')}/"
        f"leituras_{agora.strftime('%H%M%S')}_{lote_id[:8]}.parquet"
    )
    s3.put_object(Bucket=BUCKET_S3, Key=caminho, Body=buffer.getvalue())
    return caminho


def executar(lotes: int, intervalo_seg: int, amostras_por_maquina: int) -> None:
    banco = MongoClient(URI_MONGO)[BANCO_MONGO]
    maquinas = list(banco.maquinas.find({"status": "ativo"}, {"_id": 0, "maquina_id": 1}))
    if not maquinas:
        raise RuntimeError("Nenhuma máquina ativa encontrada no MongoDB. Rode popular_catalogo.py antes.")

    s3 = criar_cliente_s3()
    garantir_bucket(s3)

    for i in range(lotes):
        lote_id = str(uuid.uuid4())
        registros = gerar_leituras(maquinas, amostras_por_maquina=amostras_por_maquina)
        caminho = gravar_parquet_bronze(s3, registros, lote_id=lote_id)
        print(f"[bronze] Lote {i + 1}/{lotes} gravado ({len(registros)} eventos) -> s3://{BUCKET_S3}/{caminho}")
        if i < lotes - 1:
            time.sleep(intervalo_seg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lotes", type=int, default=3)
    parser.add_argument("--intervalo", type=int, default=2)
    parser.add_argument("--amostras", type=int, default=10)
    args = parser.parse_args()
    executar(lotes=args.lotes, intervalo_seg=args.intervalo, amostras_por_maquina=args.amostras)