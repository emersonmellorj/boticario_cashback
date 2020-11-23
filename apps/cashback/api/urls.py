from django.urls import path
from . import views

app_name = 'cashback'
urlpatterns = [
    path('compras/', views.ComprasListView.as_view(), name='purchase_list'),
    path('compras/<pk>/', views.ComprasDetailView.as_view(), name='purchase_detail'),
]
