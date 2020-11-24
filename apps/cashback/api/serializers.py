from rest_framework import serializers
from ..models import Compras, Usuarios


class ComprasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compras
        fields = ['purchase_code', 'purchase_total_price',
                  'purchase_date', 'cpf', 'cashback_percent', 'cashback_value', 'status']


class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['firstname', 'lastname', 'email', 'cpf', 'password']

        extra_kwargs = {
            'password': {'write_only': True},
        }
