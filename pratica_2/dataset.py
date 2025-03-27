import pandas as pd


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

gender_translation = {
    'Male': 'Masculino',
    'Female': 'Feminino'
}

dados['genero'] = dados['genero'].map(gender_translation)


linha_produto_translation = {
    'Fashion accessories': 'Acessórios de Moda',
    'Food and beverages': 'Alimentos e Bebidas',
    'Electronic accessories': 'Acessórios Eletrônicos',
    'Sports and travel': 'Esportes e Viagens',
    'Home and lifestyle': 'Casa e Estilo de Vida',
    'Health and beauty': 'Saúde e Beleza'
}


dados['linha_produto'] = dados['linha_produto'].map(linha_produto_translation)


forma_pagamento_translation = {
    'Ewallet': 'Carteira Digital',
    'Cash': 'Dinheiro',
    'Credit card': 'Cartão de Crédito'
}
dados['forma_de_pagamento'] = dados['forma_de_pagamento'].map(forma_pagamento_translation)

tipo_cliente_translation = {
    'Member': 'Membro',
    'Normal': 'Normal'
}
dados['tipo_cliente'] = dados['tipo_cliente'].map(tipo_cliente_translation)