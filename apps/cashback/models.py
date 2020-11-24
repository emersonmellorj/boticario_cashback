from apps.cashback.api.utils.cashback import cashback_calculate
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.urls import reverse


class UsuarioManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, cpf, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            cpf=cpf,
            firstname=firstname,
            lastname=lastname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, cpf, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            cpf=cpf,
            firstname=firstname,
            lastname=lastname
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Usuarios(AbstractBaseUser):
    firstname = models.CharField(max_length=50, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=255,
        unique=True,
    )
    cpf = models.CharField("CPF", max_length=14)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'cpf']

    objects = UsuarioManager()

    def get_absolute_url(self):
        return reverse("cashback:user_detail", kwargs={"cpf": self.cpf})

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_perms(perm_list, obj=None):
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class Compras(models.Model):
    purchase_code = models.IntegerField(
        primary_key=True, null=False, blank=False
    )
    purchase_total_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=False, blank=False
    )
    purchase_date = models.DateField(null=False, blank=False)
    cpf = models.CharField("CPF", max_length=14, null=False, blank=False)
    cashback_percent = models.IntegerField(null=True, blank=True)
    cashback_value = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    status = models.CharField(max_length=15, default='Em validação')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_art = models.DateTimeField(auto_now=True)
