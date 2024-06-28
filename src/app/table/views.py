from rest_framework import viewsets

from core import models, serializers


class TableViewSet(viewsets.ModelViewSet):
    queryset = models.Table.objects.all()
    serializer_class = serializers.TableSerializer


class EntryViewSet(viewsets.ModelViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
