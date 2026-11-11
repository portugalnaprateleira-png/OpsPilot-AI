"""OpsPilot AI - shareable, self-contained portfolio demonstrator."""
from __future__ import annotations

import os
import pandas as pd
import streamlit as st
from engine import build_assets, draft_action_plan, get_due_items, summarize

st.set_page_config(page_title="OpsPilot AI | Demo PME", page_icon="🧭", layout="wide")
st.markdown("""
<style>
.main .block-container {max-width:1100px; padding-top:2rem;}
h1,h2,h3 {letter-spacing:-.025em;}
.stButton>button[kind="primary"] {background:#125b73; border-color:#125b73;}
[data-testid="stMetric"] {background:#f3f7f9;border:1px solid #e3ebef; border-radius:14px;padding:14px;}
.smallnote {color:#64748b;font-size:.90rem;}
.hero {padding:16px 0 10px;}
</style>""", unsafe_allow_html=True)


def get_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)


api_key = get_secret("OPENAI_API_KEY")
model = get_secret("OPENAI_MODEL", "gpt-5-mini")

with st.sidebar:
    st.header("OpsPilot AI")
    st.caption("Demonstração de arquitetura agentic para PME")
    st.divider()
    scenario = st.radio("Escolhe um cenário", [
        "Prazos dos próximos 30 dias",
        "Empilhadores: riscos e ações",
        "Preparar a próxima semana",
    ])
    st.caption("A demonstração utiliza exclusivamente dados fictícios.")
    st.divider()
    st.write("**Modo**")
    st.success("AI com ferramentas ativas" if api_key else "Simulação baseada em regras")
    if not api_key:
        st.caption("Configura OPENAI_API_KEY nos Secrets para ativar o agente LLM.")
    st.caption("Sem emails enviados, sem compras ou alterações de sistemas.")

st.markdown('<div class="hero"><h1>🧭 OpsPilot AI</h1></div>', unsafe_allow_html=True)
st.subheader("Da informação operacional a um plano de ação")
st.markdown("Uma demonstração prática de como uma pequena empresa pode antecipar problemas de manutenção, acompanhar prazos e preparar decisões — **sem ERP complexo**.")
st.info("🔎 Ambiente de demonstração: todos os ativos, datas, históricos e custos são sintéticos. Não substitui verificações legais ou técnicas.")

assets = build_assets()
base = summarize(30)
a, b, c, d = st.columns(4)
a.metric("Ativos na demonstração", len(assets))
b.metric("Eventos nos próximos 30 dias", base["ocorrencias"])
c.metric("Prazos ultrapassados", base["atrasadas"])
d.metric("Ativos com ações", base["ativos_afetados"])

st.divider()
left, right = st.columns([3, 2])
with left:
    st.markdown("### Um problema real, um clique")
    st.write("1. O agente consulta dados de equipamentos e prazos.")
    st.write("2. Um motor de regras calcula prioridades e prazos sem depender da IA.")
    st.write("3. A IA utiliza ferramentas e transforma os resultados numa recomendação.")
    st.write("4. O plano é apresentado para aprovação humana; nada é executado automaticamente.")
with right:
    st.markdown("### Cenário selecionado")
    st.write("**" + scenario + "**")
    st.caption("O resultado mostra também evidência operacional e o plano proposto.")

window_days = 7 if scenario == "Preparar a próxima semana" else 30
asset_type = "Empilhadores" if scenario == "Empilhadores: riscos e ações" else "Todos"
prompts = {
    "Prazos dos próximos 30 dias": "Analisa os prazos de manutenção, inspeções registadas e seguros dos próximos 30 dias de todos os ativos. Identifica urgências e prepara plano de ação.",
    "Empilhadores: riscos e ações": "Foca os empilhadores e os próximos 30 dias. Identifica as intervenções prioritárias. Se relevante, consulta o histórico de E-201 e apresenta riscos com cautela.",
    "Preparar a próxima semana": "Analisa todos os ativos para os próximos 7 dias e apresenta uma agenda de ações prioritárias para um responsável operacional.",
}
if "executions" not in st.session_state:
    st.session_state.executions = 0
if "result" not in st.session_state:
    st.session_state.result = None
if "last_scenario" not in st.session_state:
    st.session_state.last_scenario = None

if st.button("✨ Analisar e preparar plano de ação", type="primary", use_container_width=True):
    response = None
    used_ai = False
    error = None
    if api_key and st.session_state.executions < 3:
        try:
            from agent import run_agent
            with st.spinner("Agente a consultar ferramentas e a analisar os riscos..."):
                response = run_agent(prompts[scenario], api_key, model=model)
            used_ai = True
            st.session_state.executions += 1
        except Exception:
            error = "O modelo não respondeu nesta execução. É apresentado o resultado determinístico."
    elif api_key:
        error = "Limite demonstrativo de três execuções de IA por sessão atingido. A análise por regras continua disponível."
    st.session_state.result = {"answer": response, "ai": used_ai, "error": error}
    st.session_state.last_scenario = scenario

result = st.session_state.result if st.session_state.last_scenario == scenario else None
if result is not None:
    st.divider()
    st.markdown("## Resultado da análise")
    if result["error"]:
        st.warning(result["error"])
    if result["ai"]:
        st.success("Análise executada com modelo LLM e chamadas reais a ferramentas read-only.")
        st.markdown(result["answer"]["answer"])
        with st.expander("Ver rastreabilidade: ferramentas utilizadas"):
            st.json(result["answer"]["trace"])
    else:
        st.info("Análise determinística: a IA não foi executada nesta sessão. Configura a chave no servidor para demonstrar function calling real.")
        summary = summarize(window_days, asset_type)
        st.markdown(f"Foram identificados **{summary['ocorrencias']} eventos** que requerem acompanhamento, envolvendo **{summary['ativos_afetados']} ativos**. O plano abaixo organiza-os por prioridade e data.")

    due = get_due_items(window_days, asset_type)
    if due:
        st.markdown("### Evidência de dados")
        show = pd.DataFrame(due)[["ativo", "equipamento", "evento", "data", "dias", "prioridade"]]
        show.columns = ["Ativo", "Equipamento", "Evento", "Data", "Dias", "Prioridade"]
        st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown("### Plano preparado para validação")
        plan = draft_action_plan(window_days, asset_type)
        plan_df = pd.DataFrame(plan)
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Exportar propostas em CSV", plan_df.to_csv(index=False).encode("utf-8-sig"), file_name="opspilot-plano-proposto.csv", mime="text/csv")
        st.caption("O botão exporta um ficheiro; não cria ordens reais nem envia mensagens.")
    else:
        st.success("Não foram encontrados prazos dentro da janela selecionada nos dados fictícios.")

st.divider()
with st.expander("Ver inventário de exemplo"):
    df = pd.DataFrame([{
        "Ativo": asset["id"], "Tipo": asset["tipo"],
        "Designação": asset["designacao"], "Local": asset["local"]
    } for asset in assets])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("OpsPilot AI · Portfolio demo · Python + Streamlit + OpenAI Responses API + Function Calling · Dados 100% fictícios")
