
from django.urls import path

from . import views

urlpatterns = [
    path('',views.homepage,name=''),
    path('search', views.search, name = 'search'),
    path('clickrank', views.rank, name = 'clickrank')
]
