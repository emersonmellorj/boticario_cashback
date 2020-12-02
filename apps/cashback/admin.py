from django.contrib import admin
from .models import Compras

@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    list_display = ('purchase_code', 'cpf', 'purchase_total_price',
                    'purchase_date', 'status')

    list_filter = ('purchase_date',)
    fieldsets = (
        (None, {'fields': ('cpf', 'purchase_code', 'purchase_total_price',
                           'purchase_date', 'status')}),
    )

    search_fields = ('purchase_code',)
