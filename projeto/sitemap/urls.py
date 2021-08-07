#coding: utf-8
from django.urls import path 
from django.conf.urls import url
from .import views

urlpatterns = [
    #path('index', views.Index.as_view(), name='index'),
    url('index/(?P<id>[A-z]+)/$', views.Index.as_view(), name='index'),
]


