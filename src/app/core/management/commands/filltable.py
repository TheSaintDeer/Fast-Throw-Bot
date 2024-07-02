import os
import requests

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup

from core.models import Table, Entry

url = 'https://www.dndspeak.com/author/g6g2134211425118/page/'

def create_table(name, desc, url):
    return Table.objects.create(name=name, desc=desc, url=url)

def create_entry(table, text):
    return Entry.objects.create(table=table, text=text)

class Command(BaseCommand):
    help = "Fill tables"
    
    def handle(self, *args, **options):
        for i in range(1, 22):
            html_code = requests.get(url+str(i)+'/').text
            soup = BeautifulSoup(html_code, features="html.parser")

            for page in soup.find_all('a', 'ar-bunyad-main-full'):
                html = requests.get(page['href']).text
                s = BeautifulSoup(html, features="html.parser")

                url_page = page['href']
                name = s.find_all('h1', 'is-title')[0].text
                desc = s.find_all('div', 'entry-content')[0].p.text 
                table = create_table(name, desc, url_page)

                for entry in s.find_all('td', 'column-2'):
                    create_entry(table, entry.text)