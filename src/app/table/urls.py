from django.urls import path, include
from rest_framework import routers

from . import views


app_name = 'table'

router = routers.DefaultRouter()
router.register(r'table', views.TableViewSet)
router.register(r'entry', views.EntryViewSet)
router.register(r'tag', views.TagViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
