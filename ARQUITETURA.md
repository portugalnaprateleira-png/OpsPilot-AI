# OpsPilot AI — Decisões de arquitetura e rastreabilidade dos requisitos

## Objetivo

Demonstrar a pequenos empregadores e PME uma solução empresarial simples que começa por dados de operação, regras verificáveis e interação conversacional assistida por IA. É uma **demonstração**, não produto pronto para operação com dados reais.

## Contexto e princípios

1. **Zero instalação no PC**: editar ficheiros no GitHub e publicar em Streamlit Community Cloud.
2. **Time to value**: todas as funcionalidades visíveis na mesma aplicação.
3. **Sem overengineering**: um processo Python; sem containers, Kafka, Kubernetes, ETL e microserviços.
4. **Separação de responsabilidades**: UI (`app.py`), dados (`data.py`), lógica (`logic.py`), agente (`agent.py`).
5. **Determinismo onde importa**: datas, indicadores, custos e validações calculados pelo Python, não pelo LLM.
6. **Human-in-the-loop**: ordens de trabalho ficam em `Proposta`, sem efeitos fora da sessão.
7. **Safety first**: IA usa ferramentas read-only, limite de chamadas, código de acesso opcional, dados fictícios.
8. **Transparência**: cada indicador apresenta pressupostos e limitações.

## Diagrama lógico

```text
            Navegador (utilizador/entrevistador)
                          |
            Streamlit Community Cloud
              app.py (interface web)
       +------------------+-------------------+
       |                  |                   |
     data.py            logic.py            agent.py
  16 tabelas fake    regras / TCO / KPI   function calling
       |                  |                   |
 session_state      funções puras         tools read-only
       |                  |                   |
 exportar JSON/CSV ----->|             OpenAI Responses API
                                         (configurada por Secrets)

Legenda: não há integração com ERP nem telemática externa.
```

## Cobertura dos requisitos

| # | Atividade solicitada | Implementação demonstrativa | Observação |
|---|---|---|---|
| 1.1 | Inventário viaturas | `ativos` + módulo Frota | Matrícula, responsável, km, estado e local |
| 1.2 | Leasing/renting/seguros | `contratos`, avisos e datas | Ciclo de vida editável; não renova automaticamente |
| 1.3 | Atribuição e utilização | `ativos.colaborador_id`, `utilizacao` | Histórico completo exigiria tabela de eventos |
| 1.4 | Combustível/cartões/Via Verde | `despesas` e `cartao_referencia` | Sem API real de fornecedores |
| 1.5 | Multas/coimas | `multas` + prazo + condutor + estado | Não envia comunicações externas |
| 2.1 | Inventário de equipamentos | `ativos` com categoria Empilhador e energia | Inclui porta-paletes |
| 2.2 | Distribuição por armazém/turno | `afetacoes` | Detecta operadores sem validade documental e equipamentos indisponíveis |
| 2.3 | Aluguer/compra/substituição | `contratos`, `propostas`, simulador | Comparação nominal ilustrativa |
| 2.4 | Baterias/carregadores/gás | `consumiveis` + despesas | Atributos e prazos editáveis |
| 2.5 | Horas e taxa de utilização | `utilizacao` + KPIs | Horas produtivas/planeadas |
| 3.1 | Manutenção preventiva | Regra por calendário, km e horas | Datas e limiares são dados sintéticos |
| 3.2 | Corretiva/fornecedores | `manutencoes` + `fornecedores` | Gestão de ordem de trabalho local |
| 3.3 | IPO/verificações | `inspecoes` + alertas | Sem cálculo automático de regra legal |
| 3.4 | Avarias/custos/causas | `manutencoes`, gráfico de causas | Relatórios simples |
| 3.5 | Imobilização | `ativos.estado`, horas de paragem | Medição indicativa |
| 4.1 | Cumprimento legal | Alertas documentais configuráveis | NÃO substitui validação jurídica e SST |
| 4.2 | Formação empilhadores | `colaboradores.formacao_empilhador_ate` | Controlos de afetação ilustrativos |
| 4.3 | Cartas de condução | `colaboradores.carta_valida_ate` | Validade manual |
| 4.4 | Sinistros | `sinistros`, causa, comunicação e ações | Sem sinistros reais |
| 4.5 | Checklists diárias | `checklists` + formulário | Lança alerta de anomalia |
| 5.1 | Orçamento anual | `orcamentos` | Desvios YTD aproximados |
| 5.2 | TCO por ativo | `cost_analysis` | Custos registados + rendas + depreciação indicativa |
| 5.3 | Desvios e redução | Dashboard e tabela de categorias | Propostas dependem da validação da empresa |
| 5.4 | Compra/renting/substituição | Simulador de custo nominal | Sem NPV e impostos |
| 6.1 | Fornecedores e contratos | `fornecedores`, `contratos` | Negociação externa não implementada |
| 6.2 | Avaliação e propostas | Pontuações, `propostas` comparadas | Controlo de qualidade básico |
| 6.3 | SLA | Tempo de resposta médio vs objetivo | Não implementa cálculo contratual real |
| 7.1 | Reporting e KPIs | Dashboard e Reporting; CSV | Dados da sessão |
| 7.2 | Telemática/GPS | `telemetria` sintética | Sem GPS real ou monitorização de pessoas |
| 7.3 | Eficiência/eletrificação/CO₂ | Recomendações e simulador de fatores | Não é inventário oficial de emissões |

## KPIs e fórmulas

| KPI | Implementação | Limite |
|---|---|---|
| Disponibilidade | ativos operacionais / total × 100 | fotografia atual, não disponibilidade histórica |
| Utilização de empilhadores | horas produtivas / horas planeadas × 100 | dados YTD sintéticos |
| Cumprimento manutenção preventiva | preventivas concluídas no prazo / preventivas previstas com prazo vencido | apenas ordens registadas |
| Prazos documentais de inspeções e seguros | inspeções concluídas no prazo e seguros marcados renovados / registos com prazo vencido | não equivale a conformidade legal global |
| Custo/km | TCO estimado YTD / km YTD por viatura | registo de gastos incompleto |
| Custo/h | TCO estimado YTD / horas produtivas YTD por empilhador | sem rateio de custos gerais |
| Sinistros/custos | contagem e soma dos sinistros | sem normalização por exposição |
| Consumo combustível/energia | soma por unidades | não compara tecnologias heterogéneas |

### Exemplo de motor de regras vs agent

1. O motor lê uma inspeção com `data_limite` nos próximos 7 dias.
2. `get_alerts` emite um evento estruturado com fonte, ativo, prioridade e ação proposta.
3. O utilizador pede: "o que devo priorizar?".
4. O agente chama `get_alerts` e `draft_action_plan` através de ferramentas autorizadas.
5. O agente redige uma recomendação explicável em português europeu.
6. A ação é exportada ou mantida em estado `Proposta`. Nenhum fornecedor recebe uma ordem real.

## Decisões e trade-offs

- **Decisão A — Streamlit em vez de frontend+API separados.** Reduz custo e tempo, mas não escala em autenticação granular e multiutilizador.
- **Decisão B — `st.session_state` em vez de PostgreSQL.** Demonstra interação sem infraestrutura; perde dados ao terminar a sessão. Exportar JSON compensa apenas numa demo.
- **Decisão C — Um agente vs multiagent.** Menos pontos de falha, custo previsível, governança mais fácil; dividir agentes só se workflows independentes justificarem.
- **Decisão D — Chamadas read-only.** Evita alterações externas sem autorização, mas não demonstra execução autónoma com efeitos permanentes.
- **Decisão E — Datas legais manualmente configuradas.** Evita inferir obrigações incorretas de legislação e tipo de equipamento.

## Requisitos para entrada em produção

1. Formalizar modelo de dados (ativos, identidades, manutenções, documentos e eventos) e migração.
2. Adicionar login SSO, autorização por perfil, separação por empresa, trilhos de auditoria e gestão de segredos.
3. PostgreSQL com backups, retenção, migrações, observabilidade e encriptação.
4. Integrar fornecedores/ERP/WMS/GPS por APIs, filas/eventos quando necessário, reconciliação e idempotência.
5. Introduzir workflows de aprovação real, notificação e evidências documentais.
6. Validar legislação portuguesa, SST, proteção de dados e políticas laborais com especialistas.
7. Definir SLO, recuperação de falhas, limites de gastos LLM, avaliação de prompts e testes de segurança.
8. Desenhar testes de ponta a ponta, carga, concorrência, privacidade e recuperação.

## Governança do agente

- LLM é opcional e protegida por `OPENAI_API_KEY` + `DEMO_ACCESS_CODE` no Streamlit Secrets.
- Ferramentas são somente consulta de dados sintéticos da sessão.
- Limites de 4 passos e 4 ferramentas por resposta; input máximo 1.200 caracteres.
- Não há execução de scripts arbitrários nem escrita em sistemas externos.
- Dado vindo de ferramentas é tratado como não confiável nas instruções do agente.
- O código de acesso e limite por sessão **não substituem** autenticação nem limites de API para exposição pública.
