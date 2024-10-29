import datetime
import json
import time
from decimal import Decimal, ROUND_HALF_UP, getcontext
from functools import reduce
from itertools import chain, groupby

NORMAL_VAT_RATE = 1
REDUCED_VAT_RATE = 2

class CashClosingException(Exception):
    def __init__(self, message):
        super().__init__(message)

class JsonSerializable:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def get_dict(self):
        if not hasattr(self, "__dict__"):
            return self
        new_subdic = vars(self)
        for key, value in new_subdic.items():
            if isinstance(value, JsonSerializable):
                new_subdic[key] = value.get_dict()
            elif isinstance(value, list):
                new_subdic[key] = [v.get_dict() for v in value if v is not None]
            else:
                new_subdic[key] = value
        return new_subdic

class CashClosingHead(JsonSerializable):
    pass

class CashClosing(JsonSerializable):
    pass

class CashStatement(JsonSerializable):
    pass

class BusinessCase(JsonSerializable):
    pass

class AmountPerVat(JsonSerializable):
    def __init__(self, *args):
        if len(args) == 0:
            return
        
        if len(args) == 3:
            self.vat_definition_export_id =  args[0]
            self.incl_vat = args[1]
            self.vat = args[2]
            excl_vat = (Decimal(str(self.incl_vat)) - Decimal(str(self.vat))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.excl_vat = float(excl_vat)
            return


        vat_name = ""
        amount = 0.0
        if len(args) == 1:
            try:
                if hasattr(args[0], 'vat_rate'):
                    vat_name = args[0].vat_rate
                    self.vat_definition_export_id = NORMAL_VAT_RATE if vat_name == "NORMAL" else REDUCED_VAT_RATE
                    
                elif hasattr(args[0], 'line_number'):
                    line = args[0]
                    self.vat_definition_export_id = NORMAL_VAT_RATE if line.vat >= 19.0 else REDUCED_VAT_RATE
                amount = float(args[0].amount)
            except Exception as e:
                print(str(e))
                print(str(args))
                raise Exception(str(e) + ' ** ' + str(args) )
        
        else:
            raise Exception(f"AmountPerVat invalid number of arguments: {len(args)}")

        
        self.incl_vat = amount
        vat_rate = Decimal(19.0) if self.is_normal() else Decimal(7.0) # TODO get the vat_rate from the product
        
        vat = (Decimal(amount) * vat_rate / Decimal(100.0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.vat = float(vat)
        
        
        excl_vat = (Decimal(amount) - vat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.excl_vat = float(excl_vat)

    
    def is_normal(self):
        return self.vat_definition_export_id == 1


class Payment(JsonSerializable):
    pass

class AmountByCurrency(JsonSerializable):
    pass

class Transaction(JsonSerializable):
    pass

class TransactionHead(JsonSerializable):
    pass

class TransactionData(JsonSerializable):
    pass

class Reference(JsonSerializable):
    def __init__(self, *args):
        self.type = "Transaktion"

class TransactionSecurity(JsonSerializable):
    pass

class Line(JsonSerializable):
    pass

class Item(JsonSerializable):
    pass

def transaction_is(tx, type):
    return hasattr(tx, 'schema') and hasattr(tx.schema, 'standard_v1') and hasattr(tx.schema.standard_v1, type)

def transaction_is_order(tx):
    return transaction_is(tx, 'order')

def transaction_is_receipt(tx):
    return transaction_is(tx, 'receipt')

def get_timestamp():
    return int(time.time())

def get_client_id(transactions):
    return transactions.data[0].client_id

def get_formatted_date(timestamp):
    date_time = datetime.datetime.fromtimestamp(timestamp)
    return date_time.strftime('%Y-%m-%d')

def format_date_number(timestamp, number):
    formatted_date = get_formatted_date(timestamp)
    formatted_number = str(number).zfill(7)
    return f"{formatted_date}-{formatted_number}"

def get_head(transactions):
    cch = CashClosingHead()
    cch.export_creation_date = get_timestamp()

    min_element = transactions[0]
    max_element = transactions[-1]

    cch.first_transaction_export_id = format_date_number(min_element.head.timestamp_start, 1)
    cch.last_transaction_export_id = format_date_number(max_element.head.timestamp_start, len(transactions))
    cch.business_date = get_formatted_date(max_element.head.timestamp_start)

    return cch

def get_business_case(receipts):
    bc = BusinessCase()
    bc.type = "Umsatz"
    bc.amounts_per_vat_id = []

    # amount1 = precise_sum([a.incl_vat for r in receipts for a in r.amounts_per_vat_id if a.is_normal()])

    # amount2 = precise_sum([a.incl_vat for r in receipts for a in r.amounts_per_vat_id if not a.is_normal()])

    incl_vat1 = precise_sum([a.incl_vat for r in receipts for a in r.amounts_per_vat_id if a.is_normal()])
    vat1 = precise_sum([a.vat for r in receipts for a in r.amounts_per_vat_id if a.is_normal()])

    incl_vat2 = precise_sum([a.incl_vat for r in receipts for a in r.amounts_per_vat_id if not a.is_normal()])
    vat2 = precise_sum([a.vat for r in receipts for a in r.amounts_per_vat_id if not a.is_normal()])

    if incl_vat1 > 0:
        bc.amounts_per_vat_id.append(AmountPerVat(NORMAL_VAT_RATE, incl_vat1, vat1))
    if incl_vat2 > 0:
        bc.amounts_per_vat_id.append(AmountPerVat(REDUCED_VAT_RATE, incl_vat2, vat2))

    return bc

def precise_sum(elements):
    getcontext().prec = 28  # Set precision
    sum_decimal = reduce(Decimal.__add__, [Decimal(str(e)) for e in elements], Decimal('0.0'))
    return float(sum_decimal)

def get_payment(receipts):
    p = Payment()
    mapptf = lambda x: x.amounts_per_payment_type
    # Filter only "RECEIPT" type receipts
    all_amounts_per_payment_type = list(chain.from_iterable(map(mapptf, [r for r in receipts if r.receipt_type == "RECEIPT"])))

    p.full_amount = precise_sum([a.amount for a in all_amounts_per_payment_type])
    p.cash_amount = precise_sum([a.amount for a in all_amounts_per_payment_type if a.payment_type == "CASH"])
    
    p.cash_amounts_by_currency = []
    
    # Filter only the cash payments before the grouping
    cash_amounts_per_payment_type = [a for a in all_amounts_per_payment_type if a.payment_type == "CASH"]
    
    # Sort by currency code for cash payments
    cash_amounts_per_payment_type.sort(key=lambda x: x.currency_code)
    
    # Summarize only the cash payments by currency
    for key, group in groupby(cash_amounts_per_payment_type, lambda x: x.currency_code):
        a = AmountByCurrency()
        a.currency_code = key
        c = list(group)
        a.amount = precise_sum([a.amount for a in c])
        p.cash_amounts_by_currency.append(a)
    
    # Summarize all payment types
    p.payment_types = []
    clause = lambda x: (x.currency_code, "Bar" if x.payment_type == "CASH" else "Unbar")
    all_amounts_per_payment_type.sort(key=clause)
    
    for key, group in groupby(all_amounts_per_payment_type, clause):
        a = AmountByCurrency()
        a.currency_code = key[0]
        a.type = key[1]
        c = list(group)
        a.amount = precise_sum([a.amount for a in c])
        p.payment_types.append(a)
    
    return p


def get_transaction_head(receipt, receipt_number, tx_export_number):
    th = TransactionHead()
    if receipt.state == 'FINISHED':
        th.type = "Beleg"
    elif receipt.state == 'CANCELLED':
        th.type = "AVBelegabbruch"
    else:
        raise CashClosingException(f"Receipt: {str(receipt)}\nState: {receipt.state}\nInvalid state")
    th.storno = False
    try:
        th.closing_client_id = receipt.client_id
        th.timestamp_start = receipt.time_start
        # TODO: 001 After cancelling txn time_end is not present
        # but we also cannot complete because it is needed, so raise exception
        if not hasattr(receipt, 'time_end'):
            raise CashClosingException()
        th.timestamp_end = receipt.time_end
        th.tx_id = receipt._id
        th.number = receipt_number
        
        # We need here the whole order to get:
        #  - date
        #  - transaction_export_id
        # Also we have to copy here the cash_point_closing_export_id (and it is the same of this whole cash closing)
        # Also we need cash_register_export_id. Not sure what to put there
        # Conclusion: Not use references
        # if hasattr(receipt, 'metadata') and hasattr(receipt.metadata, 'order_id'):
        #     th.references = []
        #     r = Reference()
        #     r.tx_id = receipt.metadata.order_id
        #     th.references.append(r)

        th.transaction_export_id = format_date_number(receipt.time_start, tx_export_number)

        return th
    except AttributeError as e:
        error_message = f"Receipt ID: {receipt._id}.\nReceipt Number: {receipt_number}.\nError: {str(e)}"
        raise AttributeError(error_message) from e


def get_transaction_data(raw_receipt):
    try:
        td = TransactionData()
        receipt = get_receipt(raw_receipt)
        td.full_amount_incl_vat = 0.0
        # avoid make computation when type is CANCELLATION
        if receipt.receipt_type == 'RECEIPT':
            td.amounts_per_vat_id = receipt.amounts_per_vat_id

            td.full_amount_incl_vat =  precise_sum([x.incl_vat for x in td.amounts_per_vat_id])
            td.payment_types = []

            for appt in receipt.amounts_per_payment_type:
                a = AmountByCurrency()
                a.currency_code = appt.currency_code
                a.type = "Bar" if appt.payment_type == "CASH" else "Unbar"
                a.amount = float(appt.amount)
                td.payment_types.append(a)

            td.lines = []

            if hasattr(receipt, 'order'):  
                line_number = 0
                for line in receipt.order.line_items:
                    # TODO add here info that goes to the line
                    if not line.is_discount:
                        line_number += 1
                        line_data = get_line_data(line)
                        line_data.lineitem_export_id = line_number
                        td.lines.append(line_data)
                    else:
                        if line.is_discount_with_vat_calculated:
                            line_number += 1
                            line_data = get_line_data(line)
                            line_data.lineitem_export_id = line_number
                            td.lines.append(line_data)

            else:
                print(f"No tiene order. Raw receipt number: {raw_receipt.number}")
                print(str(receipt))

        return td
    except AttributeError as e:
        raise AttributeError(f"{str(receipt)}  - {str(e)}")


def get_transaction_security(receipt):
    ts = TransactionSecurity()
    ts.tss_tx_id = receipt._id

    return ts

def get_transactions(receipts, last_receipt_number):
    transactions = []
    tx_export_number = 0
    for receipt in receipts:
        if receipt.state in ["FINISHED", "CANCELLED"]:
            t = Transaction()
            tx_export_number += 1
            receipt_number = last_receipt_number + tx_export_number
            t.head = get_transaction_head(receipt, receipt_number, tx_export_number)
            t.data = get_transaction_data(receipt)
            t.security = get_transaction_security(receipt)

            transactions.append(t)
        else:
            raise Exception(f"Receipt ID {receipt._id} is in state {receipt.state}. Ignoring")

    return transactions

def get_cash_statement(receipts):
    cs = CashStatement()
    cs.business_cases = [
        get_business_case(receipts)
    ]
    cs.payment = get_payment(receipts)

    return cs

def get_raw_receipts(transactions):
    return list(filter(transaction_is_receipt, transactions.data))

def get_receipt(raw_receipt):
    return raw_receipt.schema.standard_v1.receipt

def get_receipts(raw_receipts):
    receipts = map(get_receipt, raw_receipts)

    return list(receipts)

def set_receipt_amounts_per_vat_id(raw_receipt):
    amounts_per_vat_id = []
    receipt = get_receipt(raw_receipt)

    amounts_per_vat_rate = receipt.amounts_per_vat_rate
    for amount_per_vat_rate in amounts_per_vat_rate:
        if float(amount_per_vat_rate.amount) > 0.0:
            amounts_per_vat_id.append(AmountPerVat(amount_per_vat_rate))

    receipt.amounts_per_vat_id = amounts_per_vat_id

def add_amounts_per_vat_id(raw_receipts):
    for r in raw_receipts:
        set_receipt_amounts_per_vat_id(r)

def build_cash_closing(transactions, options, products_provider):
    cc = CashClosing()
    cc.cash_point_closing_export_id = options["last_cash_point_closing_export_id"] + 1

    cc.client_id = get_client_id(transactions)

    add_order_to_receipt(transactions, products_provider)

    raw_receipts = get_raw_receipts(transactions)
    add_amounts_per_vat_id(raw_receipts)
    receipts = get_receipts(raw_receipts)

    last_receipt_number = options["last_receipt_number"]

    cc.transactions = get_transactions(raw_receipts, last_receipt_number)
    cc.cash_statement = get_cash_statement(receipts)
    cc.head = get_head(cc.transactions)

    return cc

def get_line_data(line):
    l = Line()
    l.business_case = get_line_business_case(line)
    l.in_house = False
    l.storno = False
    l.text = line.description
    l.item = Item()
    l.item.number = line.line_number
    l.item.quantity = float(line.quantity)
    l.item.price_per_unit = float(line.price_per_unit)


    return l

def get_line_business_case(line):
    bc = BusinessCase()
    # TODO: check discounts
    bc.type = "Rabatt" if line.is_discount else "Umsatz"

    bc.amounts_per_vat_id = [
        AmountPerVat(line)
    ]

    return bc

def add_order_to_receipt(transactions, products_provider):
    txs = transactions.data
    orders = {}

    for tx in txs:
        if transaction_is_order(tx):
            order = tx.schema.standard_v1.order
            line_number = 1
            for l in order.line_items:
                l.line_number = line_number
                line_number += 1
                l.is_discount = float(l.price_per_unit) < 0
                if not l.is_discount:
                    id = int(l.text.split(' - ', 1)[0])
                    product = products_provider.get_by_id(id)
                    l.id = product.id
                    l.vat = product.vat
                    l.description = product.title
                elif l.line_number == 2: # there are only 2 lines and the 2nd is discount
                    l.vat = order.line_items[0].vat
                    l.description = l.text
                    l.is_discount_with_vat_calculated = True
                else: 
                    first_vat = order.line_items[0].vat

                    all_same_vat = reduce(lambda a, b:  a and b, [x.vat == first_vat for x in order.line_items if not x.is_discount], True )
                    if all_same_vat: # there are many lines but all have the same VAT rate
                        l.vat = order.line_items[0].vat
                        l.description = l.text
                        l.is_discount_with_vat_calculated = True
                    else: # TODO: treat all cases
                        # TODO: throw error here we can't handle it yet
                        l.is_discount_with_vat_calculated = False
                        continue

                l.amount = float(l.quantity) * float(l.price_per_unit)
                l.vat_without_discount = l.amount * l.vat # TODO we still not need this
                
                l.business_case = get_line_business_case(l)


            orders[tx._id] = order

    for tx in txs:
        if transaction_is_receipt(tx) and hasattr(tx, 'metadata'):
            if hasattr(tx.metadata, 'order_id'):
                tx.schema.standard_v1.receipt.order = orders[tx.metadata.order_id]
            
            if hasattr(tx.metadata, 'fiskaly_order_id'):
                tx.schema.standard_v1.receipt.order = orders[tx.metadata.fiskaly_order_id]
            