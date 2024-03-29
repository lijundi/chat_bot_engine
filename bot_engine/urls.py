from django.urls import path

from . import views

urlpatterns = [
    path('train/', views.train, name='train'),
    path('test/', views.test, name='test'),
    path('get_online_model/', views.get_online_model, name='get_online_model'),
    path('online/', views.online, name='online'),
    path('start/', views.start, name='start'),
    path('stop/', views.stop, name='stop'),
    path('list/', views.get_by_skl_id, name='get_by_skl_id'),
    path('del/', views.delete_by_model_id, name='delete_by_model_id'),
    # path('reset/', views.reset_model, name='reset'),
]
