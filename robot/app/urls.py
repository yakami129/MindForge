from django.urls import re_path
from .views import ChatGPTView

urlpatterns = [
    re_path(r'^', ChatGPTView.as_view()),
]
