from rest_framework.views import APIView
from rest_framework.response import Response
import os
import openai
from dotenv import load_dotenv
load_dotenv()  # 读取 .env 文件

class ChatGPT(APIView):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def chat(prompt):
        if not prompt:
            return Response({'error': 'Prompt is required.'}, status=400)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            n=1,
            stop=None
        )

        text = response.choices[0].text.strip()
        return text
