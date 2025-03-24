import openai
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class GPTClient:
    def _init_(self, api_key: str = None):
        """
        Inicializa o cliente do GPT e o histórico da conversa.
        Se a chave não for fornecida, é lida a partir da variável de ambiente 'OPEN_AI_KEY'.
        """
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv('OPEN_AI_KEY')
        
        # Inicia o histórico como vazio
        self.history = []

        self.prompt = """
                
            """

    def call_gpt(self, prompt: str, question: str) -> str:
        """
        Recebe um prompt (contexto dinâmico), o histórico da conversa e a pergunta atual.
        Monta a mensagem a ser enviada à API do GPT e atualiza o histórico com a interação.

        Parâmetros:
            prompt (str): Contexto ou explicação para a conversa (dinâmico a cada chamada).
            question (str): Pergunta atual a ser respondida.
        
        Retorna:
            str: Resposta gerada pelo GPT.
        """
        # Mensagem do sistema: inclui o contexto e uma indicação de que segue o histórico anterior.
        system_message = {
            "role": "system",
            "content": prompt + " Historico anterior do usuário: "
        }
        # Mensagem do usuário: formata a pergunta atual.
        user_message = {
            "role": "user",
            "content": "Pergunta atual, a ser respondida: " + question
        }
        
        # Monta a lista completa de mensagens: prompt, histórico acumulado e a pergunta atual.
        messages = [system_message] + self.history + [user_message]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                temperature=0.3,
                messages=messages
            )
            response_content = response['choices'][0]['message']['content']
            # Remove eventuais marcações de código indesejadas
            response_content = response_content.replace('```', '').replace('python', '')
            
            # Atualiza o histórico com a pergunta e a resposta
            self.history.append(user_message)
            self.history.append({"role": "assistant", "content": response_content})
            
            return response_content
        except Exception as e:
            print(f"Erro ao chamar GPT: {e}")
            return "Desculpe, não consegui processar sua solicitação no momento."