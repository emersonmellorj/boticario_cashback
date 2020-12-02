# Desafio cadastro / consulta de cashbacks para revendedores do Boticário

## 1 - Problema / Oportunidade

O Boticário tem várias soluções para ajudar seus revendedores(as) a gerir suas finanças e alavancar suas vendas. Também existem iniciativas para impulsionar as operações de vendas como metas gameficadas e desconto em grandes quantidades de compras. Agora queremos criar mais uma solução, e é aí que você entra com seu talento ;) 
A oportunidade proposta é criar um sistema de Cashback, onde o valor será disponibilizado como crédito para a próxima compra da revendedora no Boticário; 
Cashback quer dizer “dinheiro de volta”, e funciona de forma simples: o revendedor faz uma compra e seu benefício vem com a devolução de parte do dinheiro gasto no mês seguinte. 
Sendo assim o Boticário quer disponibilizar um sistema para seus revendedores(as) cadastrarem suas compras e acompanhar o retorno de cashback de cada um. 

## 2 - Pacotes utilizados no projeto:

Todas as bibliotecas externas do projeto estão no arquivo requirements.txt.

## 3 - Banco de dados utilizado na solução:

Foi utilizado o Postgres como solução de armazenamento dos dados do projeto.

## 4 - Instalação e utilização da API:

De dentro do diretório aonde você deseja instalar o projeto basta criar o seu ambiente virtual, ativar o mesmo e após dar um git clone. Feito isso, instalar as dependências que estão no arquivo "requirements.txt". Logo após realizar as configurações do banco de dados em settings.py e executar os comandos makemigrations e migrate para criar a estrutura de dados.
Após realizar todos estes passos acima você já pode levantar o ambiente de teste do django com o python manage.py runserver.

## 5 - Rotas internas da API e métodos aceitos:

- http://127.0.0.1:8000/api/usuarios/ --> Cadastrar um usuário na API (POST)
- http://127.0.0.1:8000/get-token/ --> Obtér o token de autenticação (POST)
- http://127.0.0.1:8000/refresh-token/ --> Obtér a atualização do token que esta expirando (POST)
- http://127.0.0.1:8000/api/compras/ --> Cadastrar uma compra (POST)
- http://127.0.0.1:8000/api/compras/cashback/{cpf}/{ano_da_compra}/{mês_da_compra}/ --> Consultar o cashback 
de um revendedor em determinado período. É necessário enviar o CPF de cadastro da compra junto do mês / ano. (GET)
- http://127.0.0.1:8000/api/compras/{número_da_compra}/ --> Consulta uma compra específica (GET)
- http://127.0.0.1:8000/api/compras/acumulado_cashback/{cpf_da_compra}/ --> Consultar o cashback acumulado do usuário. (GET)

## 6 - Acesso às rotas da API e autenticação JWT:

Um usuário, para conseguir cadastrar / consultar uma compra ou cashback, precisa previamente ter cadastrado o seu usuário
na API. Como este usuário, ele terá acesso à url de autenticação para obter o seu token e assim conseguir acessar as rotas
da aplicação.

Quando for necessário fazer um post para a API, os dados enviados deverão seguir o padrão json. Veja um exemplo abaixo:

- Para cadastrar um usuário, os dados enviados no body da requisição deverão respeitar o padrão abaixo:
```
{
  "firstname": "Joaquim",
  "lastname": "José",
  "email": "joaquim.jose@gmail.com",
  "cpf": "99999999999", # Sem pontos e vírgulas, apenas a numeração
  "password": "teste@9999"
}
```

- Para cadastrar uma compra, o usuário deverá enviar as informações abaixo no body da requisição:
```
{
  "purchase_code": 18,
  "purchase_total_price": 407.00,
  "purchase_date": "2020-11-25",
  "cpf": "99999999999" # Sem pontos e vírgulas, apenas a numeração
}
```

## 7 - Obtendo o token de autenticação:

Após o usuário ter se cadastrado, basta o mesmo fazer um post na url get-token da API e enviar os dados 
no formato abaixo:
```
{
	"email":"",
	"password":""
}
```

O retorno será o seu token de acesso no padrão abaixo:
```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImVtZXJzb25zbUBnbWFpbC5jb20iLCJleHAiOjE2MDY2Njc4MzAsImVtYWlsIjoiZW1lcnNvbnNtQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjA2NjY0MjMwfQ.gitZgFalZEkIpzCtk-yikOsfmCRAMQB2ykuy9OIJSLI"
}
```

## 8 - Acessando as urls da API:

Após estar de posse do seu token, basta enviar esta informação no header das suas requisições conforme abaixo:

```
Authorization: "JWT + o seu token de acesso"
```

## 9 - Regras de negócio da API:

- Um usuário pertencente à um CPF só poderá cadastrar compras para o seu CPF de cadastro;
- Quando um usuário for consultar o seu cashback para determinado mês, o cálculo será feita apenas sobre as 
compras que estão com status = "Aprovado". Caso não possua compras com este status a API informará ao usuário;
- Um usuário só poderá consultar compras / cashback para o mesmo cpf que esta em seu cadastro;
- Da mesma forma, um usuário só poderá consultar o cashback acumulado (API externa) se o CPF da requisição for
o mesmo do seu cadastro;
- No momento do cadastro de uma compra, se o usuário autenticado (que obteve o token de acesso) tiver o 
CPF 15350946056, a compra será cadastrada automaticamente com o status = "Aprovado".
- Para a moderação das compras, o super usuario do django poderá acessar o django admin e verificar todas as compras 
cadastradas, tendo o poder inclusive de alterar o status da mesma;
- Uma compra só poderá ser cadastrada uma vez (validação pelo número da compra);

## 10 - Testes automatizados:

A cobertura dos testes estão baseados no relatório gerado pelo coverage. Foram desenvolvidos testes para as Views, Models, Serializers e para a função de cashback do projeto. Para executar os testes, basta utilizar o comando no shell, de dentro do diretório do projeto:

coverage run -m unittest discover apps/cashback/tests/

Conforme pode ser visto abaixo, segundo o coverage, nossa cobertura de testes está em 100%.

IMAGEM

## 11 - Logs da aplicação:
Foram configuradas saídas de logs para o terminal e para arquivo, de acordo com a severidade de cada uma delas. Os logs 
serão registrados no arquivo logs/cashback_system.log.

## 12 - Validade dos tokens de autenticação:
Como padrão, foi configurado 1 hora de duração para cada token. Após o mesmo expirar, bastar solicitar um novo. Também
 poderá ser feita uma solicitação de atualização de token antes do mesmo expirar. Bastar fazer um POST na url abaixo e seguir o padrão no envio dos dados no body da requisição:

http://127.0.0.1:8000/refresh-token/

```
{
    "token": "token que está expirando"
}
```

Importante ressaltar que a solicitação de atualização do token deverá ser feita antes da expiração do mesmo. Após expirar,
o usuário deverá solicitar um novo token fazendo o processo de solicitação de token na url get-token.