from ..models import Compras, Usuarios
from .serializers import ComprasSerializer, UsuariosSerializer

from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .utils.cashback import cashback_calculate
import requests
import logging
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

class ComprasList(APIView):
    """ Class view of purchases """
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk):
        try:
            return Compras.objects.get(purchase_code=pk)
        except Compras.DoesNotExist:
            logger.exception(f"A compra de código {pk} não existe!")
            raise Http404

    def get(self, request, pk=None, cpf=None, year=None, month=None, format=None):
        cpf_request = request.user.cpf
        
        # Total cashback value in external API
        if "acumulado_cashback" in request.get_full_path():
            return self.acumulado_cashback(cpf)

        # Get request of a single purchase
        if pk:
            logger.debug(f'Listando a compra de número {pk}')
            purchase = self.get_objects(pk)
            # Validating that the purchase belongs to the user who is authenticated
            if str(purchase.cpf) != cpf_request:
                message = f"A compra pesquisada de número {purchase.purchase_code} " \
                    f"não está vinculada ao CPF autenticado {cpf_request}."
                logger.error(
                    message
                )
                return Response(
                    {"Mensagem": message}, status=status.HTTP_403_FORBIDDEN
                )
            serializer = ComprasSerializer(purchase)

        elif cpf and month and year:
            """ Only purchases with Approved status are included in the calculations """
            if cpf_request != cpf:
                message = "Um usuário não tem permissão de consultar cashback para compras " \
                    f"que não estão vinculadas ao CPF autenticado {cpf_request}."
                logger.error(
                    message
                )
                return Response(
                    {"mensagem": message}, status=status.HTTP_403_FORBIDDEN
                )
            purchases = Compras.objects.filter(
                cpf=cpf, purchase_date__month=month, purchase_date__year=year, status='Aprovado')
            total_purchases_month = sum(purchase.purchase_total_price
                                        for purchase in purchases)
            logger.debug(
                f"Valor total de compras no mês de {month}/{year} para o cpf {cpf}: {total_purchases_month}"
            )
            # Cashback calculate of seller
            cashback_percent, cashback_value, cashback_context = cashback_calculate(
                cpf, total_purchases_month, month, year
            )
            logger.debug(f"O percentual de cashback para o cpf {cpf} é de {cashback_percent}% "
                         f"e o valor total é de {cashback_value}.")
            serializer = ComprasSerializer(purchases, many=True)
            if not purchases:
                return Response(
                    {"mensagem": "Dados não encontrados para o CPF no Mês/Ano informado."}, status=status.HTTP_404_NOT_FOUND
                )
            logger.debug(
                f'Listando as compras: {[purchase.purchase_code for purchase in purchases]}'
            )
            return Response(cashback_context)

        else:
            return Response(
                {"mensagem": "Favor informar o número da compra que deseja consultar."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.data)

    def post(self, request, format=None):
        # Validating if the authenticated user is the same as the cpf of the purchase
        cpf_user_in_request = request.user.cpf
        cpf_sent_in_json = request.data['cpf'].replace(".", "").replace("-", "")
        if cpf_user_in_request != cpf_sent_in_json:
            message = f"O CPF da compra enviada na requisição não está vinculada ao CPF autenticado {cpf_user_in_request}."
            logger.error(
                message
            )
            return Response(
                {"Mensagem": message}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = ComprasSerializer(data=request.data)
        if serializer.is_valid():
            validated_cpf = str(serializer.validated_data['cpf']) == "15350946056"
            if validated_cpf:
                logger.debug(
                    "Solicitação de cadastro de compra previamente aprovada para o CPF 15350946056."
                )
                serializer.validated_data['status'] = "Aprovado"
            serializer.save()
            logger.info(
                f"Método POST chamado para cadastro da compra: {request.data}."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def acumulado_cashback(self, cpf=None):
        """ Function that send a request for external API and get cashback acumulate """
        user_has_permission = (cpf == self.request.user.cpf)
        if user_has_permission:
            url_acumulado_cashback = f"https://mdaqk8ek5j.execute-api.us-east-1.amazonaws.com/v1/cashback?cpf={cpf}"
            logger.debug(
                f"Realizando a consulta na API do Boticário para resgatar o cashback acumulado para o CPF {cpf}"
            )
            response = requests.get(url_acumulado_cashback, headers={
                                                            'token': 'ZXPURQOARHiMc6Y0flhRC1LVlZQVFRnm'
                                                            }
                                    )
            logger.debug(
                f"Valor de cashback acumulado para o CPF {cpf}: {response.json()['body']}"
            )
            return JsonResponse(response.json()['body'], status=status.HTTP_200_OK)
        return JsonResponse({"mensagem": "Você não tem permissão para consultar o cashback deste CPF."}, 
                                status=status.HTTP_400_BAD_REQUEST
                            )


class UsuariosList(APIView):
    """ Class view of Api Users """
    permission_classes = [AllowAny]

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
            return Response({"mensagem": f"O usuário {serializer.data['email']} "
                             "foi criado com sucesso!"}, status=status.HTTP_201_CREATED)
        logger.error(
            f"Os dados para criação de usuário não foram aceitos: {request.data}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
