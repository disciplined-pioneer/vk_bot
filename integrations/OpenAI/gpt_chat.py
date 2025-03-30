import os
from openai import OpenAI
from db.beanie.models.models import MessageHistoryPost, MessageHistoryPrivate
from typing import Optional

# Класс для общения с GPT
class GPTChat:

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o", source: str = "post"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.history: list[dict[str, str]] = []  # История чата
        self.source = source  # Источник истории


    # Загружает историю чата из MessageHistory.
    async def load_history(self, id_value: int) -> None:

        if self.source == "post":
            self.history = await MessageHistoryPost.get_dialog_history(id_value)
        elif self.source == "private":
            self.history = await MessageHistoryPrivate.get_dialog_history(id_value)
        else:
            raise ValueError("Invalid source specified. Use 'post' or 'private'.")


    # Читает промпт из TXT-файла
    def load_prompt(self, prompt_path: str) -> Optional[str]:
        if not os.path.exists(prompt_path):
            print(f"Файл {prompt_path} не найден.")
            return None
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()


    # Отправляет сообщение в OpenAI и получает ответ.
    async def chat(self, user_input: str, id_value: Optional[int] = None, prompt_path: Optional[str] = None) -> str:
        if id_value:
            await self.load_history(id_value)  # Загружаем историю в зависимости от source

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
