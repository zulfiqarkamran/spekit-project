# from django.urls import include, path
from django.urls import re_path, path
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from . import views


schema_view = get_swagger_view(title='Spekit API')

urlpatterns = [
    path('', schema_view),
    path('api/folders', views.FolderView.as_view()),
    path('api/folders/<int:id>', views.FolderDetailsView.as_view()),
    path('api/documents', views.DocumentView.as_view()),
    path('api/documents/<int:id>', views.DocumentDetailsView.as_view()),
    path('api/topics', views.TopicView.as_view()),
    path('api/topics/<int:id>', views.TopicDetailsView.as_view()),
    path('api/folder-topics', views.FolderTopicView.as_view()),
    path('api/document-topics', views.DocumentTopicView.as_view()),
]
