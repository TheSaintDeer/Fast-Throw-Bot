from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from core import models, serializers, services


class TableViewSet(viewsets.ModelViewSet):
    queryset = models.Table.objects.all()
    serializer_class = serializers.TableSerializer

    def list(self, request, *args, **kwargs):
        queryset = models.Table.objects.all()
        serializer = serializers.TableSerializer(queryset, many=True, fields=(
            'pk',
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
    
    @action(detail=False, methods=['get'])
    def full(self, request):
        table = models.Table.objects.get(name=request.data['name'])
        return Response({'url': table.url})
    
    @action(detail=False, methods=['get'])
    def roll(self, request):
        entries = models.Table.objects.filter(name=request.data['name']).values('entries__text')
        entry = services.get_random_entry(entries)
        return Response({'entry': entry['entries__text']})


class EntryViewSet(viewsets.ModelViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    @action(detail=False, methods=['get'])
    def search_by_tags(self, request):
        tag = models.Tag.objects.get(name=request.data['name'])
        serializer = serializers.TableSerializer(tag.table_set.all(), many=True, fields=(
            'pk',
            'name', 
            'desc',
        ))
        return Response(serializer.data)
