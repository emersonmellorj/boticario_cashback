from django.test import TestCase, Client

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'boticario_cashback.settings'
django.setup()

from apps.cashback.models import Compras, Usuarios

class TestUserModel(TestCase):

    def setUp(self):
        self.cpf = "99999999999"
        self.email = "joao_das_couves@gmail.com"
        self.firstname = "João"
        self.lastname = "das Couves"
        self.password = "teste@123"

        self.create_user = Usuarios.objects.create_user(
            email=self.email,
            cpf=self.cpf,
            firstname=self.firstname,
            lastname=self.lastname,
            password=self.password
        )

        self.create_super_user = Usuarios.objects.create_superuser(
            email="super_user@gmail.com",
            cpf="88888888888",
            firstname="super",
            lastname="user",
            password="super@123"
        )

        self.first_user = Usuarios.objects.first()

    def test_get_a_created_user(self):
        created_user = Usuarios.objects.get(email=self.email)
        self.assertEqual("joao_das_couves@gmail.com", created_user.email)

    def test_try_create_user_without_email(self):
        with self.assertRaises(ValueError):
            create_user_without_email = Usuarios.objects.create_user(email="",
                                                                    cpf=self.cpf,
                                                                    firstname=self.firstname,
                                                                    lastname=self.lastname,
                                                                    password=self.password
                                        )

    def test_create_a_super_user(self):
        self.assertEqual(self.create_super_user.is_admin, True)

    def test_print_an_user(self):
        self.assertEqual(str(self.first_user), self.first_user.cpf)

    def test_an_user_has_perm(self):
        user_has_perm = self.first_user.has_perm("Teste")
        self.assertEqual(user_has_perm, True)

    def test_an_user_has_perms(self):
        user_has_perms = self.first_user.has_perms(["Teste 1", "Teste 2"])
        self.assertEqual(user_has_perms, True)

    def test_an_user_has_module_perms(self):
        user_has_module_perms = self.first_user.has_module_perms("apps.cashback")
        self.assertEqual(user_has_module_perms, True)

    def test_an_user_is_staff(self):
        super_user = Usuarios.objects.get(email="super_user@gmail.com")
        self.assertEqual(super_user.is_staff, True)
        