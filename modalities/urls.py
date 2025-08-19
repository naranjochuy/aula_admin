from django.urls import path
from .views import *

app_name = "modalities"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_update"),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category_delete"),
    path("sub-categories/", SubCategoryListView.as_view(), name="sub_category_list"),
    path("sub-categories/new/", SubCategoryCreateView.as_view(), name="sub_category_create"),
    path("sub-categories/<int:pk>/edit/", SubCategoryUpdateView.as_view(), name="sub_category_update"),
    path('sub-categories/<int:pk>/', SubCategoryDetailView.as_view(), name='sub_category_detail'),
    path("sub-categories/<int:pk>/delete/", SubCategoryDeleteView.as_view(), name="sub_category_delete"),
]
