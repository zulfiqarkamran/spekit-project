# from django.urls import include, path
from django.urls import re_path, path
from rest_framework import routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

from . import views


schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Spekit API",
        default_version='1.0.0',
        description="API documentation of Spekit App",
    ),
    public=True,
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema"),
    path('api/folders', views.FolderView.as_view()),
    path('api/folders/<int:id>', views.FolderDetailsView.as_view()),
    path('api/documents', views.DocumentView.as_view()),
    path('api/documents/<int:id>', views.DocumentDetailsView.as_view()),
    path('api/topics', views.TopicView.as_view()),
    path('api/topics/<int:id>', views.TopicDetailsView.as_view()),
    path('api/folder-topics', views.FolderTopicView.as_view()),
    path('api/document-topics', views.DocumentTopicView.as_view()),
]
