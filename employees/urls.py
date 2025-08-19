from django.urls import path
from .views import (
    EmployeeListView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDeleteView,
    EmployeeDetailView,
    EmployeePermissionsUpdateView
)

app_name = 'employees'

urlpatterns = [
    path('', EmployeeListView.as_view(), name='list'),
    path('new/', EmployeeCreateView.as_view(), name='create'),
    path('view/<int:pk>/', EmployeeDetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', EmployeeUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', EmployeeDeleteView.as_view(), name='delete'),
    path('permissions/<int:pk>/', EmployeePermissionsUpdateView.as_view(), name='permissions'),
]
