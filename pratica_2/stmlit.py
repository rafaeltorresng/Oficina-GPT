import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
from GPT_CLIENT import GPTClient
from dotenv import load_dotenv

load_dotenv()

# Carrega e trata os dados
@st.cache_data
def load_data():
    dados = pd.read_csv("../data/supermarket_sales.csv")
    
    colunas_rename = {
        'Invoice ID': 'id_fatura',
        'Branch': 'filial',
        'City': 'cidade',
        'Customer type': 'tipo_cliente',
        'Gender': 'genero',
        'Product line': 'linha_produto',
        'Unit price': 'preco_unitario',
        'Quantity': 'quantidade',
        'Tax 5%': 'imposto_5%',
        'Total': 'total',
        'Date': 'data',
        'Time': 'hora',
        'Payment': 'forma_de_pagamento',
        'cogs': 'custo_das_mercadorias_vendidas',
        'gross margin percentage': 'percentual_de_margem_bruta',
        'gross income': 'rendimento_bruto',
        'Rating': 'avaliacao'
    }
    dados.rename(columns=colunas_rename, inplace=True)
    
    traducoes = {
        'genero': {'Male': 'Masculino', 'Female': 'Feminino'},
        'linha_produto': {
            'Fashion accessories': 'Acessórios de Moda',
            'Food and beverages': 'Alimentos e Bebidas',
            'Electronic accessories': 'Acessórios Eletrônicos',
            'Sports and travel': 'Esportes e Viagens',
            'Home and lifestyle': 'Casa e Estilo de Vida',
            'Health and beauty': 'Saúde e Beleza'
        },
        'forma_de_pagamento': {
            'Ewallet': 'Carteira Digital', 
            'Cash': 'Dinheiro', 
            'Credit card': 'Cartão de Crédito'
        },
        'tipo_cliente': {'Member': 'Membro', 'Normal': 'Normal'}
    }
    
    for col, trad in traducoes.items():
        dados[col] = dados[col].map(trad)
    
    return dados

dados = load_data()

# Função para execução segura de código gerado pelo GPT (para gráficos)
def execute_safe_code(code: str):
    try:
        allowed_vars = {
            'dados': dados,
            'px': px,
            'pd': pd,
            'st': st,
            'sum': sum,
            'mean': pd.Series.mean
        }
        exec(code, allowed_vars)
        # Se o código gerar um gráfico, espera que a variável 'fig' esteja definida;
        # caso contrário, se definir 'resultado', retornamos esse valor.
        return allowed_vars.get('fig') or allowed_vars.get('resultado')
    except Exception as e:
        st.error(f"Erro na execução: {str(e)}")
        return None

# Inicializa o GPTClient na sessão
if 'gpt_client' not in st.session_state:
    st.session_state.gpt_client = GPTClient(api_key=os.getenv('OPEN_AI_KEY'))

st.title("📊 Analisador de Vendas Inteligente")

user_input = st.chat_input("Faça sua pergunta sobre as vendas:")

if user_input:
    # Verifica se a pergunta é de cálculo, por exemplo, receita de um ano específico
    calc_match = re.search(r'receita.*?(\d{4})', user_input.lower())
    if calc_match:
        year = int(calc_match.group(1))
        # Converte a coluna 'data' usando o formato correto (m/d/YYYY)
        dados['data'] = pd.to_datetime(dados['data'], format='%m/%d/%Y')
        dados_year = dados[dados['data'].dt.year == year]
        receita = dados_year['total'].sum()
        st.write(f"A receita de {year} é: R$ {receita:.2f}")
    else:
        # Se a consulta não for de cálculo, encaminha para o GPT
        response = st.session_state.gpt_client.call_gpt(system_prompt="", question=user_input)
        
        # Se a resposta contém código (indicando um gráfico), executa-o; caso contrário, exibe o texto
        code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
        if code_blocks:
            code = code_blocks[0].strip()
            result = execute_safe_code(code)
            if isinstance(result, (str, float, int)):
                st.write(result)
            elif result is not None:
                st.plotly_chart(result)
        else:
            st.write(response)
