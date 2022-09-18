from django.contrib import admin
from .models import Folder, Document, Topic, FolderTopic, DocumentTopic

# Register your models here.
admin.site.register(Folder)
admin.site.register(Document)
admin.site.register(Topic)
admin.site.register(FolderTopic)
admin.site.register(DocumentTopic)
