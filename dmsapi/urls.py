# from django.urls import include, path
from django.urls import re_path, path
from rest_framework import routers

from . import views


urlpatterns = [
    path('api/folders', views.FolderView.as_view()),
    path('api/folders/<int:id>', views.FolderDetailsView.as_view()),
    path('api/documents', views.DocumentView.as_view()),
    path('api/documents/<int:id>', views.DocumentDetailsView.as_view()),
    path('api/topics', views.TopicView.as_view()),
    path('api/topics/<int:id>', views.TopicDetailsView.as_view()),
    path('api/folder-topics', views.FolderTopicView.as_view()),
    path('api/document-topics', views.DocumentTopicView.as_view()),
]
