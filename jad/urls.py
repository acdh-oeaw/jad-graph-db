from django.urls import path

from jad import views

app_name = "jad"

urlpatterns = [
    path("q", views.find_similar_passages, name="find_similar_passages"),
    path("network-data", views.network, name="network"),
]
