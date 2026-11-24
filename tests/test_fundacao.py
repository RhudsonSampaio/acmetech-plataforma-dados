from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from pipelines.ingestao_bronze import gerar_leituras
    from pipelines.popular_catalogo import MAQUINAS
except ModuleNotFoundError:
    from ingestao_bronze import gerar_leituras
    from popular_catalogo import MAQUINAS


def test_simulador_gera_campos_esperados():
    leituras = gerar_leituras(MAQUINAS, amostras_por_maquina=2)
    assert len(leituras) == 6  # 3 máquinas x 2 amostras
    campos_obrigatorios = {
        "evento_id",
        "maquina_id",
        "timestamp_evento",
        "temp_c",
        "vibracao_mms",
        "pressao_bar",
        "consumo_kw",
    }
    assert campos_obrigatorios.issubset(leituras[0].keys())