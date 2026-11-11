"""OpsPilot AI PME — aplicação Streamlit de portefólio, sem backend externo.

Os registos ficam na sessão do browser; usa exportação JSON para guardar.
Nunca utilizar dados reais/sensíveis neste protótipo público sem controlos adicionais.
"""
from __future__ import annotations

import copy
import hmac
import json
import os
from datetime import date

import pandas as pd
import streamlit as st

from data import TABLES, build_demo
from logic import (
    compare_proposals, cost_analysis, energy_metrics, generate_action_plan,
    get_alerts, get_compliance_rate, get_maintenance_rate, make_maintenance_proposals,
    number, operating_indicators, parse_date, recorded_deadline_compliance, supplier_sla, validate_dataset,
)

st.set_page_config(page_title="OpsPilot AI | Gestão PME", page_icon="🧭", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1350px;padding-top:1.6rem;}
[data-testid="stMetric"]{background:rgba(115,139,160,.06);border:1px solid rgba(115,139,160,.18);border-radius:12px;padding:12px;}
h1,h2,h3{letter-spacing:-.025em}
section[data-testid="stSidebar"]{min-width:255px}
</style>
""", unsafe_allow_html=True)


def secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)


def load_state() -> None:
    if "records" not in st.session_state:
        st.session_state.records = build_demo()
    if "revision" not in st.session_state:
        st.session_state.revision = 1


def as_df(rows, cols=None) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if cols:
        df = df.reindex(columns=cols)
    return df


def table(rows, cols=None, label="Sem registos para apresentar."):
    if not rows:
        st.info(label)
    else:
        st.dataframe(as_df(rows, cols), use_container_width=True, hide_index=True)


def download_csv(label: str, rows, filename: str, cols=None):
    if rows:
        st.download_button(label, as_df(rows, cols).to_csv(index=False).encode("utf-8-sig"), file_name=filename, mime="text/csv")


def header(title: str, desc: str):
    st.title(title)
    st.caption(desc)


def show_alerts(alerts, limit=None):
    rows = alerts[:limit] if limit else alerts
    table(rows, ["area", "referencia", "ativo", "evento", "prazo", "dias", "prioridade", "acao_proposta"])


def euro(n):
    return f"{number(n):,.0f} €".replace(",", " ")


def fmt_percent(n):
    return f"{number(n):.1f}%"


def show_inventory(data, kind):
    subset = [a for a in data["ativos"] if a.get("categoria") == kind]
    cols = ["id", "designacao", "matricula", "energia", "local", "departamento", "colaborador_id", "estado", "km_atual", "horas_atual", "proxima_manutencao"]
    table(subset, cols)
    download_csv("Exportar inventário CSV", subset, f"opspilot-{kind.lower()}.csv", cols)


def view_dashboard(data):
    header("Centro de Operações", "Visão geral da frota e dos equipamentos — dados fictícios e editáveis.")
    today = date.today()
    metrics = operating_indicators(data)
    alerts = get_alerts(data, 30)
    costs = cost_analysis(data)
    a, b, c, d = st.columns(4)
    a.metric("Ativos", metrics["ativos"])
    b.metric("Alertas (30 dias)", len(alerts))
    c.metric("Prazo ultrapassado", sum(a["dias"] < 0 for a in alerts))
    d.metric("Custos registados/estimados YTD", euro(costs["total_eur"]))
    a, b, c = st.columns(3)
    a.metric("Disponibilidade instantânea", fmt_percent(metrics["disponibilidade_pct"]))
    b.metric("Utilização dos empilhadores", fmt_percent(metrics["utilizacao_empilhadores_pct"]))
    c.metric("Sinistros registados", metrics["sinistros"])
    st.subheader("Prioridades para a próxima semana")
    short = get_alerts(data, 7)
    show_alerts(short, limit=12)
    st.subheader("Alertas por área")
    if alerts:
        counts = as_df(alerts).groupby("area").size().rename("Alertas")
        st.bar_chart(counts)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Plano proposto")
        plan = generate_action_plan(data, 7)
        table(plan[:10], ["ativo", "area", "prioridade", "prazo", "acao"])
        download_csv("Descarregar plano de ação", plan, "opspilot-plano-semanal.csv")
    with col2:
        st.subheader("Como experimentar")
        st.markdown("""**1.** Abre qualquer módulo no menu lateral.  
**2.** Consulta ativos, contratos, manutenção e indicadores.  
**3.** Em **Dados & Registos**, altera um valor e guarda.  
**4.** Volta ao dashboard e verifica a análise atualizada.  
**5.** Testa o **Assistente Agentic** ou exporta um plano.

**Nota:** os dados vivem nesta sessão, sem persistência permanente.""")


def view_fleet(data):
    header("1 · Frota automóvel", "Inventário, atribuições, renting, seguros, combustível, Via Verde e multas.")
    cars = [a for a in data["ativos"] if a.get("categoria") == "Viatura"]
    a,b,c = st.columns(3)
    a.metric("Viaturas", len(cars))
    b.metric("Indisponíveis", sum(x.get("estado") != "Operacional" for x in cars))
    c.metric("Contratos associados", sum(x.get("ativo_id") in {a["id"] for a in cars} for x in data["contratos"]))
    sections = st.tabs(["Inventário e atribuição", "Leasing / seguros", "Combustível, Via Verde e despesas", "Multas e coimas"])
    with sections[0]:
        show_inventory(data, "Viatura")
        st.info("Para alterar a matrícula, condutor, quilómetros, estado ou departamento: Dados & Registos → Ativos / inventário.")
    with sections[1]:
        ids = {a["id"] for a in cars}
        contracts = [x for x in data["contratos"] if x.get("ativo_id") in ids]
        table(contracts)
        st.subheader("Renovações e devoluções a acompanhar")
        show_alerts([x for x in get_alerts(data, 90) if x["area"] == "Contratos" and x["ativo"] in ids])
    with sections[2]:
        rows = [x for x in data["despesas"] if x.get("ativo_id") in {a["id"] for a in cars}]
        st.metric("Despesas listadas", euro(sum(number(x.get("valor_eur")) for x in rows)))
        table(rows)
        download_csv("Exportar despesas", rows, "opspilot-despesas-frota.csv")
    with sections[3]:
        table(data["multas"])
        st.info("O condutor e o estado da comunicação são editáveis em Dados & Registos. Não são enviadas comunicações externas.")


def view_equipment(data):
    header("2 · Empilhadores e movimentação", "Inventário, afetação por turno, horas, contratos, baterias e consumíveis.")
    forklifts = [a for a in data["ativos"] if a.get("categoria") == "Empilhador"]
    indicators = operating_indicators(data)
    a,b,c = st.columns(3)
    a.metric("Equipamentos", len(forklifts))
    b.metric("Utilização acumulada", fmt_percent(indicators["utilizacao_empilhadores_pct"]))
    c.metric("Indisponíveis", sum(a.get("estado") != "Operacional" for a in forklifts))
    tabs = st.tabs(["Equipamentos", "Distribuição por turno", "Baterias, gás e consumíveis", "Horas e ocupação", "Compra/aluguer"])
    with tabs[0]:
        show_inventory(data, "Empilhador")
    with tabs[1]:
        table(data["afetacoes"])
        issues = [x for x in get_alerts(data, 30) if x["area"] == "Segurança" and x["referencia"].startswith("A-")]
        st.subheader("Incompatibilidades detetadas")
        show_alerts(issues)
    with tabs[2]:
        table(data["consumiveis"])
        show_alerts([x for x in get_alerts(data, 30) if x["area"] == "Equipamentos"])
    with tabs[3]:
        rows = [r for r in data["utilizacao"] if r.get("ativo_id") in {x["id"] for x in forklifts}]
        table(rows)
        if rows:
            st.bar_chart(as_df(rows).set_index("ativo_id")[["horas_previstas", "horas_produtivas"]])
        st.caption("Ocupação = horas produtivas / horas planeadas. Indicador YTD ilustrativo; não substitui telemetria real.")
    with tabs[4]:
        table([x for x in data["contratos"] if x.get("ativo_id") in {a["id"] for a in forklifts}])
        table([x for x in compare_proposals(data) if x["ativo"] in {a["id"] for a in forklifts}])


def view_maintenance(data):
    header("3 · Manutenção e fiabilidade", "Preventiva, corretiva, intervenções, inspeções, causas e imobilização.")
    due = [x for x in get_alerts(data, 30) if x["area"] == "Manutenção"]
    completed, total, rate = get_maintenance_rate(data)
    a,b,c = st.columns(3)
    a.metric("Alertas de manutenção", len(due))
    b.metric("Preventivas no prazo", fmt_percent(rate), help=f"{completed}/{total} intervenções previstas até hoje")
    c.metric("Horas de paragem registadas", sum(number(x.get("horas_paragem")) for x in data["manutencoes"]))
    tabs = st.tabs(["Plano preventivo", "Ordens de trabalho", "Avarias e fiabilidade", "Inspeções"])
    with tabs[0]:
        show_alerts(due)
        st.markdown("**Gerar ordens internas em estado Proposta**")
        if st.button("Preparar ordens de manutenção (30 dias)", type="primary"):
            created = make_maintenance_proposals(data, 30)
            st.success(f"{created} propostas criadas nesta sessão. Nenhuma ordem foi enviada para fornecedores.")
        st.caption("A função é idempotente para o mesmo evento: clicar novamente não duplica as propostas.")
    with tabs[1]:
        table(data["manutencoes"])
        download_csv("Exportar ordens de trabalho", data["manutencoes"], "opspilot-manutencoes.csv")
    with tabs[2]:
        issues = [x for x in data["manutencoes"] if x.get("tipo") == "Corretiva"]
        table(issues, ["id", "ativo_id", "descricao", "causa", "horas_paragem", "custo_eur", "estado"])
        if issues:
            causes = as_df(issues).groupby("causa").size().rename("Ocorrências")
            st.bar_chart(causes)
        st.caption("As causas recorrentes são classificações registadas — não são diagnósticos automáticos.")
    with tabs[3]:
        table(data["inspecoes"])


def view_compliance(data):
    header("4 · Segurança e conformidade", "Habilitações, verificações, checklists, sinistros e ações corretivas.")
    done, due, pct = recorded_deadline_compliance(data)
    st.metric("Prazos registados: inspeções e seguros (já vencidos)", f"{done}/{due}" if due else "Sem vencimentos")
    st.caption("Registos documentais no prazo; inclui seguros com workflow marcado Renovado. Não constitui verificação de conformidade legal.")
    tabs = st.tabs(["Prazos e habilitações", "Checklists", "Sinistros", "Regras e limites"])
    with tabs[0]:
        show_alerts([x for x in get_alerts(data, 90) if x["area"] in ("Conformidade", "Habilitações", "Segurança")])
        table(data["colaboradores"])
    with tabs[1]:
        table(data["checklists"])
        st.subheader("Registar uma checklist simulada")
        with st.form("new_checklist"):
            asset = st.selectbox("Ativo", [x["id"] for x in data["ativos"]])
            operator = st.selectbox("Colaborador / operador", [x["id"] for x in data["colaboradores"]])
            c1,c2,c3,c4 = st.columns(4)
            trav = c1.selectbox("Travões", ["OK", "Anomalia"])
            tyres = c2.selectbox("Pneus/rodas", ["OK", "Anomalia"])
            lights = c3.selectbox("Luzes", ["OK", "Anomalia"])
            safety = c4.selectbox("Segurança", ["OK", "Anomalia"])
            observation = st.text_input("Observações (sem dados pessoais)", max_chars=180)
            submitted = st.form_submit_button("Registar checklist na sessão")
        if submitted:
            result = "Conforme" if all(x == "OK" for x in [trav, tyres, lights, safety]) else "Não conforme"
            record = dict(id=f"CK-NEW-{len(data['checklists'])+1:03d}", ativo_id=asset, operador_id=operator,
                          data=date.today().isoformat(), travoes=trav, pneus=tyres, luzes=lights,
                          seguranca=safety, observacoes=observation, resultado=result)
            data["checklists"].append(record)
            st.success(f"Checklist registada: {result}. Os resultados afetam os alertas desta sessão.")
    with tabs[2]:
        table(data["sinistros"])
        st.caption("Participação à seguradora, análise de causas e medidas corretivas são campos de registo. Sem envio automático.")
    with tabs[3]:
        st.warning("As datas são introduzidas manualmente e os exemplos são fictícios. A aplicação NÃO determina automaticamente o enquadramento legal português nem bloqueia fisicamente equipamentos.")
        st.markdown("""O processo real necessita de validação das obrigações aplicáveis a cada ativo, verificações técnicas por entidade competente, políticas de SST, documentação, proteção de dados e controlo de acessos. Nenhuma sugestão deste protótipo substitui aconselhamento profissional ou avaliação de riscos.""")


def view_finance(data):
    header("5 · Custos e orçamento", "TCO indicativo YTD, custo/km ou hora, desvios e comparação económica simples.")
    analysis = cost_analysis(data)
    st.metric("TCO estimado do ano até hoje", euro(analysis["total_eur"]))
    st.caption(analysis["observacao"])
    tabs = st.tabs(["TCO por ativo", "Orçamento e desvios", "Compra vs renting", "Consumos"])
    with tabs[0]:
        table(analysis["ativos"])
        download_csv("Exportar TCO", analysis["ativos"], "opspilot-tco.csv")
        st.caption("EUR/km ou EUR/hora apenas quando existe volume operacional YTD. Valores não comparáveis entre categorias sem normalização.")
    with tabs[1]:
        table(analysis["categorias"])
        if analysis["categorias"]:
            df = as_df(analysis["categorias"]).set_index("categoria")
            st.bar_chart(df[["custo_ytd_eur", "orcamento_ytd_proporcional_eur"]])
        st.caption("Comparação aproximada do orçamento anual repartido proporcionalmente pelo número de meses; sazonalidade não modelada.")
    with tabs[2]:
        st.markdown("**Simulador nominal de decisão (sem desconto financeiro, impostos ou inflação)**")
        a,b,c = st.columns(3)
        purchase = a.number_input("Preço de compra (€)", min_value=0.0, value=28000.0, step=1000.0)
        residual = b.number_input("Valor residual previsto (€)", min_value=0.0, value=6000.0, step=500.0)
        maintenance = c.number_input("Manutenção anual na compra (€)", min_value=0.0, value=1400.0, step=100.0)
        d,e,f = st.columns(3)
        monthly = d.number_input("Renda mensal (€)", min_value=0.0, value=540.0, step=20.0)
        years = e.number_input("Horizonte (anos)", min_value=1, max_value=10, value=4)
        upfront = f.number_input("Entrada de renting (€)", min_value=0.0, value=0.0, step=100.0)
        buy_total = purchase - min(residual, purchase) + maintenance * years
        rent_total = upfront + monthly * 12 * years
        a,b = st.columns(2)
        a.metric("Compra: custo nominal no horizonte", euro(buy_total))
        b.metric("Renting: custo nominal no horizonte", euro(rent_total))
        st.info(f"Pelos pressupostos introduzidos, a opção nominalmente inferior é: **{'Compra' if buy_total < rent_total else 'Renting' if rent_total < buy_total else 'Empate'}**. Para decisão real, acrescentar financiamento, seguro, impostos, serviços incluídos e valor temporal do dinheiro.")
    with tabs[3]:
        values = energy_metrics(data)
        a,b,c = st.columns(3)
        a.metric("Combustível registado", f"{values['litros']:,.0f} L")
        b.metric("Eletricidade registada", f"{values['kwh']:,.0f} kWh")
        c.metric("Gas registado", f"{values['kg_gas']:,.0f} kg")
        st.caption("Consumo médio por tipo de energia deve ser calculado por viaturas comparáveis e com a mesma janela temporal.")


def view_suppliers(data):
    header("6 · Fornecedores e contratos", "Avaliação de fornecedores, propostas, comparação, prazos e indicadores SLA.")
    tabs = st.tabs(["Avaliação e SLA", "Contratos", "Comparar propostas"])
    with tabs[0]:
        rows = supplier_sla(data)
        table(rows)
        st.caption("SLA demonstrativo: média de resposta comparada com objetivo em horas. Não representa o cumprimento de todos os incidentes nem cláusulas reais.")
    with tabs[1]:
        table(data["contratos"])
        show_alerts([a for a in get_alerts(data, 90) if a["area"] == "Contratos"])
    with tabs[2]:
        rows = compare_proposals(data)
        table(rows)
        download_csv("Exportar comparação de propostas", rows, "opspilot-propostas.csv")
        st.caption("Custo nominal = entrada + mensalidades × prazo; diferenças de cobertura, seguros e serviços exigem revisão.")


def view_reporting(data):
    header("7 · Reporting e melhoria contínua", "Indicadores para direção, dados de telemática simulada e sustentabilidade.")
    ops = operating_indicators(data)
    costs = cost_analysis(data)
    energy = energy_metrics(data)
    pm_ok, pm_total, pm_rate = get_maintenance_rate(data)
    leg_ok, leg_total, leg_rate = recorded_deadline_compliance(data)
    rows = [
        {"indicador":"Custo por km", "valor":"Ver TCO por ativo", "base":"Custos YTD / km YTD"},
        {"indicador":"Custo por hora", "valor":"Ver TCO por equipamento", "base":"Custos YTD / horas produtivas YTD"},
        {"indicador":"Disponibilidade dos ativos", "valor":fmt_percent(ops["disponibilidade_pct"]), "base":"Ativos operacionais / ativos totais (fotografia atual)"},
        {"indicador":"Manutenção preventiva no prazo", "valor":fmt_percent(pm_rate), "base":f"{pm_ok}/{pm_total} intervenções com prazo vencido"},
        {"indicador":"Sinistros", "valor":str(ops["sinistros"]), "base":"N.º de registos"},
        {"indicador":"Custo dos sinistros", "valor":euro(ops["custo_sinistros_eur"]), "base":"Montantes dos registos"},
        {"indicador":"Combustível", "valor":f"{energy['litros']:.0f} L", "base":"Quantidade em despesas YTD"},
        {"indicador":"Energia elétrica", "valor":f"{energy['kwh']:.0f} kWh", "base":"Quantidade em despesas YTD"},
        {"indicador":"Utilização dos empilhadores", "valor":fmt_percent(ops["utilizacao_empilhadores_pct"]), "base":"Horas produtivas / horas planeadas"},
        {"indicador":"Prazos registados: inspeções e seguros", "valor":fmt_percent(leg_rate), "base":f"{leg_ok}/{leg_total} registos com prazo passado"},
    ]
    table(rows)
    download_csv("Exportar indicadores", rows, "opspilot-kpis.csv")
    tabs = st.tabs(["Telemática simulada", "Eficiência e sustentabilidade", "Propostas de melhoria"])
    with tabs[0]:
        st.warning("Demonstração sem acesso a GPS real ou localização de colaboradores. As localizações são fictícias e representam instalações, não coordenadas em tempo real.")
        table(data["telemetria"])
    with tabs[1]:
        c1,c2 = st.columns(2)
        diesel_factor = c1.number_input("Fator demonstrativo kgCO₂/L combustível", min_value=0.0, value=2.68, step=0.01)
        elec_factor = c2.number_input("Fator demonstrativo kgCO₂/kWh", min_value=0.0, value=0.20, step=0.01)
        emission = energy["litros"] * diesel_factor + energy["kwh"] * elec_factor
        st.metric("Emissões estimadas (proxy parcial)", f"{emission/1000:,.2f} tCO₂")
        st.caption("Fatores editáveis e ilustrativos. Não é inventário de emissões GHG/ESG; mistura diferentes usos e omite GLP, híbridos e emissões do ciclo de vida.")
    with tabs[2]:
        st.markdown("""**Oportunidades a validar:**
- Substituição de veículos com custo por km elevado, após análise de idade, financiamento e utilização.
- Dimensionamento dos equipamentos por armazém e turno, usando ocupação real.
- Redução de imobilização através de manutenção preventiva e gestão de peças críticas.
- Avaliação de eletrificação com infraestrutura, autonomia e custo energético efetivos.
- Normalização de registos, checklists e contratos antes de integrar aplicações externas.
""")


def agent_question_ui(data):
    header("Assistente Agentic", "Pergunta em linguagem natural → ferramentas Python → proposta explicada, sujeita a validação.")
    st.markdown("""**Exemplos de perguntas:**
- Quais são as obrigações e manutenções prioritárias nos próximos 30 dias?
- Que ativos têm maior custo estimado e o que devo investigar?
- Quais os riscos de segurança antes de afetar um empilhador?
- Que fornecedores estão a ultrapassar o SLA?""")
    prompt = st.text_area("O que queres analisar?", value="Analisa os riscos e prazos dos próximos 30 dias e prepara cinco recomendações prioritárias.", max_chars=1200)
    key = secret("OPENAI_API_KEY")
    access = secret("DEMO_ACCESS_CODE")
    if not key:
        st.info("Modo demonstração: agente LLM desativado. Usa o plano baseado em regras abaixo. Para ativar, configura os Secrets do Streamlit.")
    elif not access:
        st.warning("Chave da API configurada, mas falta DEMO_ACCESS_CODE. O agente fica desativado para evitar custos numa página pública.")
    code = st.text_input("Código de acesso à demo de IA (se configurado)", type="password") if key and access else ""
    allowed = bool(key and access and hmac.compare_digest(code, access))
    if "ai_runs" not in st.session_state:
        st.session_state.ai_runs = 0
    if st.button("Consultar agente IA", type="primary", disabled=not allowed or st.session_state.ai_runs >= 3):
        if not prompt.strip():
            st.error("Escreve uma pergunta.")
        else:
            try:
                from agent import run_agent
                with st.spinner("Agente a consultar ferramentas autorizadas..."):
                    output = run_agent(prompt.strip(), data, key, secret("OPENAI_MODEL", "gpt-5-mini"))
                st.session_state.ai_runs += 1
                st.session_state.agent_output = output
            except Exception as e:
                st.error("Não foi possível executar a IA nesta tentativa. Consulta a versão baseada em regras. Verifica a configuração e quota da API.")
    if st.session_state.get("agent_output"):
        result = st.session_state.agent_output
        st.subheader("Resposta do agente")
        st.markdown(result["answer"])
        with st.expander("Ferramentas chamadas (rastreabilidade)"):
            st.json(result["trace"])
    st.divider()
    st.subheader("Plano baseado em regras — sem IA nem custo")
    days = st.slider("Horizonte de análise", 7, 90, 30, 1)
    plan = generate_action_plan(data, days)
    table(plan[:25])
    download_csv("Exportar plano", plan, "opspilot-plano.csv")
    st.caption("O agente só consulta dados da sessão e propõe ações; não envia emails nem altera sistemas externos. Limite por sessão não é uma proteção completa contra abuso: mantém acesso protegido e quota de API.")


def view_records(data):
    header("Dados & Registos", "Editar todas as 16 tabelas no browser. Alterações aplicam-se apenas à sessão atual.")
    st.warning("Não introduzas dados pessoais reais, matrículas verdadeiras, contratos confidenciais ou segredos nesta demo pública. Exporta JSON para guardar alterações; o Streamlit Cloud não as persiste.")
    name = st.selectbox("Escolhe o conjunto de dados", list(TABLES.keys()), format_func=lambda k: f"{TABLES[k]} ({len(data[k])})")
    st.caption("Podes editar células, acrescentar linhas ou eliminar linhas. Mantém os IDs únicos e as referências a ativos/colaboradores/fornecedores existentes.")
    original = as_df(data[name])
    editor_key = f"editor_{name}_v{st.session_state.revision}"
    edited = st.data_editor(original, num_rows="dynamic", use_container_width=True, hide_index=True, key=editor_key)
    if st.button("Guardar alterações desta tabela", type="primary"):
        replacement = copy.deepcopy(data)
        rows = json.loads(edited.to_json(orient="records", date_format="iso"))
        # Eliminar linhas inteiramente vazias, mantendo a validação do resto.
        rows = [r for r in rows if any(v not in (None, "") for v in r.values())]
        replacement[name] = rows
        errors = validate_dataset(replacement)
        if errors:
            st.error("Não foi possível guardar: " + " | ".join(errors[:5]))
        else:
            st.session_state.records = replacement
            st.session_state.revision += 1
            st.success("Alterações guardadas nesta sessão.")
            st.rerun()
    st.divider()
    st.subheader("Guardar / restaurar os dados desta demonstração")
    backup = json.dumps(data, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    st.download_button("⬇️ Exportar TODAS as tabelas (JSON)", backup, file_name="opspilot-backup-demo.json", mime="application/json")
    uploaded = st.file_uploader("Importar backup JSON (máx. 2 MB)", type="json")
    if uploaded and st.button("Validar e importar JSON"):
        if uploaded.size > 2_000_000:
            st.error("Ficheiro demasiado grande (limite 2 MB).")
        else:
            try:
                candidate = json.loads(uploaded.getvalue().decode("utf-8"))
                errors = validate_dataset(candidate)
                if errors:
                    st.error("Importação recusada: " + " | ".join(errors[:5]))
                else:
                    st.session_state.records = candidate
                    st.session_state.revision += 1
                    st.success("Backup importado nesta sessão.")
                    st.rerun()
            except (ValueError, UnicodeError) as e:
                st.error("JSON inválido. Verifica se o ficheiro foi exportado pelo OpsPilot.")
    if st.button("Repor dados fictícios de origem"):
        st.session_state.records = build_demo()
        st.session_state.revision += 1
        st.rerun()


def view_architecture():
    header("Arquitetura e limites", "O que esta demo implementa e o que falta para operar uma PME com dados reais.")
    st.code("""Navegador → Streamlit (app.py)
             ├── Dados editáveis por sessão (data.py)
             ├── Regras / KPIs / alertas (logic.py)
             └── Agente opcional (agent.py)
                    └── OpenAI Responses API + tools read-only

Exportação JSON/CSV → ficheiro local do utilizador
Sem ERP, sem email, sem GPS real, sem base de dados nem autenticação empresarial.""", language="text")
    st.markdown("""**Cobertura demonstrativa:** 7 domínios operacionais, 16 tabelas editáveis, regras determinísticas, simulação de custos, relatórios e agente opcional.

**Fora do MVP:** persistência multiutilizador, login e papéis, controlo de acessos, gestão documental com evidências, integrações reais (Via Verde, seguradoras, ERP, WMS, GPS), notificações, envio de coimas, ordens externas, conformidade jurídica validada, auditoria imutável, testes de carga e monitorização de produção.

**Para uma empresa real:** primeiro definir necessidades, riscos, base legal e modelo de dados; depois introduzir autenticação, Postgres gerido, API de integração, auditoria, backups e testes de segurança. Nunca colocar dados pessoais reais numa demo aberta.""")


load_state()
data = st.session_state.records
with st.sidebar:
    st.title("🧭 OpsPilot AI")
    st.caption("Fleet & Equipment Control · Demo PME")
    page = st.radio("Navegação", [
        "📊 Dashboard", "🚐 Frota automóvel", "🏗️ Empilhadores", "🔧 Manutenção", "🛡️ Segurança e conformidade",
        "💶 Custos e orçamento", "🤝 Fornecedores", "📈 Reporting", "🤖 Assistente Agentic", "🗃️ Dados & Registos", "ℹ️ Arquitetura",
    ])
    st.divider()
    st.caption("✅ Dados fictícios · ✏️ Editáveis na sessão")
    st.caption("📅 " + date.today().strftime("%d/%m/%Y"))
    if secret("OPENAI_API_KEY") and secret("DEMO_ACCESS_CODE"):
        st.success("IA disponível com código")
    else:
        st.info("IA opcional; regras ativas")
    st.caption("Sem ERP / GPS real · Sem emails enviados")

if page == "📊 Dashboard": view_dashboard(data)
elif page == "🚐 Frota automóvel": view_fleet(data)
elif page == "🏗️ Empilhadores": view_equipment(data)
elif page == "🔧 Manutenção": view_maintenance(data)
elif page == "🛡️ Segurança e conformidade": view_compliance(data)
elif page == "💶 Custos e orçamento": view_finance(data)
elif page == "🤝 Fornecedores": view_suppliers(data)
elif page == "📈 Reporting": view_reporting(data)
elif page == "🤖 Assistente Agentic": agent_question_ui(data)
elif page == "🗃️ Dados & Registos": view_records(data)
else: view_architecture()
st.divider()
st.caption("OpsPilot AI · Projeto de demonstração · Dados 100% sintéticos · Execução sem base de dados permanente · Nunca constitui parecer técnico ou jurídico")
