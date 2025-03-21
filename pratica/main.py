import openai


class GPTClient:
    def _init_(self, api_key: str, number: str):
        self.client = OpenAI(api_key=api_key)
        self.history = self.get_history(number)

    def call_gpt(self, prompt: str, question: str) -> str:
        messages = [{"role": "system", "content": prompt + "Historico anterior do usuário: "}] + self.history + [{"role": "user", "content": "Pergunta atual, a ser respondida: " + question}]
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.3,
                seed=42,
                messages=messages
            )
            response_content = response.choices[0].message.content
            response_content = response_content.replace('```', '').replace('python', '')
            return response_content
        except Exception as e:
            logger.error(f"Erro ao chamar GPT: {e}")
            return "Desculpe, não consegui processar sua solicitação no momento."
