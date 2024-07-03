from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from core import models, serializers, services


class TablePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class TableViewSet(viewsets.ModelViewSet):
    queryset = models.Table.objects.all()
    serializer_class = serializers.TableSerializer

    def list(self, request, *args, **kwargs):
        queryset = models.Table.objects.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=(
                'pk',
                'name', 
                'desc',
            ))
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, fields=(
            'pk',
            'name', 
            'desc',
        ))
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = models.Table.objects.all()
        table = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(table)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def full(self, request):
        queryset = models.Table.objects.all()
        table = get_object_or_404(queryset, pk=request.data['pk'])
        return Response({'url': table.url})
    
    @action(detail=False, methods=['get'])
    def roll(self, request):
        entries = models.Table.objects.filter(pk=request.data['pk']).values('entries__text')
        if not entries:
            return HttpResponseNotFound()
        entry = services.get_random_entry(entries)
        return Response({'entry': entry['entries__text']})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = models.Table.objects.filter(name__icontains=request.data['keyword'])
        if not queryset: 
            return HttpResponseNotFound()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=(
                'pk',
                'name', 
                'desc',
            ))
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serialize(queryset, many=True, fields=(
            'pk',
            'name', 
            'desc',
        ))
        return Response(serializer.data)


class EntryViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer


class TelegramChatViewSet(viewsets.ModelViewSet):
    queryset = models.TelegramChat.objects.all()
    serializer_class = serializers.TelegramChatSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = models.Favorite.objects.all()
    serializer_class = serializers.FavoriteSerializer

    def create(self, request, *args, **kwargs):
        telegramchat, created = models.TelegramChat.objects.get_or_create(
            chat_id=request.data['telegramchat']
        )
        table = get_object_or_404(models.Table.objects.all(), pk=request.data['table']) 

        if not telegramchat.favorite_set.filter(table__pk=table.pk):
            serializer = serializers.FavoriteSerializer(
                data={
                    'telegramchat': telegramchat.pk, 
                    'table': table.pk
            })

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data)
        
        return HttpResponseNotFound()