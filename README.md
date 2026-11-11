# OpsPilot AI — Gestão inteligente de frotas e equipamentos para PME

> **Demonstração de portefólio** | Streamlit + Python + regras determinísticas + agente OpenAI opcional  
> Dados **100% fictícios**. Sem dados reais, integrações, persistência partilhada, comunicações automáticas ou pareceres legais.

## Experimentar em 2 minutos

1. Abre a aplicação Streamlit publicada.
2. Seleciona **📊 Dashboard**, consulta os alertas e exporta o plano.
3. Seleciona **🚐 Frota** ou **🏗️ Empilhadores** e navega pelas secções.
4. Em **🗃️ Dados & Registos**, altera a data de inspeção de um ativo e clica **Guardar alterações**.
5. Volta ao **Dashboard**: os alertas refletem a alteração.
6. Em **🤖 Assistente Agentic**, consulta o plano determinístico; o agente LLM apenas funciona quando configurado e autorizado.

## Cobertura funcional

| Domínio | Funcionalidades implementadas neste MVP |
|---|---|
| Frota automóvel | Inventário, matrículas e responsáveis, km, estado, contratos e renovações, renting/seguros, despesas e cartões, portagens, multas e estado das comunicações |
| Empilhadores | Inventário e tipo de energia, armazém e turno, afetações de operadores, compra/aluguer, baterias e consumíveis, horas, ocupação |
| Manutenção | Calendário, alertas por km/horas, manutenção preventiva/corretiva, ordens propostas, oficinas, causa de falha, custos, tempo parado, inspeções |
| Segurança | Cartas e formações com validade, detetor de incompatibilidades nas afetações, checklists, sinistros e medidas corretivas, avisos de conformidade |
| Custos | Orçamento anual, TCO indicativo YTD, EUR/km, EUR/h, categorias e desvios, simulador compra/renting, consumos |
| Fornecedores | Cadastro, contratos e prazos, avaliações, resposta média vs SLA, propostas comparáveis por custo nominal |
| Reporting | KPIs, exportação CSV, telemetria/localização sintética, fatores configuráveis de emissões, oportunidades de eficiência |

**16 tabelas editáveis** na aplicação, sem necessidade de Excel/ERP. Edição com validação mínima de IDs e referências; importação/exportação JSON de todas as tabelas. Alterações vivem **só na sessão do navegador**.

## Arquitetura enxuta

```text
Visitante (browser)
       |
 Streamlit (app.py)  ← UI / navegação / formulários / CSV / JSON
       |
  ├─ data.py           dados sintéticos de demonstração (16 domínios)
  ├─ logic.py          regras verificáveis, alertas, TCO, KPI
  └─ agent.py          agente opcional, ferramentas read-only
       |
    OpenAI Responses API (apenas quando ativada e autorizada)
```

Ver [ARQUITETURA.md](ARQUITETURA.md) para decisões, requisitos e evolução para produção.

## Substituir a versão anterior no GitHub (sem instalar software)

1. Descarrega o ZIP e **extrai o conteúdo** no teu computador.
2. Abre o teu repositório no GitHub pelo navegador.
3. Escolhe **Add file → Upload files** (ou o link *uploading an existing file*).
4. Carrega os ficheiros extraídos **na raiz** do repositório. Confirma que `app.py`, `logic.py`, `data.py`, `agent.py` e `requirements.txt` aparecem diretamente na raiz, sem pasta adicional.
5. Quando o GitHub detetar ficheiros com o mesmo nome, confirma a **substituição** e clica **Commit changes**. Podes manter `engine.py` antigo, mas a nova aplicação não o utiliza.
6. Se a aplicação já estiver publicada no Streamlit Cloud, o código atualizado será detetado pelo serviço. Não precisas de alterar o endereço publicado.
7. Abre o link Streamlit e experimenta o dashboard e os registos.

Se ainda não estiver publicada: em https://share.streamlit.io seleciona repositório, `main` e `app.py`, depois **Deploy**.

### Ficheiros da raiz

- `app.py` — interface, módulos e registos
- `data.py` — dados exclusivamente sintéticos
- `logic.py` — motor determinístico, regras, indicadores, custos e propostas
- `agent.py` — ferramentas read-only e OpenAI Responses API
- `requirements.txt` — dependências
- `test_logic.py`, `test_agent_tools.py` — testes automáticos
- `ARQUITETURA.md` — documentação de arquitetura
- `PASSOS_GITHUB.md` — guia de publicação pelo navegador

## Ativar a IA (OPCIONAL)

A demo funciona sem OpenAI. Para experimentar o agente LLM, define nos **Secrets** da aplicação, nunca no GitHub:

```toml
OPENAI_API_KEY = "chave-da-tua-conta"
DEMO_ACCESS_CODE = "codigo-secreto-dificil-de-adivinhar"
OPENAI_MODEL = "gpt-5-mini"
```

O visitante tem de introduzir o código de acesso para ativar chamadas à API. Existe limite de 3 chamadas por sessão, **mas não é controlo robusto de utilização ou despesa**; configura quotas/limites de gasto na API e prefere deixar a IA desligada numa demo pública. Não colocar segredos, dados reais ou documentos pessoais em texto de prompts.

## Testes

```bash
pip install -r requirements.txt pytest
pytest -q test_logic.py test_agent_tools.py
```

**Sem dependência de IA para executar os testes.**

## Limitações e transparência

- A aplicação não é um EAM/ERP pronto para produção, mas um **protótipo operacional e arquitetural**.
- Não há autenticação empresarial, persistência entre sessões, permissões por utilizador, auditoria persistente ou backups automáticos.
- As datas de inspeções são **registos sintéticos**, não cálculo automático de prazos legais.
- Não existem integrações reais com Via Verde, seguradoras, oficinas, WMS, GPS ou fornecedores.
- O TCO é aproximado: valores sintéticos YTD + mensalidades aproximadas + depreciação linear; não é modelação contabilística validada.
- É proibido usar dados reais/identificáveis nesta demonstração pública sem desenho de privacidade, segurança e base legal adequados.

Criado para mostrar como uma PME pode começar com dados simples e evoluir progressivamente para uma solução integrada.
