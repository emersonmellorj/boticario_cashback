from django.db.models import query
from rest_framework import generics
from ..models import Compras, Usuarios
from .serializers import ComprasSerializer, UsuariosSerializer

from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication

from .utils.cashback import cashback_calculate
import requests


class ComprasList(APIView):
    def get_objects(self, pk):
        try:
            return Compras.objects.get(purchase_code=pk)
        except Compras.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            compra = self.get_objects(pk)
            serializer = ComprasSerializer(compra)
        else:
            compra = Compras.objects.all()
            serializer = ComprasSerializer(compra, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ComprasSerializer(data=request.data)
        if serializer.is_valid():
            # Cashback calculate for purchase
            cashback_percent, cashback_value = cashback_calculate(
                serializer.validated_data['purchase_total_price']
            )
            serializer.validated_data['cashback_percent'] = cashback_percent
            serializer.validated_data['cashback_value'] = cashback_value

            validated_cpf = serializer.validated_data['cpf'] == "15350946056"
            if validated_cpf:
                serializer.validated_data['status'] = "Aprovado"
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuariosList(APIView):

    #authentication_classes = (BasicAuthentication,)

    def get_objects(self, cpf):
        try:
            return Usuarios.objects.get(cpf=cpf)
        except Usuarios.DoesNotExist:
            raise Http404

    # def get(self, request, cpf, format=None):
    #    usuario = self.get_objects(cpf)
    #    serializer = UsuariosSerializer(usuario)
    #    return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UsuariosSerializer(data=request.data)
        if serializer.is_valid():
            Usuarios.objects.create_user(
                serializer.data['email'],
                serializer.data['firstname'],
                serializer.data['lastname'],
                serializer.data['cpf'],
                serializer.data['password']
            )
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def acumulado_cashback(request, cpf):
    url_acumulado_cashback = f"https://mdaqk8ek5j.execute-api.us-east-1.amazonaws.com/v1/cashback?cpf={cpf}"
    response = requests.get(url_acumulado_cashback,
                            headers={
                                'token': 'ZXPURQOARHiMc6Y0flhRC1LVlZQVFRnm'}
                            )
    return JsonResponse(response.json()['body'], status=status.HTTP_200_OK)
