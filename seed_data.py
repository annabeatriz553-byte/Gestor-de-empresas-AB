"""
Script para popular o banco de dados com dados de exemplo.
Execute: python seed_data.py
"""

from database import *
from datetime import datetime, timedelta
import random

def seed_database():
    """Popula o banco com dados de exemplo."""

    print("📊 Populando banco de dados com dados de exemplo...")

    empresas_exemplo = [
        {
            "nome": "Acme Tecnologia Ltda",
            "responsavel": "João Silva",
            "email": "joao@acmetech.com.br",
            "telefone": "(11) 98765-4321",
            "cnpj": "12.345.678/0001-90",
            "endereco": "Rua Principal, 100 - São Paulo, SP",
            "status": "ativa",
            "observacoes": "Empresa líder em soluções de TI"
        },
        {
            "nome": "Global Solutions Brasil",
            "responsavel": "Maria Santos",
            "email": "maria@globalsolutions.com.br",
            "telefone": "(11) 97654-3210",
            "cnpj": "98.765.432/0001-12",
            "endereco": "Av. Paulista, 500 - São Paulo, SP",
            "status": "ativa",
            "observacoes": "Consultoria empresarial"
        },
        {
            "nome": "Inovação Brasil Services",
            "responsavel": "Pedro Costa",
            "email": "pedro@inovacaobrasil.com.br",
            "telefone": "(21) 99876-5432",
            "cnpj": "55.555.555/0001-55",
            "endereco": "Rua Commerce, 200 - Rio de Janeiro, RJ",
            "status": "ativa",
            "observacoes": "Serviços de importação e exportação"
        },
        {
            "nome": "TechStart Inovações",
            "responsavel": "Ana Julia",
            "email": "ana@techstart.com.br",
            "telefone": "(85) 98765-0987",
            "cnpj": "11.111.111/0001-11",
            "endereco": "Avenida Tecnológica, 150 - Fortaleza, CE",
            "status": "ativa",
            "observacoes": "Startup de tecnologia em crescimento"
        },
        {
            "nome": "Consultoria Plus",
            "responsavel": "Carlos Mendes",
            "email": "carlos@consultoriaplus.com.br",
            "telefone": "(31) 98765-4567",
            "cnpj": "22.222.222/0001-22",
            "endereco": "Rua Consultoria, 300 - Belo Horizonte, MG",
            "status": "inativa",
            "observacoes": "Empresa em transição"
        },
    ]

    for empresa in empresas_exemplo:
        success, message = adicionar_empresa(
            empresa["nome"],
            empresa["responsavel"],
            empresa["email"],
            empresa["telefone"],
            empresa["cnpj"],
            empresa["endereco"],
            empresa["status"],
            empresa["observacoes"]
        )
        if success:
            print(f"✅ {empresa['nome']}")
        else:
            print(f"⚠️  {empresa['nome']} - {message}")

    print("\n📅 Adicionando situações do mês...")

    empresas = obter_todas_empresas()

    for empresa in empresas:
        for mes in range(1, 13):
            mes_str = f"{mes:02d}"

            notas_entrada = random.randint(0, 1)
            notas_saida = random.randint(0, 1)
            notas_servico = random.randint(0, 1)
            conciliacao = random.randint(0, 1)
            documentacao_ok = random.randint(0, 1)

            success, message = adicionar_situacao_mes(
                empresa[0],
                mes_str,
                2024,
                notas_entrada,
                notas_saida,
                notas_servico,
                conciliacao,
                documentacao_ok,
                f"Dados de exemplo para {mes_str}/2024"
            )

            if success and mes == 1:
                print(f"✅ Situações adicionadas para {empresa[1]}")

    print("\n" + "="*50)
    print("✨ Banco de dados populado com sucesso!")
    print("="*50)
    print("\nPróximos passos:")
    print("1. Execute: streamlit run app.py")
    print("2. Abra: http://localhost:8501")
    print("3. Explore o dashboard com dados de exemplo!")

if __name__ == "__main__":
    seed_database()
