import streamlit as st
from GPT_CLIENT import SupermarketAnalytics
import time

# Configuração inicial
st.set_page_config(page_title="Analytics Supermercado", layout="wide")
st.title("📊 Painel de Análise de Vendas")

# Inicialização do sistema
@st.cache_resource
def init_analytics():
    return SupermarketAnalytics("../data/supermarket_sales.csv")

analytics = init_analytics()

# Histórico de conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input do usuário
user_input = st.chat_input("Faça sua pergunta sobre vendas...")

if user_input:
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Processa a pergunta
    with st.spinner("Analisando dados..."):
        start_time = time.time()
        response = analytics.analyze(user_input)
        elapsed = time.time() - start_time
    
    # Adiciona resposta ao histórico
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "time": f"{elapsed:.2f}s"
    })

# Exibe histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            st.caption(f"Processado em {msg['time']}")