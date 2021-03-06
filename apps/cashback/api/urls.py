from django.urls import path
from . import views

app_name = 'cashback'
urlpatterns = [
    path('compras/', views.ComprasList.as_view(), name='purchase_create'),
    path('compras/cashback/<str:cpf>/<int:year>/<int:month>/',
         views.ComprasList.as_view(), name='purchase_list'),
    path('compras/<pk>/', views.ComprasList.as_view(), name='purchase_detail'),
    path('usuarios/', views.UsuariosList.as_view(),
         name='user_create'),
    path('compras/acumulado_cashback/<str:cpf>/',
         views.ComprasList.as_view(), name="cashback_acumulate")
]
