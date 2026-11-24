subir:
	docker compose up --build -d

logs:
	docker compose logs -f ingestao

testar:
	docker compose run --rm --no-deps ingestao python -m pytest -v

inspecionar:
	docker compose run --rm --no-deps ingestao python -c "import io, os, boto3, pandas as pd; from botocore.config import Config; s3=boto3.client('s3', endpoint_url=os.getenv('ENDPOINT_S3','http://seaweedfs:8333'), aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID','acmetech'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY','acmetech123'), config=Config(s3={'addressing_style':'path'})); bucket=os.getenv('BUCKET_S3','acmetech-lake'); objs=s3.list_objects_v2(Bucket=bucket, Prefix='bronze/').get('Contents', []); print('Objetos na Bronze:', len(objs)); [print(' -', o['Key'], o['Size'], 'bytes') for o in objs]; obj=s3.get_object(Bucket=bucket, Key=objs[-1]['Key']) if objs else None; print('\nAmostra do último lote:\n', pd.read_parquet(io.BytesIO(obj['Body'].read())).head(10).to_string(index=False)) if obj else None"

derrubar:
	docker compose down -v