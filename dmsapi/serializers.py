from rest_framework import serializers
from .models import Folder, Document, Topic, FolderTopic, DocumentTopic


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"

class FolderTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderTopic
        fields = "__all__"

class DocumentTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTopic
        fields = "__all__"