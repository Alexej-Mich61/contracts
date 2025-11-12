# contracts_app/urls.py
from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.ContractListView.as_view(), name='contract_list'),
    path('contract/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contract/add/', views.ContractCreateView.as_view(), name='contract_add'),
    path('contract/<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_edit'),
    path('contract/<int:pk>/update-checklist/', views.update_checklist, name='update_checklist'),
    path('contract/<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract_delete'),
]