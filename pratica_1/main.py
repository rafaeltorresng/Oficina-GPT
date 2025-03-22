import os
import openai
import pandas as pd
import streamlit as st
import json
import altair as alt


# Função de Análise com GPT
def analyze_sentiment(review):
    prompt = f"""
    Analise o seguinte review e retorne:
    - Sentimento (Positivo, Neutro, Negativo)
    - Justificativa (máx. 10 palavras)
    - Tópicos-chave (ex: "preço", "qualidade")

    Formato de resposta (JSON):
    {{
        "sentimento": "...",
        "justificativa": "...",
        "topicos": ["..."]
    }}

    Review: {review}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        return {"sentimento": "Erro", "justificativa": str(e), "topicos": []}

# Interface do Streamlit 
st.set_page_config(page_title="Análise de Reviews com GPT", layout="wide")
st.title("📊 Dashboard Interativo de Análise de Sentimentos")

# Carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("../data/Reviews.csv") 
        return df[["Text", "Score"]].sample(20, random_state=42)
    except FileNotFoundError:
        st.error("Arquivo 'Reviews.csv' não encontrado na pasta 'data'!")
        return pd.DataFrame()

df = load_data()
if not df.empty:
    df.columns = ["review_text", "star_rating"] 

# Sidebar 
st.sidebar.header("Configurações")
st.sidebar.markdown("### Insira sua chave da OpenAI")
api_key = st.sidebar.text_input("Chave:", type="password")

if api_key:
    openai.api_key = api_key

# Botão para iniciar análise
if st.sidebar.button("Analisar Reviews") and not df.empty:
    resultados = []
    progress_bar = st.progress(0)
    
    for i, review in enumerate(df["review_text"]):
        resultado = analyze_sentiment(review)
        resultado["review"] = review 
        resultados.append(resultado)
        progress_bar.progress((i + 1) / len(df))
    
    st.session_state.resultados = pd.DataFrame(resultados)
    st.success("Análise concluída 🎉")

# Exibir resultados
if "resultados" in st.session_state:
    df_resultados = st.session_state.resultados
    
    # Métricas
    col1, col2, col3, col4= st.columns(4)
    col1.metric("📊 Total de Reviews", len(df_resultados))
    col2.metric("✅ Positivos", df_resultados[df_resultados["sentimento"] == "Positivo"].shape[0])
    col3.metric("❌ Negativos", df_resultados[df_resultados["sentimento"] == "Negativo"].shape[0])
    col4.metric("⚪ Neutros", df_resultados[df_resultados["sentimento"] == "Neutro"].shape[0]) 

    
    # Gráfico 
    st.subheader("Distribuição de Sentimentos")
    sentiment_counts = df_resultados["sentimento"].value_counts().reset_index()
    sentiment_counts.columns = ["sentimento", "count"]

    color_mapping = {
        "Positivo": "#90EE90",
        "Neutro": "#D3D3D3",
        "Negativo": "#FFCCCB"
    }

    chart = alt.Chart(sentiment_counts).mark_bar().encode(
        y='sentimento:N',
        x='count:Q',
        color=alt.Color('sentimento:N', 
                       scale=alt.Scale(
                           domain=list(color_mapping.keys()),
                           range=list(color_mapping.values())
                       ),
                       legend=None)
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)
    
    # Tabela interativa
    st.subheader("Análises Detalhadas")
    st.dataframe(
        df_resultados[["review", "sentimento", "justificativa", "topicos"]],
        column_config={
            "topicos": st.column_config.ListColumn("Tópicos", help="Tópicos identificados pelo GPT")
        },
        height=400
    )

    # Exportação p/ CSV
    if st.button("Exportar Resultados"):
        df_resultados.to_csv("analise_sentimentos.csv", index=False)
        st.success("Resultados exportados com sucesso!")