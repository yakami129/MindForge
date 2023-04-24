import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from model.gpt.ChatGptModel import ChatGPT
from .utils import BudiBaseOpenApiClient
from .utils import UUIDGenerator


@api_view(['POST'])
def execute_schema_task_chat(request):
    '''
      执行数据结果设计任务
    :param request:
    :return:
    '''
    data = json.loads(request.body.decode('utf-8'))
    chat = None
    try:
        chat_gpt = ChatGPT()  # 实例化 ChatGPT 对象
        chat = chat_gpt.execute_schema_task_chat(goal=data['goal'], task_name=data['taskName'],
                                                 task_goal=data['taskGoal'], task_thought=data['taskThought'])
    except Exception as e:
        print("chat error: %s" % str(e))
        chat = '发生系统错误，请稍后重试'
    return Response({"response": chat, "code": "200"})


@api_view(['GET'])
def start_goal_chat(request):
    """
       基于目标产生任务
    """
    prompt = request.GET.get("prompt")
    chat = None
    try:
        chat_gpt = ChatGPT()  # 实例化 ChatGPT 对象
        chat = chat_gpt.start_goal_chat(prompt=prompt)  # 调用 start_goal_chat 方法
    except Exception as e:
        # 记录错误日志或使用其他的错误处理方式
        chat = '发生系统错误，请稍后重试'
    return Response({"response": chat, "code": "200"})


@api_view(['POST'])
def create_application(request):
    """
     创建应用程序
    :param request:
    :return:
    """
    data = json.loads(request.body.decode('utf-8'))
    app_name = data["appName"]
    new_app_name = app_name + UUIDGenerator.generate()
    app_url = "/" + UUIDGenerator.generate() + "/" + app_name
    response = BudiBaseOpenApiClient.ApplicationClient.create(app_name=new_app_name, app_url=app_url)
    return Response({"response": response, "code": "200"})


@api_view(['POST'])
def create_table(request):
    """
     创建数据表
    :param request:
    :return:
    """
    data = json.loads(request.body.decode('utf-8'))
    schemas = data["schemas"]
    app_id = data["appId"]
    response_list = []
    for schema in schemas:
        response = BudiBaseOpenApiClient.TableClient.create(app_id=app_id, schema_obj=schema)
        response_list.append(response)
    return Response({"response": response_list, "code": "200"})
