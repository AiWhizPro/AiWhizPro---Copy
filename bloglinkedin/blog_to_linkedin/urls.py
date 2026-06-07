from django.urls import path
from . import views

app_name = 'blog_to_linkedin'

urlpatterns = [
    path('', views.home, name='home'),
]
