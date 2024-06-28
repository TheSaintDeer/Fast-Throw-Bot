from django.db import models


class Table(models.Model):
    name = models.CharField(
        max_length=255
    )
    desc = models.TextField()
    tags = models.ManyToManyField(
        'Tag',
    )
    number_of_entries = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(
        max_length=64
    )


class Entry(models.Model):
    text = models.TextField()
    table = models.ForeignKey(
        'Table',
        on_delete=models.CASCADE
    )