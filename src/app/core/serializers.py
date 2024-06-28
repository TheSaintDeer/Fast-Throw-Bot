from rest_framework import serializers

from . import models


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['name']


class EntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Entry
        fields = ['text', 'table']


class TableSerializer(serializers.ModelSerializer):
    entries = serializers.StringRelatedField(many=True, read_only=True)
    tags = TagSerializer(many=True)

    def create(self, validated_data):
        if not validated_data['short_name']:
            validated_data['short_name'] = validated_data['name'][:20]

        return super().create(validated_data)

    class Meta:
        model = models.Table
        fields = ['pk', 'name', 'short_name', 'tags', 'number_of_entries', 'entries']

