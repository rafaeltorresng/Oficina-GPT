import pandas as pd
import pytz
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class SupermarketAnalytics:
    def __init__(self, data_path: str):
        self.dados = self._load_and_prepare_data(data_path)
        self.gpt_client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))
        self.current_datetime = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
    def _load_and_prepare_data(self, path: str) -> pd.DataFrame:
        """Carrega e prepara os dados do supermercado"""
        dados = pd.read_csv(path)
        
        # Tradução de colunas
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
            'cogs': 'custo_mercadorias',
            'gross margin percentage': 'margem_bruta_percentual',
            'gross income': 'renda_bruta'
        }
        dados = dados.rename(columns=colunas_rename)
        
        # Tradução de valores categóricos
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
            'tipo_cliente': {
                'Member': 'Membro',
                'Normal': 'Normal'
            }
        }
        
        for col, mapeamento in traducoes.items():
            dados[col] = dados[col].map(mapeamento)
            
        # Converter data para datetime
        dados['data_datetime'] = pd.to_datetime(dados['data'], format='%m/%d/%Y')
        
        return dados

    def _get_date_filters(self) -> Dict[str, str]:
        """Retorna filtros de data pré-definidos"""
        return {
            'hoje': self.current_datetime.strftime('%d/%m/%Y'),
            'ontem': (self.current_datetime - timedelta(days=1)).strftime('%d/%m/%Y'),
            'mes_atual': self.current_datetime.strftime('%m'),
            'ano_atual': self.current_datetime.strftime('%Y')
        }

    def generate_query(self, user_prompt: str) -> str:
        """Gera a query pandas baseada na pergunta do usuário"""
        date_filters = self._get_date_filters()
        
        columns_description = {
            'id_fatura': "Identificador único da transação",
            'filial': "Filial (A, B ou C)",
            'cidade': "Cidade da filial",
            'tipo_cliente': "Tipo de cliente (Membro ou Normal)",
            'genero': "Gênero do cliente",
            'linha_produto': "Categoria do produto (já traduzida)",
            'preco_unitario': "Preço unitário do produto",
            'quantidade': "Quantidade vendida",
            'total': "Valor total da venda (já com impostos)",
            'data': "Data no formato dd/mm/aaaa",
            'data_datetime': "Data como datetime para operações temporais",
            'forma_de_pagamento': "Método de pagamento (já traduzido)"
        }
        
        prompt = f"""
        Você é um assistente de análise de dados para um supermercado. 
        Data atual: {self.current_datetime.strftime('%d/%m/%Y %H:%M:%S')}
        
        ### ESTRUTURA DO DATAFRAME (dados):
        {pd.DataFrame(columns_description.items(), columns=['Coluna', 'Descrição']).to_markdown()}
        
        ### REGRAS PARA GERAÇÃO DE QUERIES:
        1. Use APENAS as colunas existentes listadas acima
        2. Para filtros temporais:
           - Hoje: {date_filters['hoje']}
           - Ontem: {date_filters['ontem']}
           - Mês atual: {date_filters['mes_atual']}
           - Ano atual: {date_filters['ano_atual']}
        3. Sempre retorne o resultado na variável `result`
        4. Para agregações use .groupby() + .agg()
        5. Para ordenação use .sort_values()
        
        ### EXEMPLOS:
        1. "Quais produtos mais vendidos em janeiro":
        result = (
            dados[dados['data_datetime'].dt.month == 1]
            .groupby('linha_produto')['quantidade']
            .sum()
            .sort_values(ascending=False)
        )
        
        2. "Faturamento por filial":
        result = (
            dados.groupby('filial')['total']
            .sum()
            .sort_values(ascending=False)
        )
        
        3. "Vendas por método de pagamento":
        result = (
            dados.groupby('forma_de_pagamento')['total']
            .sum()
            .sort_values(ascending=False)
        )
        
        Gere APENAS o código Python para a pergunta: "{user_prompt}"
        """
        
        response = self.gpt_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3
        )
        
        query = response.choices[0].message.content
        logging.info(f"Query gerada: {query}")
        return query

    def humanize_response(self, question: str, query_result) -> str:
        """Transforma resultados de queries em respostas humanizadas"""
        prompt = f"""
        Você é um assistente amigável de um supermercado. 
        Data atual: {self.current_datetime.strftime('%d/%m/%Y %H:%M:%S')}
        
        ### CONTEXTO:
        - Pergunta do usuário: "{question}"
        - Resultado da análise: {str(query_result)}
        
        ### DIRETRIZES:
        1. Seja claro e conciso
        2. Formate valores monetários como "R$ X.XXX,XX"
        3. Para listas, mostre os principais itens
        4. Se o resultado for vazio: "Não encontrei dados para esta consulta"
        5. Destaque insights relevantes
        6. Nunca mostre código ou queries
        7. Use emojis quando apropriado (💰, 📊, 🛒)
        
        ### EXEMPLOS:
        1. Para resultado 1500.50:
        "O total foi de R$ 1.500,50"
        
        2. Para série pandas:
        "Os produtos mais vendidos foram:
        - Acessórios Eletrônicos: 120 unidades
        - Alimentos e Bebidas: 95 unidades"
        
        3. Para DataFrame:
        "Aqui está o resumo por filial:
        - Filial A: R$ 5.200,00
        - Filial B: R$ 4.800,00"
        
        Agora, gere a resposta para o resultado acima:
        """
        
        response = self.gpt_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def analyze(self, user_prompt: str):
        """Fluxo completo de análise"""
        try:
            # Passo 1: Gerar query
            query = self.generate_query(user_prompt)
            
            # Passo 2: Executar query
            local_vars = {'dados': self.dados, 'result': None}
            exec(query, globals(), local_vars)
            result = local_vars['result']
            
            # Passo 3: Humanizar resposta
            return self.humanize_response(user_prompt, result)
            
        except Exception as e:
            logging.error(f"Erro na análise: {str(e)}")
            return "Ops, ocorreu um erro ao processar sua solicitação. Poderia reformular a pergunta?"