import os
from openai import OpenAI
from db.beanie.models.models import MessageHistory

class GPTChat:

    def __init__(self, api_key, base_url, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.history = []  # История будет загружаться из MessageHistory

    async def load_history(self, parent_id):
        """Загружает историю чата из MessageHistory."""
        # Это пример, нужно заменить на реальный код загрузки
        self.history = await MessageHistory.get_dialog_history(parent_id)

    def load_prompt(self, prompt_path):
        """Считывает промпт из TXT-файла."""
        if not os.path.exists(prompt_path):
            print(f"Файл {prompt_path} не найден.")
            return None
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    async def chat(self, user_input, parent_id=None, prompt_path=None):
        """Отправляет сообщение в OpenAI и получает ответ."""
        # Загружаем историю, если parent_id передан
        if parent_id:
            await self.load_history(parent_id)

        # Если есть промпт, добавляем его в историю как системное сообщение
        if prompt_path:
            prompt = self.load_prompt(prompt_path)
            if prompt:
                self.history.append({"role": "system", "content": prompt})

        # Добавляем сообщение пользователя
        self.history.append({"role": "user", "content": user_input})

        # Отправляем запрос к GPT
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )

        # Получаем ответ от модели
        assistant_message = chat_completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_message})

        return assistant_message  # Просто возвращаем ответ модели