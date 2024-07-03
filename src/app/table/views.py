from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponseNotFound
from rest_framework import viewsets, mixins, status
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
        tables = get_list_or_404(models.Table)
        page = self.paginate_queryset(tables)

        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=(
                'pk', 'name', 'desc',))
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tables, many=True, fields=(
            'pk', 'name', 'desc',))
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        table = get_object_or_404(models.Table, pk=pk)
        serializer = self.get_serializer(table)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def full(self, request):
        table = get_object_or_404(models.Table, pk=request.data['pk'])
        return Response({'url': table.url})
    
    @action(detail=False, methods=['get'])
    def roll(self, request):
        entries = get_list_or_404(models.Table.objects.all().values('entries__text'), pk=request.data['pk'])
        if not entries:
            return HttpResponseNotFound()
        
        entry = services.get_random_entry(entries)
        return Response({'entry': entry['entries__text']})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        tables = get_list_or_404(models.Table, name__icontains=request.data['keyword'])
        if not tables: 
            return HttpResponseNotFound()
        
        page = self.paginate_queryset(tables)
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=(
                'pk', 'name', 'desc',))
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serialize(tables, many=True, fields=(
                'pk', 'name', 'desc',))
        return Response(serializer.data)


class EntryViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer


class TelegramChatViewSet(viewsets.ModelViewSet):
    queryset = models.TelegramChat.objects.all()
    serializer_class = serializers.TelegramChatSerializer

    @action(detail=False, methods=["get"])
    def favorites(self, request, *args, **kwargs):
        chat = models.TelegramChat.objects.\
            filter(chat_id=request.data['chat_id']).first()
            
        serializer = serializers.TableSerializer(
            chat.favorite_tables.all(), 
            many=True, 
            fields=(
                'pk',
                'name', 
                'desc',
        ))

        return Response(serializer.data)
            

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = models.Favorite.objects.all()
    serializer_class = serializers.FavoriteSerializer

    def create(self, request, *args, **kwargs):
        telegramchat, created = models.TelegramChat.objects.get_or_create(
            chat_id=request.data['telegramchat']
        )
        table = get_object_or_404(models.Table.objects.all(), pk=request.data['table']) 

        if not telegramchat.favorite_set.filter(table__pk=table.pk):
            serializer = self.get_serializer(
                data={
                    'telegramchat': telegramchat.pk, 
                    'table': table.pk
            })

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data)
        
        return HttpResponseNotFound()
    
    @action(detail=False, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(
            models.Favorite,
            telegramchat__chat_id=request.data['telegramchat'],
            table__pk=request.data['table']
        )
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
        