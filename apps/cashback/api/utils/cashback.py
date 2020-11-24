def cashback_calculate(value):
    if value < 1000.00:
        cashback_percent = 10
    elif value >= 1000.00 and value < 1500.00:
        cashback_percent = 15
    else:
        cashback_percent = 20
    cashback_value = round(value * cashback_percent / 100, 2)
    return cashback_percent, cashback_value
