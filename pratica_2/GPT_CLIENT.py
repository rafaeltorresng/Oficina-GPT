import openai
from dotenv import load_dotenv
import os

load_dotenv()

class GPTClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPEN_AI_KEY')
        openai.api_key = self.api_key
        self.history = []

    def call_gpt(self, system_prompt: str, question: str) -> str:
        full_system_prompt = """

        [TASK]
        Você é um assistente de análise de dados para um chatbot integrado ao Streamlit que responde perguntas sobre um dataset de vendas de supermercado.
        - Se a pergunta exigir um cálculo simples (por exemplo, “Qual a receita de 2019?”), retorne apenas o resultado final de forma objetiva e concisa, como: “A receita de 2019 é: R$ 123456.78”.
        - Se a pergunta exigir a geração de um gráfico (com termos como “gráfico”, “plotar”, “visualizar”), retorne somente o código Python necessário – utilizando Plotly para Streamlit – para gerar o gráfico.
        - Responda apenas com o resultado final ou com o código necessário, sem revelar nenhum detalhe do seu processamento interno.

        [CONTEXT]
        Você tem acesso a um dataset de vendas de supermercado já carregado e processado. As principais colunas são:
        - "data": datas no formato "m/d/YYYY"
        - "total": valor total de cada venda
        - Outras colunas: "filial", "cidade", "genero", "linha_produto", etc.
        O usuário pode solicitar informações numéricas (como somas e médias) ou visualizações (gráficos de barras, linhas etc.). Você não deve revelar nenhum detalhe sobre como o cálculo ou a visualização é realizado internamente.

        [REFERENCES]
        Exemplo 1: Consulta Numérica:
        Input: "Qual a receita de 2019?"
        Output: "A receita de 2019 é: R$ 123456.78"

        Exemplo 2: Consulta de Gráfico:
        Input: "Mostre um gráfico de barras comparando as receitas das filiais."
        Output (Código Python):
        ```python
        # [INÍCIO DO CÓDIGO STREAMLIT]
        import plotly.express as px
        import pandas as pd

        dados_filtrados = dados.groupby('filial', as_index=False)['total'].sum()

        fig = px.bar(
            dados_filtrados,
            x='filial',
            y='total',
            title='Receita por Filial',
            labels={'filial': 'Filial', 'total': 'Receita'}
        )

        st.plotly_chart(fig, use_container_width=True)
        # [FIM DO CÓDIGO STREAMLIT]
        Não revele detalhes internos de seu processo de análise. Responda apenas com o resultado final ou com o código necessário para gerar o gráfico, conforme o tipo de pergunta.
 """

        messages = [ {"role": "system", "content": full_system_prompt}, *self.history, {"role": "user", "content": question} ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3
            )
            response_content = response.choices[0].message.content.strip()
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": response_content})
            return response_content

        except Exception as e:
            print(f"Erro ao chamar GPT: {e}")
            return "Desculpe, ocorreu um erro."
