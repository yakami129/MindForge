from rest_framework.response import Response
from rest_framework.views import APIView
from model.gpt.ChatGptModel import ChatGPT


class ChatGPTView(APIView):
    """
     GPT聊天
    """

    def get(self, request):
        prompt = request.GET.get("prompt")
        chat = None
        try:
            chat = ChatGPT.chat(prompt)
        except Exception as e:
            print("chat error: %s" % str(e))
            chat = '发生系统错误，请稍后重试'

        return Response({"response": chat})
