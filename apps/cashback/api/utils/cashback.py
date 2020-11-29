def cashback_calculate(cpf, value, month, year):
    """ Function for cashback calculate """
    if value < 1000.00:
        cashback_percent = 10
    elif value >= 1000.00 and value < 1500.00:
        cashback_percent = 15
    else:
        cashback_percent = 20
    cashback_value = round(value * cashback_percent / 100, 2)

    cashback_context = {
        'CPF da compra': cpf,
        f'Valor total de compras aprovadas no mês de {month}/{year}': f"R$ {value}",
        'Percentual de cashback': f"{cashback_percent}%",
        'Valor total de cashback': f"R$ {cashback_value}"
    }

    return cashback_percent, cashback_value, cashback_context
