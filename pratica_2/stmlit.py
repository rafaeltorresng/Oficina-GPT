import streamlit as st
from GPT_CLIENT import GPTClient
import os
from dotenv import load_dotenv


load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

gpt_client = GPTClient(OPEN_AI_KEY)

# Função para exibir mensagens do usuário e do chatbot
def display_messages(messages):
    for msg in messages:
        st.markdown(f"*{msg['user']}:* {msg['text']}")

# Função principal do aplicativo
def main():
    st.title("INTEGRANDO GPT COM PROJETO DE DADOS")

    # Armazenar as mensagens
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Caixa de texto para o usuário digitar a mensagem
    user_input = st.text_input("Digite sua mensagem:", "")

    if user_input:
        # Adicionar a mensagem do usuário à lista de mensagens
        st.session_state.messages.append({"user": "Você", "text": user_input})

        # Aqui você pode adicionar a lógica do GPT ou outro chatbot para gerar respostas
        # Exemplo de resposta automática:
        bot_response = gpt_client.call_gpt(user_input)

        # Adicionar a resposta do bot à lista de mensagens
        st.session_state.messages.append({"user": "Bot", "text": bot_response})

    # Exibir todas as mensagens (usuário e bot)
    display_messages(st.session_state.messages)

if __name__ == "_main_":
    main()