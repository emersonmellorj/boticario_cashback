from django.urls import path
from . import views

app_name = 'cashback'
urlpatterns = [
    path('compras/', views.ComprasList.as_view(), name='purchase_list'),
    path('compras/<pk>/', views.ComprasList.as_view(), name='purchase_detail'),
    path('usuarios/', views.UsuariosList.as_view(),
         name='user_create'),
    path('acumulado_cashback/<str:cpf>/',
         views.acumulado_cashback, name="cashback_acumulate")
]
