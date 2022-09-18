from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Folder, Document

# Create your tests here.
class TestCases(APITestCase):

    def create_folder(self, name, parent=None):
        data = {
            "name": name,
        }
        if parent is not None:
            data["parent"] = parent

        response = self.client.post("/api/folders", data)
        return response

    def TestCreateParentFolder(self):
        response = self.create_folder("parent folder")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Folder.objects.get().name, "parent folder")

    def TestCreateChildFolder(self):
        response = self.create_folder("child folder", parent=Folder.objects.get(name="parent folder").id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(Folder.objects.all())[1].name, 'child folder')
        self.assertEqual(list(Folder.objects.all())[1].parent.name, 'parent folder')

    def TestGetFolders(self):
        response = self.client.get("/api/folders")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                "id": 1,
                "name": "parent folder"
            },
            {
                "id": 2,
                "name": "child folder"
            }
        ])

    def TestGetOneFolder(self):
        response = self.client.get("/api/folders/2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["name"], "child folder")
        self.assertEqual(response.data["parent"], 1)

    def TestPatchFolder(self):
        data = {
            "name": "child folder - name changed"
        }
        response = self.client.patch("/api/folders/2", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["name"], "child folder - name changed")
        self.assertEqual(response.data["parent"], 1)

    def TestDeleteFolder(self):
        data = {
            "id": 2
        }
        response = self.client.delete("/api/folders", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Folder.objects.all()), 1)

    def TestCreateDocument(self, parent=None):
        data = {
            "name": "doc1",
        }
        if parent is not None:
            data["parent"] = parent

        response = self.client.post("/api/documents", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def TestGetDocuments(self):
        response = self.client.get("/api/documents")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                "id": 1,
                "name": "doc1"
            },
            {
                "id": 2,
                "name": "doc1"
            }
        ])

    def TestGetOneDocument(self):
        response = self.client.get("/api/documents/2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["name"], "doc1")
        self.assertEqual(response.data["parent"], 1)

    def TestPatchDocument(self):
        data = {
            "name": "doc2"
        }
        response = self.client.patch("/api/documents/2", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 2)
        self.assertEqual(response.data["name"], "doc2")
        self.assertEqual(response.data["parent"], 1)

    def TestDeleteDocument(self):
        data = {
            "id": 2
        }
        response = self.client.delete("/api/documents", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Folder.objects.all()), 1)

    def TestCreateTopic(self):
        data = {
            "name": "Alpha",
            "short_desc": "test short description"
        }

        response = self.client.post("/api/topics", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def TestGetTopics(self):
        response = self.client.get("/api/topics")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                "id": 1,
                "name": "Alpha"
            }
        ])

    def TestGetOneTopic(self):
        response = self.client.get("/api/topics/1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["name"], "Alpha")
        self.assertEqual(response.data["short_desc"], "test short description")
        self.assertEqual(response.data["long_desc"], "")

    def TestPatchTopic(self):
        data = {
            "long_desc": "test long description"
        }
        response = self.client.patch("/api/topics/1", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["name"], "Alpha")
        self.assertEqual(response.data["short_desc"], "test short description")
        self.assertEqual(response.data["long_desc"], "test long description")

    def TestDeleteTopic(self):
        data = {
            "id": 1
        }
        response = self.client.delete("/api/topics", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Folder.objects.all()), 0)

    def test_all(self):
        self.TestCreateParentFolder()
        self.TestCreateChildFolder()
        self.TestGetFolders()
        self.TestGetOneFolder()
        self.TestPatchFolder()
        self.TestDeleteFolder()

        self.TestCreateDocument()
        self.TestCreateDocument(1)
        self.TestGetDocuments()
        self.TestGetOneDocument()
        self.TestPatchDocument()
        self.TestDeleteDocument()

        self.TestCreateTopic()
        self.TestGetTopics()
        self.TestGetOneTopic()
        self.TestPatchTopic()
        self.TestDeleteTopic()
