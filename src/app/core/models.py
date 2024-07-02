from django.db import models


class TelegramChat(models.Model):
    chat_id = models.CharField(
        max_length=10,
    )
    favorite_tables = models.ManyToManyField(
        'Table',
        blank=True
    )

    def __str__(self):
        return f'{self.chat_id}'


class Table(models.Model):
    
    name = models.CharField(
        max_length=255
    )
    desc = models.TextField(
        null=True
    )
    url = models.URLField(
        max_length=1024
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
