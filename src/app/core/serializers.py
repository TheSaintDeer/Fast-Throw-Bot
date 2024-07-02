from rest_framework import serializers

from . import models


class EntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Entry
        fields = ['text', 'table']


class TableSerializer(serializers.ModelSerializer):
    entries = serializers.StringRelatedField(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = models.Table
        fields = ['pk', 'name', 'desc', 'url', 'entries']
