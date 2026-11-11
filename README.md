# OpsPilot AI — Demo para PME

**Aplicação Streamlit demonstrável sem instalação local.** Analisa eventos fictícios de manutenção, inspeções e seguros de 12 viaturas/empilhadores e prepara propostas de ação exportáveis em CSV.

## Publicar apenas com o navegador (GitHub + Streamlit Cloud)

1. Descarrega o ZIP e **extrai-o**. Não coloques o ZIP como ficheiro no GitHub: o Streamlit precisa dos ficheiros Python separados.
2. Entra em https://github.com e cria um repositório público chamado `opspilot-ai` (Create a new repository).
3. No repositório, usa **Add file > Upload files** (ou **uploading an existing file**, se o repositório estiver vazio). Seleciona **todos os ficheiros extraídos** e confirma em **Commit changes**.
4. Confirma que `app.py`, `engine.py`, `agent.py` e `requirements.txt` aparecem **na raiz** do repositório, e não dentro de uma pasta.
5. Vai a https://share.streamlit.io, inicia sessão com o GitHub, seleciona **Create app > Yup, I have an app**.
6. Escolhe o repositório `opspilot-ai`, branch `main` e **Main file path**: `app.py`. Carrega em **Deploy**.
7. Abre o endereço público `https://<nome-da-app>.streamlit.app` e testa os 3 cenários. Podes enviar este URL numa candidatura.

**Sem chave de API**, a aplicação corre como demonstração baseada em regras, sem executar um LLM. Este é o modo mais simples e seguro para a primeira publicação.

## Ativar posteriormente a IA com ferramentas (opcional)

A aplicação inclui código para OpenAI Responses API + function calling com 3 ferramentas autorizadas e apenas de leitura/proposta. Para o ativar, usa **Streamlit Cloud > App settings > Secrets**, com formato TOML:

```toml
OPENAI_API_KEY = "a-tua-chave-aqui"
OPENAI_MODEL = "gpt-5-mini"
```

**Nunca coloques uma chave de API nos ficheiros do GitHub.** A aplicação pública não tem autenticação nem um limite global de requisições; utiliza IA real apenas com controlos de custos e acesso apropriados. Os limites de execução por sessão não impedem utilização repetida por vários visitantes.

## Ficheiros

- `app.py`: interface Streamlit e exportação CSV
- `engine.py`: dados sintéticos e regras determinísticas
- `agent.py`: agente opcional com function calling
- `requirements.txt`: bibliotecas para a publicação
- `ARQUITETURA.md`: decisões de arquitetura e fluxo agentic
- `test_engine.py` e `test_agent_tools.py`: testes unitários

## Limitações

Dados, datas, prioridades, estimativas e históricos são fictícios. Não existe acesso a ERP, email ou equipamentos reais. O programa não executa operações externas. Os prazos de inspeção são dados demonstrativos, não aconselhamento jurídico.

## Tecnologias

Python · Streamlit · Pandas · OpenAI Responses API (opcional)
