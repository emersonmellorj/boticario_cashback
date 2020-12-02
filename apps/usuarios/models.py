from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, cpf, password=None):
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
    cpf = models.CharField("CPF", max_length=14, primary_key=True)
    firstname = models.CharField(max_length=50, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'cpf']

    objects = UsuarioManager()


    def __str__(self):
        return self.cpf

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