from django.test import TestCase, Client

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'boticario_cashback.settings'
django.setup()

from apps.cashback.models import Compras, Usuarios
from apps.cashback.api.serializers import ComprasSerializer, UsuariosSerializer

from django.utils import timezone

class TestUsuariosSerializer(TestCase):

    def setUp(self):
        self.user_atributes = {
            'firstname': 'User',
            'lastname': 'Any',
            'email': 'user_any@gmail.com',
            'cpf': '99999999999',
            'password': 'user@any123'
        }

        self.user = Usuarios.objects.create(**self.user_atributes)
        self.serializer = UsuariosSerializer(instance=self.user)

    def test_serializer_user_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual("user_any@gmail.com", data["email"])


class TestComprasSerializer(TestCase):

    def setUp(self):

        self.create_user_url = "http://localhost:8000/api/usuarios/"

        # Data for create an normal user
        self.user_data = {
            "firstname": "Jorge", 
            "lastname": "Silva", 
            "email": "jorge.silva@gmail.com", 
            "cpf": "99999999999",
            "password": "teste@123"
        }

        # Create an normal user        
        self.create_user = self.client.post(self.create_user_url, data=self.user_data)

        # Get a normal created user
        self.user = Usuarios.objects.get(email=self.user_data["email"])

        self.purchase_atributes = {
            'purchase_code': 0,
            'purchase_total_price': 1000.00,
            'purchase_date': '2020-11-30',
            'cpf': self.user,
            'status': 'Aprovado',
            'created_at': timezone.now()
        }

        self.purchase = Compras.objects.create(**self.purchase_atributes)
        self.serializer = ComprasSerializer(instance=self.purchase)

    def test_serializer_purchase_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual("99999999999", data["cpf"])