from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
import os
api_key=os.environ.get("OPENAI_API_KEY")
class OpenAIAPI:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)

    def get_classification(self, user_input):
        has_number = any(char.isdigit() for char in user_input)

        if not has_number:
            return "請輸入包含價格的產品資訊，以便進行記帳。"
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個記帳程式 幫我歸類 食、衣、住、行、育、樂 我接下來要輸入的產品類別 跟價格 如果我沒有指定 你就自己幫我分類 回復格式: 類別 品項名 價格 如果有多筆要換行 請嚴格遵守格式 就是每一項品項就三個欄位 不要自己家東西 ex 食 御飯糰 50"},
                {"role": "user", "content": user_input}
            ]
        )

        # 解析 OpenAI 的回傳，這裡只取第一個 message 的 content
        openai_response = completion.choices[0].message.content
        print(openai_response)
        return openai_response