# Django
from django.conf.urls import  url
from django.views.generic import TemplateView

app_name='home'
urlpatterns = [
    url(r'^index/$',
        TemplateView.as_view(template_name='home/home.html'),
        name='index'),
]
