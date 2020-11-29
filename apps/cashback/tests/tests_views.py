
from django.test import TestCase, Client
import requests
from django.utils import timezone

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'boticario_cashback.settings'
django.setup()

from apps.cashback.models import Compras, Usuarios
from model_mommy import mommy

class TestUsers(TestCase):
    """ Test of create and get users """
    def setUp(self):
        self.client = Client()
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
        create_user = self.client.post(self.create_user_url, data=self.user_data)

    def test_get_a_created_user(self):
        user = Usuarios.objects.get(email=self.user_data["email"])
        self.assertEqual("jorge.silva@gmail.com", user.email)

    def test_try_create_an_existing_user(self):
        create_other_user = self.client.post(self.create_user_url, data=self.user_data)
        self.assertIn("Usuário com este E-mail já existe.", create_other_user.json()['email'])


class TestPurchases(TestCase):
    """ Test of create and get new purchases and cashbacks """
    def setUp(self):
        self.client = Client()

        # URLs of project
        self.url_get_token = "http://localhost:8000/get-token/"
        self.create_user_url = "http://localhost:8000/api/usuarios/"
        self.create_purchase_url = f"http://localhost:8000/api/compras/"
        self.get_cashback_url = f"http://localhost:8000/api/compras/cashback"

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
        
        # Credentials of normal created user
        self.credentials = {
                        'email': self.user.email,
                        'password': self.user_data['password'],
                    }

        # Get token of normal created user
        self.token = self.client.post(self.url_get_token, data=self.credentials)

        # Header Authorization of normal user
        self.authorization = f"JWT {self.token.data['token']}"
        self.headers = {
            "HTTP_AUTHORIZATION": self.authorization
        }

        # Create a normal purchase
        mommy.make('Compras', cpf="99999999999", purchase_code="0", purchase_date="2020-11-30")

        # Create a validated purchase
        mommy.make(
            'Compras', 
            cpf=f"{self.user.cpf}",
            purchase_code="0",
            purchase_date="2020-11-30",
            status="Aprovado",
            created_at=timezone.now()
        )

        # Get a created purchase
        self.id_compra = Compras.objects.first().purchase_code

        # Url for get a purchase
        self.get_purchase_url = f"http://localhost:8000/api/compras/{self.id_compra}/"
        
        # Create a user that purchases will be validated in create
        self.user_validated_data = {
            "firstname": "Validated", 
            "lastname": "User", 
            "email": "validated.user@gmail.com", 
            "cpf": "15350946056",
            "password": "teste@123"
        }

        self.create_validated_user = self.client.post('http://localhost:8000/api/usuarios/', data=self.user_validated_data)
        self.validated_user = Usuarios.objects.get(email=self.user_validated_data["email"])
        
        self.credentials2 = {'email': self.validated_user.email,
                   'password': self.user_validated_data['password'],
                   }

        # Get token of validated created user
        self.token_validated_user = self.client.post(self.url_get_token, data=self.credentials2)

        # Header authorization of validated user
        self.authorization_of_validate_user = f"JWT {self.token_validated_user.data['token']}"
        self.headers_validated_user = {
            "HTTP_AUTHORIZATION": self.authorization_of_validate_user
        }

    def test_get_a_created_purchase(self):
        result = self.client.get(self.get_purchase_url, **self.headers)
        self.assertEqual(result.json()['purchase_code'], 0)

    def test_get_purchase_without_purchase_code_in_url(self):
        result = self.client.get(self.create_purchase_url , **self.headers)
        self.assertEqual("Favor informar o número da compra que deseja consultar.", result.json()["mensagem"])

    def test_get_inexistent_purchase(self):
        url = f"{self.create_purchase_url}-1/"
        result = self.client.get(url, **self.headers)
        self.assertEqual(result.json()['detail'], "Não encontrado.")

    def test_get_purchase_in_other_cpf(self):
        url = f"{self.create_purchase_url}1/"        
        result = self.client.get(url, **self.headers)
        self.assertEqual(result.status_code, 403)

    def test_try_get_cashback_for_existent_user(self):
        url = f"{self.get_cashback_url}/{self.user.cpf}/2010/10/"
        result = self.client.get(url, **self.headers)
        self.assertIn("Dados não encontrados para o CPF no Mês/Ano informado", result.json()["mensagem"])

    def test_get_cashback_for_user(self):
        url = f"{self.get_cashback_url}/{self.user.cpf}/2020/11/"
        result = self.client.get(url, **self.headers)
        self.assertIn("Valor total de compras aprovadas no mês de 11/2020", result.json())

    def test_get_cashback_in_other_cpf(self):
        url = f"{self.get_cashback_url}/{88888888888}/2020/10/"
        result = self.client.get(url, **self.headers)
        self.assertIn(
            "cashback para compras que não estão vinculadas ao CPF autenticado", 
            result.json()["mensagem"]
        )

    def test_get_cashback_without_purchases_in_month(self):
        url = f"{self.get_cashback_url}/{self.user.cpf}/1000/10/"
        result = self.client.get(url, **self.headers)
        self.assertEqual("Dados não encontrados para o CPF no Mês/Ano informado.",result.json()["mensagem"] )

    def test_get_cashback_without_send_cpf_in_request(self):
        url = f"{self.get_cashback_url}/88888888888/"
        result = self.client.get(url, **self.headers)
        self.assertEqual(result.status_code, 404)

    def test_post_a_new_purchase(self):
        data = {
                "purchase_code": -1,
                "purchase_total_price": 1.00,
                "purchase_date": "2020-12-01",
                "cpf": self.user.cpf
        }
        result = self.client.post(self.create_purchase_url, data=data, **self.headers)
        self.assertEqual(result.json()["status"], "Em validação")

    def test_post_a_new_purchase_for_other_cpf(self):
        data = {
                "purchase_code": -1,
                "purchase_total_price": 1.00,
                "purchase_date": "2020-12-01",
                "cpf": "77777777777"
        }
        result = self.client.post(self.create_purchase_url, data=data, **self.headers)
        self.assertEqual(result.status_code, 403)

    def test_post_a_new_purchase_with_existent_purchase_code(self):
        data = {
                "purchase_code": 0,
                "purchase_total_price": 1.00,
                "purchase_date": "2020-12-01",
                "cpf":  self.user.cpf
        }
        result = self.client.post(self.create_purchase_url, data=data, **self.headers)
        self.assertEqual(result.status_code, 400)

    def test_post_a_purchase_with_status_validated(self):
        data = {
                "purchase_code": -2,
                "purchase_total_price": 2.00,
                "purchase_date": "2020-12-02",
                "cpf": self.validated_user.cpf
        }
        result = self.client.post(self.create_purchase_url, data=data, **self.headers_validated_user)
        self.assertEqual("Aprovado", result.json()["status"])

    
class TestExternalAcumulatedCashback(TestCase):
    """ Test get acumulated cashback in external API over internal URL """
    def setUp(self):
        self.acumulate_cashback_url = f"http://127.0.0.1:8000/api/compras/acumulado_cashback/99999999999/"
        self.create_user_url = "http://localhost:8000/api/usuarios/"
        self.url_get_token = "http://localhost:8000/get-token/"
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
        # Credentials of normal created user
        self.credentials = {
                        'email': self.user.email,
                        'password': self.user_data['password'],
                    }
        # Get token of normal created user
        self.token = self.client.post(self.url_get_token, data=self.credentials)
        # Header Authorization of normal user
        self.authorization = f"JWT {self.token.data['token']}"
        self.headers = {
            "HTTP_AUTHORIZATION": self.authorization
        }

    def test_get_cashback_acumulate_for_logged_user(self):
        result = self.client.get(self.acumulate_cashback_url, **self.headers)
        self.assertIn("credit", result.json())

    def test_get_cashback_acumulate_for_anonymous_user(self):
        result = self.client.get(self.acumulate_cashback_url)
        self.assertEqual("As credenciais de autenticação não foram fornecidas.", result.json()['detail'])

    def test_try_get_cashback_acumulate_for_user_with_other_cpf(self):
        acumulate_cashback_url = f"http://127.0.0.1:8000/api/compras/acumulado_cashback/88888888888/"
        result = self.client.get(acumulate_cashback_url, **self.headers)
        self.assertEqual("Você não tem permissão para consultar o cashback deste CPF.", result.json()['mensagem'])