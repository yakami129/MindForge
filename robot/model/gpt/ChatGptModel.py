from rest_framework.views import APIView
from rest_framework.response import Response
from dotenv import load_dotenv
import os
import openai
import json

load_dotenv()  # 读取 .env 文件


class ChatGPT(APIView):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def chat(self, prompt):
        if not prompt:
            return Response({'error': 'Prompt is required.'}, status=400)

        # response = openai.Completion.create(
        #     model="gpt-3.5-turbo",
        #     prompt=prompt,
        #     temperature=0.5,
        #     max_tokens=1024,
        #     n=1,
        #     stop=None
        # )

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = completion.choices[0].message.content
        return text

    def start_goal_chat(self, prompt):
        start_goal_prompt = ChatGPTPrompt.start_goal_prompt(self=self, goal=prompt)
        result = ChatGPT.chat(self=self, prompt=start_goal_prompt)
        result = ChatGPT.format_result(result)
        result_object = json.loads(result)
        return result_object

    def execute_schema_task_chat(self, goal, task_name, task_goal, task_hought):
        schema_task_prompt = ChatGPTPrompt.execute_schema_task_prompt(self=self, goal=goal, task_name=task_name,
                                                                      task_goal=task_goal,
                                                                      task_hought=task_hought)
        result = ChatGPT.chat(self=self, prompt=schema_task_prompt)
        result = ChatGPT.format_result(result)
        result_object = json.loads(result)
        return result_object

    def format_result(str):
        start_index = str.find("$START") + len("$START")
        end_index = str.find("$END")
        result = str[start_index:end_index]
        return result


class ChatGPTPrompt:

    def start_goal_prompt(self, goal):
        query_prompt_str = "你现在是一个名为 MindForgGPT 的自主任务创建 AI。 您有以下目标 `{0}`。请按照数据结构设计，页面设计去分类, 每个分类可以创建一个包含 0 到 3 个任务的列表，你无需完成它，只输出任务名称，任务目标和实现思路，以便更接近或完全达到您的目标你的输出格式"
        out_put_prompt_str = "$START{\"query\":\"我提出的目标\",\"appName\":\"根据我提出的目标生成appName\",\"schema\":[{\"taskName\":\"你生成的数据结构设计任务名称\",\"taskGoal\":\"你生成的数据结构设计任务目标\",\"taskHought\":\"你生成的数据结构设计任务思路\"}],\"view\":[{\"taskName\":\"你生成的页面设计任务名称\",\"taskGoal\":\"你生成的页面设计任务目标\",\"taskHought\":\"你生成的页面设计任务思路\"}]}$END"
        start_goal_prompt_str = query_prompt_str.format(goal) + out_put_prompt_str
        return start_goal_prompt_str

    def execute_schema_task_prompt(self, goal, task_name, task_goal, task_hought):
        query_prompt_str = "你现在是一个名为 MindForgSchemaGPT 的数据结构设计 AI。 您有以下目标 `{0}`,您的任务为`{1}`，目标为`{2}`,思路为`{3}`,如果有多个数据实体，请输出多个数据实体,如果是多个数据实体，请在当前输出数组中累加新的元素，请严格按照输出格式输出内容，输出格式如下"
        out_put_prompt_str = "$START[{\"schema\":\"你生成的数据实体名称用英语\",\"columns\":[{\"name\":\"你生成的字段名称用英语\",\"type\":\"你生成的字段类型（使用mysql的数据类型）\",\"description\":\"你生成的字段描述\"}]}//如果有多个数据实体，请在此处添加新的数据实体]$END"
        start_goal_prompt_str = query_prompt_str.format(goal, task_name, task_goal, task_hought) + out_put_prompt_str
        return start_goal_prompt_str
