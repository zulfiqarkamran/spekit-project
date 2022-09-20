from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

    @method_decorator(name='post', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def post(self, request):
        return create(request.data, Folder, self.serializer_class, check_parent=True)

    @method_decorator(name='get', decorator=swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    ))
    def get(self, request):
        return get_all(Folder)

    @method_decorator(name='delete', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={}
            )
        }
    ))
    def delete(self, request, format=None):
        return delete_one(request.data, Folder, has_parent=True)


class FolderDetailsView(APIView):
    serializer_class = FolderSerializer

    @method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Folder id whose details are required as output"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def get(self, request, id):
        return get_one(id, Folder, self.serializer_class)

    @method_decorator(name='patch', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Folder id whose details are to be modified"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'has_children': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def patch(self, request, id):
        return patch_record(request.data, id, Folder, self.serializer_class)


class DocumentView(APIView):
    serializer_class = DocumentSerializer

    @method_decorator(name='post', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'content': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def post(self, request):
        return create(request.data, Document, self.serializer_class, check_parent=True)

    @method_decorator(name='get', decorator=swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    ))
    def get(self, request):
        return get_all(Document)

    @method_decorator(name='delete', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={}
            )
        }
    ))
    def delete(self, request, format=None):
        return delete_one(request.data, Document, has_parent=True)


class DocumentDetailsView(APIView):
    serializer_class = DocumentSerializer

    @method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Document id whose details are required as output"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def get(self, request, id):
        return get_one(id, Document, self.serializer_class)

    @method_decorator(name='patch', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Document id whose details are to be modified"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                'content': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'parent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def patch(self, request, id):
        return patch_record(request.data, id, Document, self.serializer_class)


class TopicView(APIView):
    serializer_class = TopicSerializer

    @method_decorator(name='post', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'short_desc'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'short_desc': openapi.Schema(type=openapi.TYPE_STRING),
                'long_desc': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'short_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'long_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def post(self, request):
        return create(request.data, Topic, self.serializer_class)

    @method_decorator(name='get', decorator=swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    ))
    def get(self, request):
        return get_all(Topic)

    @method_decorator(name='delete', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={}
            )
        }
    ))
    def delete(self, request, format=None):
        return delete_one(request.data, Folder)


class TopicDetailsView(APIView):
    serializer_class = TopicSerializer

    @method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Topic id whose details are required as output"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'short_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'long_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def get(self, request, id):
        return get_one(id, Topic, self.serializer_class)

    @method_decorator(name='patch', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY,
                description=("Topic id whose details are to be modified"),
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'short_desc': openapi.Schema(type=openapi.TYPE_STRING),
                'long_desc': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'short_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'long_desc': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def patch(self, request, id):
        return patch_record(request.data, id, Topic, self.serializer_class)


class FolderTopicView(APIView):
    serializer_class = FolderTopicSerializer

    @method_decorator(name='post', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['folder', 'topic'],
            properties={
                'folder': openapi.Schema(type=openapi.TYPE_INTEGER),
                'topic': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'folder': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'topic': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def post(self, request):
        return create(request.data, FolderTopic, self.serializer_class)

    @method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'topic_name', openapi.IN_QUERY,
                description=("Topic name whose associated folders are required in the output"),
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    ))
    def get(self, request):
        topic_name = request.GET.get("topic_name", None)
        if topic_name is None:
            return Response([{"message": "Parameter 'topic_name' is required"}], status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        folder_topics = FolderTopic.objects.filter(topic=obj.id)
        id_set = []
        for folder_topic in folder_topics:
            id_set.append(folder_topic.folder.id)
        folders = Folder.objects.values("id", "name").filter(id__in=id_set)

        return Response(list(folders), status=status.HTTP_200_OK)


class DocumentTopicView(APIView):
    serializer_class = DocumentTopicSerializer

    @method_decorator(name='post', decorator=swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['document', 'topic'],
            properties={
                'document': openapi.Schema(type=openapi.TYPE_INTEGER),
                'topic': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'document': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'topic': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        }
    ))
    def post(self, request):
        return create(request.data, DocumentTopic, self.serializer_class)

    @method_decorator(name='get', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'topic_name', openapi.IN_QUERY,
                description=("Topic name whose associated documents are required in the output"),
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'folder_name', openapi.IN_QUERY,
                description=("Folder name whose documents are required in the output"),
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    ))
    def get(self, request):
        topic_name = request.GET.get("topic_name", None)
        if topic_name is None:
            return Response([{"message": "Parameter 'topic_name' is required"}], status=status.HTTP_400_BAD_REQUEST)

        try:
            topic_obj = Topic.objects.get(name=topic_name)
            folder_obj = None
            if request.GET.get("folder_name", None) is not None:
                folder_obj = Folder.objects.get(name=request.GET.get("folder_name"))
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
