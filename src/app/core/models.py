from django.db import models


class Table(models.Model):
    name = models.CharField(
        max_length=255
    )
    short_name = models.CharField(
        max_length=20,
        null=True
    )
    desc = models.TextField(
        null=True
    )
    tags = models.ManyToManyField(
        'Tag',
    )
    number_of_entries = models.IntegerField()

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=64
    )

    def __str__(self):
        return f'{self.name}'


class Entry(models.Model):
    table = models.ForeignKey(
        'Table',
        on_delete=models.CASCADE,
        related_name='entries'
    )
    text = models.TextField()

    def __str__(self):
        return f'{self.text}'
    
    class Meta:
        verbose_name_plural = "entries"
