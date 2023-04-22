from django.urls import path

from . import views

urlpatterns = [
    path('startGoalChat', views.start_goal_chat, name='startGoalChat'),
    path('executeSchemaTaskChat', views.execute_schema_task_chat, name='executeSchemaTaskChat'),
]
