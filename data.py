"""Dados exclusivamente sintéticos para demonstração OpsPilot AI.

Cada execução inicia uma cópia isolada por sessão Streamlit. Não existe persistência
entre visitas: usar Exportar/Importar JSON para transportar alterações.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

TABLES = {
    "ativos": "Ativos / inventário",
    "colaboradores": "Colaboradores e habilitações",
    "fornecedores": "Fornecedores e SLA",
    "contratos": "Contratos e seguros",
    "utilizacao": "Utilização (km / horas)",
    "despesas": "Combustível, energia, portagens e custos",
    "multas": "Multas e coimas",
    "afetacoes": "Afetações de equipamentos por turno",
    "consumiveis": "Baterias, carregadores e consumíveis",
    "manutencoes": "Manutenções e ordens de trabalho",
    "inspecoes": "Inspeções e verificações",
    "checklists": "Checklists diárias",
    "sinistros": "Sinistros e acidentes",
    "propostas": "Propostas de fornecedores",
    "orcamentos": "Orçamento anual",
    "telemetria": "Telemática / GPS (simulado)",
}

# Cada tabela utiliza colunas simples para edição no browser.
REQUIRED = {
    "ativos": ["id", "categoria", "designacao"],
    "colaboradores": ["id", "nome"],
    "fornecedores": ["id", "nome"],
    "contratos": ["id", "ativo_id", "fornecedor_id"],
    "utilizacao": ["id", "ativo_id"],
    "despesas": ["id", "ativo_id", "categoria"],
    "multas": ["id", "ativo_id"],
    "afetacoes": ["id", "ativo_id", "operador_id"],
    "consumiveis": ["id", "ativo_id"],
    "manutencoes": ["id", "ativo_id", "tipo"],
    "inspecoes": ["id", "ativo_id"],
    "checklists": ["id", "ativo_id"],
    "sinistros": ["id", "ativo_id"],
    "propostas": ["id", "fornecedor_id"],
    "orcamentos": ["id", "categoria"],
    "telemetria": ["id", "ativo_id"],
}


def build_demo(today: date | None = None) -> dict[str, list[dict[str, Any]]]:
    today = today or date.today()
    dt = lambda n: (today + timedelta(days=n)).isoformat()
    year = today.year
    def first_day(offset_months=0):
        # Enough for a demo; all usage and expenses are year-to-date.
        return f"{year}-01-01"

    ativos = [
        dict(id="V-101", categoria="Viatura", designacao="Carrinha entregas 01", matricula="AA-11-AA", energia="Gasóleo", local="Lisboa", departamento="Distribuição", colaborador_id="C-01", estado="Operacional", km_atual=142300, horas_atual=0, proxima_manutencao=dt(-4), limite_km_manutencao=145000, limite_horas_manutencao=0, custo_compra_eur=29000, valor_residual_eur=6000, vida_util_anos=6),
        dict(id="V-102", categoria="Viatura", designacao="Carrinha entregas 02", matricula="BB-22-BB", energia="Gasóleo", local="Porto", departamento="Distribuição", colaborador_id="C-02", estado="Operacional", km_atual=95000, horas_atual=0, proxima_manutencao=dt(8), limite_km_manutencao=97000, limite_horas_manutencao=0, custo_compra_eur=0, valor_residual_eur=0, vida_util_anos=0),
        dict(id="V-103", categoria="Viatura", designacao="Ligeiro apoio 03", matricula="CC-33-CC", energia="Elétrico", local="Lisboa", departamento="Técnica", colaborador_id="C-03", estado="Operacional", km_atual=42000, horas_atual=0, proxima_manutencao=dt(52), limite_km_manutencao=46000, limite_horas_manutencao=0, custo_compra_eur=34000, valor_residual_eur=9000, vida_util_anos=7),
        dict(id="V-104", categoria="Viatura", designacao="Carrinha serviço 04", matricula="DD-44-DD", energia="Gasóleo", local="Setúbal", departamento="Serviços", colaborador_id="C-04", estado="Imobilizado", km_atual=185600, horas_atual=0, proxima_manutencao=dt(13), limite_km_manutencao=185000, limite_horas_manutencao=0, custo_compra_eur=26000, valor_residual_eur=3500, vida_util_anos=6),
        dict(id="V-105", categoria="Viatura", designacao="Comercial 05", matricula="EE-55-EE", energia="Híbrido", local="Lisboa", departamento="Comercial", colaborador_id="C-05", estado="Operacional", km_atual=36500, horas_atual=0, proxima_manutencao=dt(65), limite_km_manutencao=40000, limite_horas_manutencao=0, custo_compra_eur=0, valor_residual_eur=0, vida_util_anos=0),
        dict(id="V-106", categoria="Viatura", designacao="Carrinha entregas 06", matricula="FF-66-FF", energia="Gasóleo", local="Porto", departamento="Distribuição", colaborador_id="C-06", estado="Operacional", km_atual=120700, horas_atual=0, proxima_manutencao=dt(21), limite_km_manutencao=120000, limite_horas_manutencao=0, custo_compra_eur=27500, valor_residual_eur=5000, vida_util_anos=6),
        dict(id="E-201", categoria="Empilhador", designacao="Empilhador elétrico 01", matricula="", energia="Elétrico", local="Armazém Norte", departamento="Logística", colaborador_id="", estado="Operacional", km_atual=0, horas_atual=3950, proxima_manutencao=dt(4), limite_km_manutencao=0, limite_horas_manutencao=4000, custo_compra_eur=22500, valor_residual_eur=4000, vida_util_anos=7),
        dict(id="E-202", categoria="Empilhador", designacao="Empilhador GLP 02", matricula="", energia="Gás", local="Armazém Sul", departamento="Logística", colaborador_id="", estado="Operacional", km_atual=0, horas_atual=2670, proxima_manutencao=dt(38), limite_km_manutencao=0, limite_horas_manutencao=2750, custo_compra_eur=0, valor_residual_eur=0, vida_util_anos=0),
        dict(id="E-203", categoria="Empilhador", designacao="Empilhador diesel 03", matricula="", energia="Gasóleo", local="Armazém Norte", departamento="Logística", colaborador_id="", estado="Manutenção", km_atual=0, horas_atual=4960, proxima_manutencao=dt(-1), limite_km_manutencao=0, limite_horas_manutencao=5000, custo_compra_eur=24500, valor_residual_eur=5000, vida_util_anos=8),
        dict(id="E-204", categoria="Empilhador", designacao="Porta-paletes elétrico 04", matricula="", energia="Elétrico", local="Armazém Sul", departamento="Logística", colaborador_id="", estado="Operacional", km_atual=0, horas_atual=1140, proxima_manutencao=dt(70), limite_km_manutencao=0, limite_horas_manutencao=1250, custo_compra_eur=8000, valor_residual_eur=1200, vida_util_anos=6),
    ]
    colaboradores = [
        dict(id="C-01", nome="Ana Martins (fictício)", departamento="Distribuição", carta_valida_ate=dt(360), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-02", nome="Bruno Reis (fictício)", departamento="Distribuição", carta_valida_ate=dt(21), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-03", nome="Carla Sousa (fictício)", departamento="Técnica", carta_valida_ate=dt(200), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-04", nome="Diogo Alves (fictício)", departamento="Serviços", carta_valida_ate=dt(-5), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-05", nome="Eva Rocha (fictício)", departamento="Comercial", carta_valida_ate=dt(400), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-06", nome="Filipe Lopes (fictício)", departamento="Distribuição", carta_valida_ate=dt(89), formacao_empilhador_ate="", ativo="Sim"),
        dict(id="C-07", nome="Gonçalo Melo (fictício)", departamento="Armazém", carta_valida_ate="", formacao_empilhador_ate=dt(35), ativo="Sim"),
        dict(id="C-08", nome="Helena Vaz (fictício)", departamento="Armazém", carta_valida_ate="", formacao_empilhador_ate=dt(-12), ativo="Sim"),
        dict(id="C-09", nome="Inês Costa (fictício)", departamento="Armazém", carta_valida_ate="", formacao_empilhador_ate=dt(220), ativo="Sim"),
    ]
    fornecedores = [
        dict(id="F-01", nome="RentFrota Demo", especialidade="Renting", pontuacao_1_5=4.3, sla_alvo_h=48, resposta_media_h=31),
        dict(id="F-02", nome="Seguro Exemplo", especialidade="Seguros", pontuacao_1_5=4.0, sla_alvo_h=72, resposta_media_h=56),
        dict(id="F-03", nome="Oficina Atlântico Demo", especialidade="Oficina", pontuacao_1_5=3.8, sla_alvo_h=24, resposta_media_h=34),
        dict(id="F-04", nome="Energia & Frota Demo", especialidade="Combustível", pontuacao_1_5=4.6, sla_alvo_h=48, resposta_media_h=20),
        dict(id="F-05", nome="LiftService Demo", especialidade="Empilhadores", pontuacao_1_5=4.2, sla_alvo_h=24, resposta_media_h=17),
    ]
    contratos = [
        dict(id="CT-01", ativo_id="V-102", fornecedor_id="F-01", tipo="Renting", inicio=dt(-400), fim=dt(45), mensalidade_eur=510, estado="Ativo", devolucao_prevista=dt(45)),
        dict(id="CT-02", ativo_id="V-105", fornecedor_id="F-01", tipo="Renting", inicio=dt(-600), fim=dt(18), mensalidade_eur=480, estado="Ativo", devolucao_prevista=dt(18)),
        dict(id="CT-03", ativo_id="E-202", fornecedor_id="F-05", tipo="Aluguer", inicio=dt(-280), fim=dt(85), mensalidade_eur=365, estado="Ativo", devolucao_prevista=dt(85)),
        dict(id="CT-04", ativo_id="V-101", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-300), fim=dt(24), mensalidade_eur=74, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-05", ativo_id="V-102", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-300), fim=dt(17), mensalidade_eur=70, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-06", ativo_id="V-103", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-250), fim=dt(90), mensalidade_eur=77, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-07", ativo_id="V-104", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-300), fim=dt(-3), mensalidade_eur=88, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-08", ativo_id="V-105", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-280), fim=dt(35), mensalidade_eur=71, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-09", ativo_id="V-106", fornecedor_id="F-02", tipo="Seguro", inicio=dt(-260), fim=dt(75), mensalidade_eur=76, estado="Ativo", devolucao_prevista=""),
        dict(id="CT-10", ativo_id="E-201", fornecedor_id="F-05", tipo="Manutenção", inicio=dt(-330), fim=dt(120), mensalidade_eur=115, estado="Ativo", devolucao_prevista=""),
    ]
    utilizacao = [
        dict(id=f"U-{i+1:03d}", ativo_id=asset["id"], periodo=f"{year}-01 a {today.isoformat()}", km_periodo=km, horas_previstas=hp, horas_produtivas=hu, horas_paragem=down)
        for i,(asset, km,hp,hu,down) in enumerate(zip(ativos,
            [14500,12200,8500,15700,9800,13900,0,0,0,0],
            [0,0,0,0,0,0,1600,1600,1600,1200],
            [0,0,0,0,0,0,1240,1100,980,760],
            [32,20,6,115,15,27,25,35,120,18]))
    ]
    despesas = [
        dict(id=f"D-{i+1:03d}", ativo_id=aid, data=dt(-int((i*11)%190)), categoria=cat, quantidade=q, unidade=uni, valor_eur=v, cartao_referencia=card, detalhe=detail)
        for i,(aid,cat,q,uni,v,card,detail) in enumerate([
            ("V-101","Combustível",920,"L",1570,"CART-101","Gasóleo"),("V-102","Combustível",820,"L",1380,"CART-102","Gasóleo"),
            ("V-103","Energia",1220,"kWh",302,"","Carregamento"),("V-104","Combustível",1050,"L",1790,"CART-104","Gasóleo"),
            ("V-105","Combustível",490,"L",855,"CART-105","Híbrido"),("V-106","Combustível",890,"L",1540,"CART-106","Gasóleo"),
            ("E-201","Energia",2400,"kWh",480,"","Carregamento"),("E-202","Gás",390,"kg",820,"","GLP"),
            ("E-203","Combustível",620,"L",1100,"","Gasóleo"),("E-204","Energia",840,"kWh",164,"","Bateria"),
            ("V-101","Portagens",1,"registo",390,"VV-101","Via Verde"),("V-102","Portagens",1,"registo",350,"VV-102","Via Verde"),
            ("V-104","Portagens",1,"registo",300,"VV-104","Via Verde"),("V-106","Portagens",1,"registo",330,"VV-106","Via Verde"),
            ("V-101","Outros",1,"registo",120,"","Lavagens e estacionamento"),
        ])
    ]
    multas = [
        dict(id="M-001", ativo_id="V-101", data=dt(-18), valor_eur=120, condutor_id="C-01", prazo_resposta=dt(12), referencia="REF-DEMO-001", estado="Identificar/validar"),
        dict(id="M-002", ativo_id="V-104", data=dt(-35), valor_eur=95, condutor_id="C-04", prazo_resposta=dt(-4), referencia="REF-DEMO-002", estado="Comunicação pendente"),
    ]
    afetacoes = [
        dict(id="A-001", ativo_id="E-201", armazem="Armazém Norte", turno="Manhã", operador_id="C-07", data=dt(0), horas_previstas=8, horas_trabalhadas=6.5),
        dict(id="A-002", ativo_id="E-202", armazem="Armazém Sul", turno="Tarde", operador_id="C-09", data=dt(0), horas_previstas=8, horas_trabalhadas=6),
        dict(id="A-003", ativo_id="E-203", armazem="Armazém Norte", turno="Manhã", operador_id="C-08", data=dt(1), horas_previstas=8, horas_trabalhadas=0),
        dict(id="A-004", ativo_id="E-204", armazem="Armazém Sul", turno="Noite", operador_id="C-09", data=dt(1), horas_previstas=8, horas_trabalhadas=4.5),
    ]
    consumiveis = [
        dict(id="CO-01", ativo_id="E-201", categoria="Bateria", designacao="Bateria tração", quantidade=1, unidade="un", custo_eur=900, proxima_verificacao=dt(19), estado="Em uso"),
        dict(id="CO-02", ativo_id="E-201", categoria="Carregador", designacao="Carregador 48 V", quantidade=1, unidade="un", custo_eur=430, proxima_verificacao=dt(7), estado="A inspecionar"),
        dict(id="CO-03", ativo_id="E-202", categoria="Gás", designacao="Garrafa GLP", quantidade=4, unidade="un", custo_eur=150, proxima_verificacao=dt(80), estado="Em stock"),
        dict(id="CO-04", ativo_id="E-203", categoria="Consumível", designacao="Kit rodas", quantidade=1, unidade="kit", custo_eur=220, proxima_verificacao=dt(40), estado="A substituir"),
    ]
    manutencoes = [
        dict(id="OT-001", ativo_id="V-101", tipo="Preventiva", categoria="Revisão", descricao="Troca óleo e filtros", abertura=dt(-10), prevista=dt(-4), concluida="", fornecedor_id="F-03", custo_eur=320, horas_paragem=0, causa="Plano", estado="Aberta"),
        dict(id="OT-002", ativo_id="V-104", tipo="Corretiva", categoria="Bateria", descricao="Falha ao arrancar", abertura=dt(-8), prevista=dt(2), concluida="", fornecedor_id="F-03", custo_eur=490, horas_paragem=40, causa="Falha bateria", estado="Em curso"),
        dict(id="OT-003", ativo_id="E-201", tipo="Corretiva", categoria="Carregamento", descricao="Intermitência carregador", abertura=dt(-22), prevista=dt(-19), concluida=dt(-18), fornecedor_id="F-05", custo_eur=210, horas_paragem=8, causa="Conector desgastado", estado="Concluída"),
        dict(id="OT-004", ativo_id="E-203", tipo="Corretiva", categoria="Hidráulica", descricao="Fuga hidráulica", abertura=dt(-5), prevista=dt(-1), concluida="", fornecedor_id="F-05", custo_eur=680, horas_paragem=62, causa="Vedação", estado="Em curso"),
        dict(id="OT-005", ativo_id="V-102", tipo="Preventiva", categoria="Travões", descricao="Revisão sistema travagem", abertura=dt(-12), prevista=dt(-6), concluida=dt(-6), fornecedor_id="F-03", custo_eur=295, horas_paragem=5, causa="Plano", estado="Concluída"),
        dict(id="OT-006", ativo_id="E-201", tipo="Preventiva", categoria="Revisão", descricao="Inspeção técnica interna", abertura=dt(-16), prevista=dt(-2), concluida=dt(-1), fornecedor_id="F-05", custo_eur=150, horas_paragem=4, causa="Plano", estado="Concluída"),
    ]
    inspecoes = [
        dict(id="I-001", ativo_id="V-101", tipo="IPO (data registada)", data_limite=dt(64), executada_em="", estado="Pendente", evidencia=""),
        dict(id="I-002", ativo_id="V-102", tipo="IPO (data registada)", data_limite=dt(11), executada_em="", estado="Pendente", evidencia=""),
        dict(id="I-003", ativo_id="V-104", tipo="IPO (data registada)", data_limite=dt(-3), executada_em="", estado="Pendente", evidencia=""),
        dict(id="I-004", ativo_id="E-201", tipo="Verificação equipamento", data_limite=dt(15), executada_em="", estado="Pendente", evidencia=""),
        dict(id="I-005", ativo_id="E-202", tipo="Verificação equipamento", data_limite=dt(75), executada_em="", estado="Pendente", evidencia=""),
        dict(id="I-006", ativo_id="E-203", tipo="Verificação equipamento", data_limite=dt(-2), executada_em="", estado="Pendente", evidencia=""),
    ]
    checklists = [
        dict(id="CK-001", ativo_id="E-201", operador_id="C-07", data=dt(0), travoes="OK", pneus="OK", luzes="OK", seguranca="OK", observacoes="", resultado="Conforme"),
        dict(id="CK-002", ativo_id="E-203", operador_id="C-08", data=dt(0), travoes="OK", pneus="Anomalia", luzes="OK", seguranca="OK", observacoes="Desgaste de roda", resultado="Não conforme"),
        dict(id="CK-003", ativo_id="V-101", operador_id="C-01", data=dt(-1), travoes="OK", pneus="OK", luzes="OK", seguranca="OK", observacoes="", resultado="Conforme"),
    ]
    sinistros = [
        dict(id="S-001", ativo_id="V-104", data=dt(-50), tipo="Acidente ligeiro", custo_eur=950, comunicado_seguro="Sim", causa="Manobra", medidas_corretivas="Formação e revisão de procedimento", estado="Em análise"),
        dict(id="S-002", ativo_id="E-203", data=dt(-20), tipo="Dano de equipamento", custo_eur=320, comunicado_seguro="Não", causa="Impacto em rack", medidas_corretivas="Reforçar sinalização", estado="Concluído"),
    ]
    propostas = [
        dict(id="P-001", fornecedor_id="F-01", ativo_id="V-105", modalidade="Renting", entrada_eur=0, mensalidade_eur=480, prazo_meses=48, manutencao_incluida="Sim", estado="Recebida"),
        dict(id="P-002", fornecedor_id="F-01", ativo_id="V-105", modalidade="Renting", entrada_eur=1200, mensalidade_eur=445, prazo_meses=48, manutencao_incluida="Não", estado="Em comparação"),
        dict(id="P-003", fornecedor_id="F-05", ativo_id="E-202", modalidade="Aluguer", entrada_eur=0, mensalidade_eur=365, prazo_meses=36, manutencao_incluida="Sim", estado="Recebida"),
    ]
    orcamentos = [
        dict(id=f"B-{i+1:02d}", ano=year, categoria=cat, orcamento_eur=budget)
        for i,(cat,budget) in enumerate([
            ("Combustível",15000),("Energia",3200),("Gás",2400),("Portagens",3000),("Outros",1200),
            ("Contratos",25000),("Manutenção",12500),("Consumíveis",3500),("Sinistros",4500),("Multas",550)
        ])
    ]
    telemetria = [
        dict(id=f"TEL-{i+1:03d}", ativo_id=a["id"], data_hora=dt(-i%4)+" 10:30", ultima_localizacao=a["local"], km_leitura=a["km_atual"], horas_leitura=a["horas_atual"], fonte="Simulada")
        for i,a in enumerate(ativos)
    ]
    return {
        "ativos": ativos, "colaboradores": colaboradores, "fornecedores": fornecedores,
        "contratos": contratos, "utilizacao": utilizacao, "despesas": despesas,
        "multas": multas, "afetacoes": afetacoes, "consumiveis": consumiveis,
        "manutencoes": manutencoes, "inspecoes": inspecoes,
        "checklists": checklists, "sinistros": sinistros, "propostas": propostas,
        "orcamentos": orcamentos, "telemetria": telemetria,
    }
