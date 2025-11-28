from django.urls import path
from . import views

app_name = 'qr_generator'

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download_qr, name='download_qr'),
]