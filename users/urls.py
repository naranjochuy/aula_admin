from django.urls import path
from .views import *

app_name = "users"

urlpatterns = [
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/new/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/edit/", GroupUpdateView.as_view(), name="group_update"),
    path("groups/<int:pk>/delete/", GroupDeleteView.as_view(), name="group_delete"),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
]
