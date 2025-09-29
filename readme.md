# InvestiPro

InvestiPro é um aplicativo web desenvolvido com [Streamlit](https://streamlit.io/) para gerenciamento de carteiras de investimentos pessoais.

## Objetivo

Permitir que usuários cadastrem, visualizem e acompanhem seus investimentos, com autenticação segura e dashboards interativos.

## Funcionalidades

- **Cadastro de Usuário:** Crie um perfil com login e senha.
- **Gestão de Ativos:** Lance ativos como Ações, ETFs, FIIs, Renda Fixa e Tesouro Direto, informando valores pagos e detalhes.
- **Dashboard:** Visualize gráficos com a divisão percentual da carteira por tipo de ativo.

## Telas Principais

1. **Login/Cadastro:** Autenticação de usuários.
2. **Lançamento de Ativos:** Formulário para adicionar e editar ativos.
3. **Dashboard:** Gráficos e estatísticas da carteira.

## Tecnologias

- Python
- Streamlit
- SQLite (ou outro banco de dados leve)
- Bibliotecas de visualização (ex: Plotly, Matplotlib)

## Como usar

1. Clone este repositório.
2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o app:
    ```bash
    streamlit run app.py
    ```

## Próximos Passos

- Implementar autenticação de usuários.
- Criar modelos de dados para os ativos.
- Desenvolver telas de cadastro e dashboard.

---
Sinta-se à vontade para contribuir!