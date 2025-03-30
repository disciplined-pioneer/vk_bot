import os
from openai import OpenAI
from db.beanie.models.models import MessageHistory

class GPTChat:

    def __init__(self, api_key, base_url, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.history = []  # Путая история чата


    # Загружает историю чата из MessageHistory.
    async def load_history(self, parent_id):
        self.history = await MessageHistory.get_dialog_history(parent_id)


    # читывает промпт из TXT-файла
    def load_prompt(self, prompt_path):
        if not os.path.exists(prompt_path):
            print(f"Файл {prompt_path} не найден.")
            return None
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()


    # Отправляет сообщение в OpenAI и получает ответ.
    async def chat(self, user_input, parent_id=None, prompt_path=None):

        if parent_id:
            await self.load_history(parent_id)

        if prompt_path:
            prompt = self.load_prompt(prompt_path)
            if prompt:
                self.history.append({"role": "system", "content": prompt})

        self.history.append({"role": "user", "content": user_input})

        # Отправляем запрос к GPT
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )

        # Получаем ответ от модели
        assistant_message = chat_completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_message})

        return assistant_message