import os
from openai import OpenAI
from db.beanie.models.models import MessageHistory
from typing import Optional

# Класс для общеня с GPT
class GPTChat:

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.history: list[dict[str, str]] = []  # История чата


    # Загружает историю чата из MessageHistory.
    async def load_history(self, parent_id: str) -> None:
        self.history = await MessageHistory.get_dialog_history(parent_id)


    # Читает промпт из TXT-файла
    def load_prompt(self, prompt_path: str) -> Optional[str]:
        if not os.path.exists(prompt_path):
            print(f"Файл {prompt_path} не найден.")
            return None
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()


    # Отправляет сообщение в OpenAI и получает ответ.
    async def chat(self, user_input: str, parent_id: Optional[str] = None, prompt_path: Optional[str] = None) -> str:
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