from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import FolderSerializer, DocumentSerializer, TopicSerializer, FolderTopicSerializer, DocumentTopicSerializer
from .models import Folder, Document, Topic, FolderTopic, DocumentTopic


def create(data, model, serializer_class, check_parent=False):
    ser = serializer_class(data=data)

    if model == Folder or model == Document:
        if data.get('parent') is None:
            check_name = model.objects.filter(name=data.get('name'), parent=None)
            if len(check_name) > 0:
                return Response([{"message": "Name duplication not allowed"}], status=status.HTTP_400_BAD_REQUEST)

    if ser.is_valid():
        ser.save()

        if check_parent and data.get('parent') is not None:
            parent = Folder.objects.get(id=data.get('parent'))
            parent.has_children = True
            parent.save()

        return Response(ser.data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

def get_all(model):
    data = model.objects.values("id", "name")
    # serializer = serializer_class(data, many=True)

    return Response(list(data), status=status.HTTP_200_OK)

def get_one(id, model, serializer_class):
    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = serializer_class(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)

def delete_one(data, model, has_parent=False):
    try:
        obj = model.objects.get(id=data.get('id'))
    except model.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if has_parent:
        parent = obj.parent

    obj.delete()

    if has_parent and parent is not None:
        subfolders = Folder.objects.filter(parent=parent.id)
        files = Document.objects.filter(parent=parent.id)
        if len(subfolders) == 0 and len(files) == 0:
            parent.has_children = False
            parent.save()

    return Response({}, status=status.HTTP_200_OK)

def patch_record(data, id, model, serializer_class):
    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = serializer_class(obj, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
class FolderView(APIView):
    serializer_class = FolderSerializer

    def post(self, request):
        """
        {
            "name": <required>
            "parent": <optional> <add this for folder nesting>
            "has_children" <optional> <this will get updated automatically if a child is added to the folder>
        }
        """
        return create(request.data, Folder, self.serializer_class, check_parent=True)

    def get(self, request):
        return get_all(Folder)

    def delete(self, request, format=None):
        """
        {
            "id": <required> <id of folder to be deleted>
        }
        """
        return delete_one(request.data, Folder, has_parent=True)


class FolderDetailsView(APIView):
    serializer_class = FolderSerializer

    def get(self, request, id):
        return get_one(id, Folder, self.serializer_class)

    def patch(self, request, id):
        """
        Data to be edited for folder corresponding to "id"
        {
            "name": <optional>
            "parent": <optional>
            "has_children" <optional>
        }
        """
        return patch_record(request.data, id, Folder, self.serializer_class)


class DocumentView(APIView):
    serializer_class = DocumentSerializer

    def post(self, request):
        """
        {
            "name": <required>
            "parent": <optional> <add this for folder nesting>
            "content" <optional> <if not added, defaults to an empty string>
        }
        """
        return create(request.data, Document, self.serializer_class, check_parent=True)

    def get(self, request):
        return get_all(Document)

    def delete(self, request, format=None):
        """
        {
            "id": <required> <id of document to be deleted>
        }
        """
        return delete_one(request.data, Document, has_parent=True)


class DocumentDetailsView(APIView):
    serializer_class = DocumentSerializer

    def get(self, request, id):
        return get_one(id, Document, self.serializer_class)

    def patch(self, request, id):
        """
        Data to be edited for document corresponding to "id"
        {
            "name": <optional>
            "parent": <optional>
            "content" <optional>
        }
        """
        return patch_record(request.data, id, Document, self.serializer_class)


class TopicView(APIView):
    serializer_class = TopicSerializer

    def post(self, request):
        """
        {
            "name": <required>
            "short_desc": <required>
            "long_desc" <optional> <if not added, defaults to an empty string>
        }
        """
        return create(request.data, Topic, self.serializer_class)

    def get(self, request):
        return get_all(Topic)

    def delete(self, request, format=None):
        """
        {
            "id": <required> <id of topic to be deleted>
        }
        """
        return delete_one(request.data, Folder)


class TopicDetailsView(APIView):
    serializer_class = TopicSerializer

    def get(self, request, id):
        return get_one(id, Topic, self.serializer_class)

    def patch(self, request, id):
        """
        Data to be edited for topic corresponding to "id"
        {
            "name": <optional>
            "short_desc": <optional>
            "long_desc" <optional>
        }
        """
        return patch_record(request.data, id, Topic, self.serializer_class)


class FolderTopicView(APIView):
    serializer_class = FolderTopicSerializer

    def post(self, request):
        """
        {
            "folder": <required> <id of folder>
            "topic": <required> <id of topic>
        }
        """
        return create(request.data, FolderTopic, self.serializer_class)

    def get(self, request):
        """
        Returns folders against a topic name

        {
            "name": <required>
        }
        """
        try:
            obj = Topic.objects.get(name=request.data["name"])
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        folder_topics = FolderTopic.objects.filter(topic=obj.id)
        id_set = []
        for folder_topic in folder_topics:
            id_set.append(folder_topic.folder.id)
        folders = Folder.objects.values("id", "name").filter(id__in=id_set)

        return Response(list(folders), status=status.HTTP_200_OK)


class DocumentTopicView(APIView):
    serializer_class = DocumentSerializer

    def post(self, request):
        """
        {
            "document": <required> <id of document>
            "topic": <required> <id of topic>
        }
        """
        return create(request.data, DocumentTopic, self.serializer_class)

    def get(self, request):
        """
        Returns documents against a topic name. Can also return the documents inside a folder against a topic name

        {
            "topic_name": <required>
            "folder_name" <optional>
        }
        """
        try:
            topic_obj = Topic.objects.get(name=request.data["topic_name"])
            folder_obj = None
            if request.data.get("folder_name", None) is not None:
                folder_obj = Folder.objects.get(name=request.data["folder_name"])
        except (Topic.DoesNotExist, Folder.DoesNotExist) as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        document_topics = DocumentTopic.objects.filter(topic=topic_obj.id)
        id_set = []
        for document_topic in document_topics:
            id_set.append(document_topic.document.id)
        if folder_obj:
            documents = Document.objects.values("id", "name").filter(id__in=id_set, parent=folder_obj.id)
        else:
            documents = Document.objects.values("id", "name").filter(id__in=id_set)

        return Response(list(documents), status=status.HTTP_200_OK)
