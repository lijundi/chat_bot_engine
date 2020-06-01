from django.urls import path

from . import views

urlpatterns = [
    path('train/', views.train, name='index'),
    path('test/', views.test, name='test'),
]
