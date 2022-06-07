from django.contrib import admin
from django.urls import include, re_path
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('movie/', views.movie, name = 'movie'),
    path('director/', views.director, name = 'director'),
    path('actor/', views.actor, name = 'actor'),
    path('insert_data/', views.insert_data, name = 'insert_data'),
    path('insert_data_submission/', views.insert_data_submission, name = 'insert_data_submission'),
    path('new_movie/', views.new_movie, name='new_movie'),
    path('register', views.register, name='register'),
    re_path(r'^edit_movie/(?P<pk>\d+)/$', views.edit_movie, name='edit_movie'),
    re_path(r'^delete_movie/(?P<pk>\d+)/$', views.delete_movie, name='delete_movie'),
    re_path(r'^recommedation/$', views.search, name='search'),
]