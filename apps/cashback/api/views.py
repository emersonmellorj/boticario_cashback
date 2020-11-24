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
import logging

logger = logging.getLogger(__name__)


class ComprasList(APIView):
    def get_objects(self, pk):
        try:
            return Compras.objects.get(purchase_code=pk)
        except Compras.DoesNotExist:
            logger.exception(f"A compra de código {pk} não existe!")
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            logger.debug(f'Listando a compra de número {pk}')
            compra = self.get_objects(pk)
            serializer = ComprasSerializer(compra)
        else:
            compras = Compras.objects.all()
            logger.debug(
                f'Listando as compras: {[compra.purchase_code for compra in compras]}')
            serializer = ComprasSerializer(compras, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ComprasSerializer(data=request.data)
        if serializer.is_valid():
            # Cashback calculate for purchase
            cashback_percent, cashback_value = cashback_calculate(
                serializer.validated_data['purchase_total_price']
            )
            logger.debug(
                f"Dados calculados para cashback da compra "
                f"{serializer.validated_data['purchase_code']}: percentual de "
                f"{cashback_percent}% com o valor total de R${cashback_value}."
            )
            serializer.validated_data['cashback_percent'] = cashback_percent
            serializer.validated_data['cashback_value'] = cashback_value

            validated_cpf = serializer.validated_data['cpf'] == "15350946056"
            if validated_cpf:
                logger.debug(
                    "Solicitação de cadastro de compra previamente aprovada para o CPF 15350946056."
                )
                serializer.validated_data['status'] = "Aprovado"
            serializer.save()
            logger.info(
                f"Método POST chamado para cadastro da compra: {request.data} com "
                f"porcentagem de cashback em {cashback_percent}% e valor de cashback de R$ {cashback_value}."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuariosList(APIView):

    #authentication_classes = (BasicAuthentication,)

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
            logger.debug(f"Solicitação de cadastro de usuário: {request.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(
            f"Os dados para criação de usuário não foram aceitos: {request.data}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def acumulado_cashback(request, cpf):
    url_acumulado_cashback = f"https://mdaqk8ek5j.execute-api.us-east-1.amazonaws.com/v1/cashback?cpf={cpf}"
    logger.debug(
        f"Realizando a consulta na API do Boticário para resgatar o cashback acumulado para o CPF {cpf}"
    )
    response = requests.get(url_acumulado_cashback,
                            headers={
                                'token': 'ZXPURQOARHiMc6Y0flhRC1LVlZQVFRnm'}
                            )
    logger.debug(
        f"Valor de cashback acumulado para o CPF {cpf}: {response.json()['body']}"
    )
    return JsonResponse(response.json()['body'], status=status.HTTP_200_OK)
