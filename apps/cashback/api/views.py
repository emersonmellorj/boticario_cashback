from django.db.models import query
from rest_framework import generics
from ..models import Compras
from .serializers import ComprasSerializer


class ComprasListView(generics.ListAPIView):
    queryset = Compras.objects.all()
    serializer_class = ComprasSerializer


class ComprasDetailView(generics.RetrieveAPIView):
    queryset = Compras.objects.all()
    serializer_class = ComprasSerializer
