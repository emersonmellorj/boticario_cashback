from django.db import models
from apps.usuarios.models import Usuarios
class Compras(models.Model):

    STATUS_CHOICES = (
        ("Em validação", "Em validação"),
        ("Aprovado", "Aprovado")
    )

    purchase_code = models.IntegerField(
        primary_key=True, null=False, blank=False
    )
    purchase_total_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=False, blank=False
    )
    purchase_date = models.DateField(null=False, blank=False)
    cpf = models.ForeignKey(Usuarios, related_name="usuario", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='Em validação'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_art = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
