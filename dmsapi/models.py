from django.db import models

# Create your models here.
class Folder(models.Model):
    name = models.CharField(max_length=30, null=False)
    parent = models.ForeignKey('self', default=None, blank=True, null=True, on_delete=models.CASCADE)
    has_children = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)
        unique_together = ('name', 'parent',)

    def __str__(self):
        return self.name

class Document(models.Model):
    name = models.CharField(max_length=30, null=False)
    parent = models.ForeignKey(Folder, default=None, blank=True, null=True, on_delete=models.CASCADE)
    content = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)
        unique_together = ('name', 'parent',)

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=30, null=False, unique=True)
    short_desc = models.CharField(max_length=60, null=False)
    long_desc = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

class FolderTopic(models.Model):
    folder = models.ForeignKey(Folder, null=False, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('folder', '-topic',)
        unique_together = ('folder', 'topic',)

    def __str__(self):
        return str(self.folder.id) + " " + str(self.topic.id)

class DocumentTopic(models.Model):
    document = models.ForeignKey(Document, null=False, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('document', '-topic',)
        unique_together = ('document', 'topic',)

    def __str__(self):
        return str(self.document.id) + " " + str(self.topic.id)
