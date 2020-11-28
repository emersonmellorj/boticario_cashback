from django.test import TestCase, Client
from apps.cashback.api.utils.cashback import cashback_calculate

class TestCashbackCalculate(TestCase):
    """ Test of percents and values of cashbacks """
    def test_return_cashback_calculate_ten_percent(self):
        percent, value, context = cashback_calculate("99999999999", 500.00, 11, 2020)
        self.assertEqual(percent, 10)

    def test_return_cashback_calculate_fifteen_percent(self):
        percent, value, context = cashback_calculate("99999999999", 1000.00, 11, 2020)
        self.assertEqual(percent, 15)

    def test_return_cashback_calculate_twenty_percent(self):
        percent, value, context = cashback_calculate("99999999999", 2000.00, 11, 2020)
        self.assertEqual(percent, 20)