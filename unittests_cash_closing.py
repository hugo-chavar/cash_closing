import json
import unittest
from decimal import Decimal
from constants import CASH_CLOSING_FILENAME, CASH_CLOSING_UNFORMATTED_FILENAME, TRANSACTIONS_FILENAME

# Load the JSON data
with open(CASH_CLOSING_FILENAME, 'r') as f:
    data = json.load(f)

class TestCashRegisterData(unittest.TestCase):

    def test_amounts_per_vat_id(self):
        vat_sums = {}
        transactions = data['transactions']

        # Calculate the sums for each vat_definition_export_id
        for transaction in transactions:
            for amount in transaction['data']['amounts_per_vat_id']:
                vat_id = amount['vat_definition_export_id']
                if vat_id not in vat_sums:
                    vat_sums[vat_id] = {
                        'excl_vat': Decimal('0.0'),
                        'incl_vat': Decimal('0.0'),
                        'vat': Decimal('0.0')
                    }
                vat_sums[vat_id]['excl_vat'] += Decimal(str(amount['excl_vat']))
                vat_sums[vat_id]['incl_vat'] += Decimal(str(amount['incl_vat']))
                vat_sums[vat_id]['vat'] += Decimal(str(amount['vat']))
                # print(f"{transaction['head']['number']}, {vat_id}, {str(amount['excl_vat'])}, {str(amount['incl_vat'])}, {str(amount['vat'])}")

        # Check the sums against the amounts_per_vat_id in the business_cases
        for business_case in data['cash_statement']['business_cases']:
            for amount in business_case['amounts_per_vat_id']:
                vat_id = amount['vat_definition_export_id']
                self.assertAlmostEqual(Decimal(str(amount['excl_vat'])), vat_sums[vat_id]['excl_vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")
                self.assertAlmostEqual(Decimal(str(amount['incl_vat'])), vat_sums[vat_id]['incl_vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")
                self.assertAlmostEqual(Decimal(str(amount['vat'])), vat_sums[vat_id]['vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")

    def test_payments(self):
        payment_type_sums = {}
        transactions = data['transactions']

        # Calculate the sums for each payment_type
        for transaction in transactions:
            for payment in transaction['data']['payment_types']:
                payment_type = payment['type']
                if payment_type not in payment_type_sums:
                    payment_type_sums[payment_type] = Decimal('0.0')
                payment_type_sums[payment_type] += Decimal(str(payment['amount']))

        # Check the sums against the payment_type
        for payment_type in data['cash_statement']['payment']['payment_types']:
            self.assertAlmostEqual(
                Decimal(str(payment_type['amount'])), 
                payment_type_sums[payment_type['type']],
                places=2,
                msg=f"VAT ID {payment_type}: excl_vat mismatch")
               
if __name__ == '__main__':
    unittest.main()
