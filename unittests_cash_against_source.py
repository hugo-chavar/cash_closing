import json
import unittest
from decimal import Decimal, getcontext, ROUND_HALF_UP
from cash_closing_config import Config
from models import FiskalyClient

client = FiskalyClient.objects.get(id=1)
config = Config(client)
# test specific cc
config.last_cc_export_id = 197

# set precision
getcontext().prec = 28



# config = Config(BASE_TIMESTAMP, last_cc_export_id=LAST_CASH_POINT_CLOSING_EXPORT_ID, last_receipt_number=LAST_RECEIPT_NUMBER)
# config.cash_register = "e2bc3f5a-1130-4d08-ac54-0fb6730d3963"

# Load the JSON data from the merged file
with open(config.transactions_filename(), 'r') as f:
    merged_data = json.load(f)

# Load the JSON data from the result file
with open(config.cash_closing_filename(), 'r') as f:
    result_data = json.load(f)

class TestMergedFileAgainstResultFile(unittest.TestCase):

    def test_amounts_per_vat_id(self):
        vat_sums = {}
        transactions = merged_data['data']

        # Calculate the sums for each vat_definition_export_id from the merged file
        for transaction in transactions:
            if 'schema' in transaction and 'standard_v1' in transaction['schema']:
                standard_v1 = transaction['schema']['standard_v1']
                if 'receipt' in standard_v1 and 'amounts_per_vat_rate' in standard_v1['receipt']:
                    for tax in standard_v1['receipt']['amounts_per_vat_rate']:
                        vat_id = 1 if tax['vat_rate'] == 'NORMAL' else 2
                        vat_rate = Decimal(19) if tax['vat_rate'] == 'NORMAL' else Decimal(7)
                        if vat_id not in vat_sums:
                            vat_sums[vat_id] = {
                                'excl_vat': Decimal('0.0'),
                                'incl_vat': Decimal('0.0'),
                                'vat': Decimal('0.0')
                            }
                        amount = Decimal(str(tax['amount']))
                        # vat = round(amount * vat_rate / Decimal(100))
                        vat = (amount * vat_rate / Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                        vat_sums[vat_id]['incl_vat'] += amount
                        vat_sums[vat_id]['vat'] += vat
                        vat_sums[vat_id]['excl_vat'] += (amount - vat)

        # Check the sums against the amounts_per_vat_id in the business_cases from the result file
        for business_case in result_data['cash_statement']['business_cases']:
            for tax in business_case['amounts_per_vat_id']:
                vat_id = tax['vat_definition_export_id']
                self.assertAlmostEqual(Decimal(str(tax['excl_vat'])), vat_sums[vat_id]['excl_vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")
                self.assertAlmostEqual(Decimal(str(tax['incl_vat'])), vat_sums[vat_id]['incl_vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")
                self.assertAlmostEqual(Decimal(str(tax['vat'])), vat_sums[vat_id]['vat'], places=2,
                    msg=f"VAT ID {vat_id}: excl_vat mismatch")

        for tx in result_data['transactions']:
            tx_number = tx['head']['number']
            if tx['head']['type'] != "Beleg":
                continue
            # print(f"Pr: {tx_number}")
            tx_vat_data_1 = next((item for item in tx['data']['amounts_per_vat_id'] if item['vat_definition_export_id'] == 1), {})
            tx_vat_data_2 = next((item for item in tx['data']['amounts_per_vat_id'] if item['vat_definition_export_id'] == 2), {})

            tx_incl_vat_1 = tx_vat_data_1.get('incl_vat', 0)
            tx_acum_incl_vat_1 = 0
            # tx_excl_vat_1 = tx_vat_data_1.get('excl_vat', 0)
            # tx_vat_1 = tx_vat_data_1.get('vat', 0)

            tx_incl_vat_2 = tx_vat_data_2.get('incl_vat', 0)
            tx_acum_incl_vat_2 = 0
            # tx_excl_vat_2 = tx_vat_data_2.get('excl_vat', 0)
            # tx_vat_2 = tx_vat_data_2.get('vat', 0)
            
            for line in tx['data']['lines']:
                line_vat_data_1 = line['business_case']['amounts_per_vat_id'][0] if line['business_case']['amounts_per_vat_id'][0]['vat_definition_export_id'] == 1 else {}
                line_vat_data_2 = line['business_case']['amounts_per_vat_id'][0] if line['business_case']['amounts_per_vat_id'][0]['vat_definition_export_id'] == 2 else {}

                line_incl_vat_1 = line_vat_data_1.get('incl_vat', 0)
                tx_acum_incl_vat_1 += line_incl_vat_1
                # line_excl_vat_1 = line_vat_data_1.get('excl_vat', 0)
                # line_vat_1 = line_vat_data_1.get('vat', 0)

                line_incl_vat_2 = line_vat_data_2.get('incl_vat', 0)
                tx_acum_incl_vat_2 += line_incl_vat_2
                # line_excl_vat_2 = line_vat_data_2.get('excl_vat', 0)
                # line_vat_2 = line_vat_data_2.get('vat', 0)
                
            self.assertAlmostEqual(Decimal(str(tx_incl_vat_1)), Decimal(str(tx_acum_incl_vat_1)), places=2,
                    msg=f"TX number {tx_number}: vat1 mismatch")
            self.assertAlmostEqual(Decimal(str(tx_incl_vat_2)), Decimal(str(tx_acum_incl_vat_2)), places=2,
                    msg=f"TX number {tx_number}: vat2 mismatch")

    def test_payments(self):
        payment_type_sums = {}
        transactions = merged_data['data']

        # Calculate the sums for each payment_type from the merged file
        for transaction in transactions:
            if 'schema' in transaction and 'standard_v1' in transaction['schema']:
                standard_v1 = transaction['schema']['standard_v1']
                if 'receipt' in standard_v1 and 'amounts_per_payment_type' in standard_v1['receipt']:
                    for payment in standard_v1['receipt']['amounts_per_payment_type']:
                        payment_type = payment['payment_type']
                        if payment_type not in payment_type_sums:
                            payment_type_sums[payment_type] = Decimal('0.0')
                        amount = Decimal(str(payment['amount']))

                        payment_type_sums[payment_type] += amount

        # Check the sums against the payment_type
        for payment in result_data['cash_statement']['payment']['payment_types']:
            self.assertAlmostEqual(
                Decimal(str(payment['amount'])), 
                payment_type_sums["CASH" if payment['type'] == "Bar" else "NON_CASH"],
                places=2,
                msg=f"VAT ID {payment}: excl_vat mismatch")
               

if __name__ == '__main__':
    unittest.main()
