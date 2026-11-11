# Baby steps — publicar OpsPilot AI sem instalar nada

## A. Atualizar o GitHub

1. Descarrega o ZIP desta versão.
2. Extrai todos os ficheiros. **Não carregues o ZIP em si.**
3. Abre https://github.com e entra no teu repositório `opspilot-ai`.
4. Clica em **Add file → Upload files**. Também podes usar o link *uploading an existing file*.
5. Arrasta os ficheiros extraídos, não a pasta que os contém.
6. Confirma que os ficheiros `app.py`, `data.py`, `logic.py`, `agent.py`, `requirements.txt` aparecem todos no nível principal.
7. Finaliza com **Commit changes**.
8. Se existirem `engine.py` e `test_engine.py` da versão antiga, podem permanecer, mas não são usados pela nova aplicação. Opcionalmente elimina-os depois pelo editor do GitHub, para evitar confusão.

## B. Verificar o Streamlit Cloud

Se já publicaste a aplicação, abre o mesmo endereço `.streamlit.app`. Ao guardar alterações no GitHub, o Streamlit normalmente reinicia com os novos ficheiros.

Se ainda não publicaste:

1. Abre https://share.streamlit.io.
2. Escolhe **Create app → Yup, I have an app**.
3. Seleciona o teu repositório, branch `main`, caminho `app.py`.
4. Clica em **Deploy**.

## C. Teste de aceitação (5 cliques)

- [ ] No Dashboard aparecem 10 ativos e alertas.
- [ ] Em Frota consegues consultar contratos, seguros, despesas e multas.
- [ ] Em Empilhadores consegues ver as afetações e o equipamento indisponível.
- [ ] Em Segurança, regista uma checklist com "Anomalia" e verifica que o aviso surge.
- [ ] Em Dados & Registos, edita uma data, guarda e exporta JSON.

**Dica importante:** a alteração feita no navegador não altera o GitHub. Quando recarregares uma nova sessão, os dados fictícios iniciais voltam a aparecer. Usa o botão **Exportar TODAS as tabelas (JSON)** para guardar alterações e **Importar backup JSON** para as recuperar.

## D. Para a candidatura

Publica o endereço da aplicação e, opcionalmente, o endereço do repositório.

Mensagem sugerida:

> Desenvolvi uma demonstração interativa de gestão de frota e equipamentos para PME, com 7 áreas funcionais, dashboards, indicadores de custos, alertas, workflows e um assistente agentic opcional. Pode experimentar sem instalação: [link Streamlit]. Código e arquitetura: [link GitHub]. Dados exclusivamente fictícios.

## E. Problemas comuns

- **`ModuleNotFoundError: No module named 'logic'`**: faltou carregar `logic.py` para a raiz do repositório.
- **`No module named 'data'`**: faltou carregar `data.py`.
- **Página com o aspeto antigo**: confirma que `app.py` foi substituído e que a última alteração está na branch usada pelo Streamlit.
- **Falha na IA**: não precisas dela para experimentar a demo. A IA só deve ser ativada quando tiveres configurado os Secrets e limites de utilização.
- **Campos alterados desapareceram**: dados só são guardados na sessão; exporta e importa um backup JSON.
