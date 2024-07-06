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
        tables = get_list_or_404(models.Table, author=None)
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
    
    @action(detail=True, methods=['get'])
    def show(self, request, pk=None):
        table = self.get_object()

        if table.url:
            return Response({'url': table.url})
        
        return Response({'url': 'It is your tables'})
    
    @action(detail=True, methods=['get'])
    def roll(self, request, pk=None):
        entries = get_list_or_404(models.Table.objects.all().values('entries__text'), pk=pk)
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
    
    @action(detail=False, methods=['post'])
    def create_custom_table(self, request):
        telegramchat, created = models.TelegramChat.objects.get_or_create(
            chat_id=request.data['telegramchat']
        )
        print(request.data)
        serializer = self.get_serializer(
            data={
                'author': telegramchat.pk,
                'name': request.data['name'],
                'desc': request.data['desc']
            }
        )

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def delete_custom_table(self, request):
        instance = get_object_or_404(
            models.Table,
            author__chat_id=request.data['telegramchat'],
            pk=request.data['table']
        )
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def list_custom_tables(self, request, *args, **kwargs):
        tables = get_list_or_404(models.Table, author__chat_id=request.data['telegramchat'])
        page = self.paginate_queryset(tables)

        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=(
                'pk', 'name', 'desc',))
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tables, many=True, fields=(
            'pk', 'name', 'desc',))
        return Response(serializer.data)


class EntryViewSet(viewsets.ModelViewSet):
    queryset = models.Entry.objects.all()
    serializer_class = serializers.EntrySerializer

    def create(self, request, *args, **kwargs):
        table = models.Table.objects.get(
            pk=request.data['table']
        )
        
        if table:
            serializer = self.get_serializer(
                data={
                    'table': table.pk,
                    'text': request.data['text']
                }
            )

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data)
        
        return HttpResponseNotFound()


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
        