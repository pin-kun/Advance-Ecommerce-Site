from django.urls import path
from ecommapp.views import *

urlpatterns = [
    path('', index, name='index-page')
]