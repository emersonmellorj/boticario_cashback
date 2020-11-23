from rest_framework import serializers
from ..models import Compras


class ComprasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compras
        fields = ['purchase_code', 'purchase_total_price',
                  'purchase_date', 'cpf', 'status']
