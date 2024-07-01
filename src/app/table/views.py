from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from core import models, serializers


class TableViewSet(viewsets.ModelViewSet):
    queryset = models.Table.objects.all()
    serializer_class = serializers.TableSerializer

    def list(self, request, *args, **kwargs):
        queryset = models.Table.objects.all()
        serializer = serializers.TableSerializer(queryset, many=True, fields=(
            'name', 
            'desc',
            'tags', 
        ))
        return Response(serializer.data)

    
    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = models.Table.objects.all()
        table = get_object_or_404(queryset, pk=pk)
        serializer = serializers.TableSerializer(table)
        return Response(serializer.data)


class EntryViewSet(viewsets.ModelViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
