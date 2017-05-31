from django.conf.urls import url
from compression import views
urlpatterns = [
    url(r'^index/', views.Index.as_view(),name='index'),
    ]