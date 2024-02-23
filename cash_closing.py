import time
import json
from functools import reduce
from itertools import chain, groupby

NORMAL_VAT_RATE = 1
REDUCED_VAT_RATE = 2

class JsonSerializable:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def get_dict(self):
        built_dict={}
        if not hasattr(self, "__dict__"):
            return self
        new_subdic = vars(self)
        # new_subdic = {k: v for k, v in vars(self).items() if not k.startswith('_')}
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
        
        elif len(args) == 2:
            self.vat_definition_export_id =  args[0]
            amount = args[1]

        
        self.incl_vat = amount
        vat_rate = 19.0 if self.is_normal() else 7.0
        self.vat = round(self.incl_vat * vat_rate / 100.0, 2)
        self.excl_vat = round(self.incl_vat - self.vat, 2)

    # @property
    # def vat(self):
    #     vat_rate = 19.0 if self.is_normal() else 7.0
    #     return round(self.incl_vat * vat_rate / 100.0, 2)
    
    # @property
    # def excl_vat(self):
    #     return round(self.incl_vat - self.vat, 2)
    
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
    pass

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

def get_head(transactions):
    # TODO fix first and last
    cch = CashClosingHead()
    cch.export_creation_date = get_timestamp()
    cch.first_transaction_export_id = 1
    cch.last_transaction_export_id = 100

    return cch

def get_business_case(receipts):
    bc = BusinessCase()
    bc.type = "Umsatz"
    bc.amounts_per_vat_id = []

    amount1 = sum(a.incl_vat for r in receipts for a in r.amounts_per_vat_id if a.is_normal())
    amount2 = sum(a.incl_vat for r in receipts for a in r.amounts_per_vat_id if not a.is_normal())

    if amount1 > 0:
        bc.amounts_per_vat_id.append(AmountPerVat(NORMAL_VAT_RATE, amount1))
    if amount2 > 0:
        bc.amounts_per_vat_id.append(AmountPerVat(REDUCED_VAT_RATE, amount2))


    # for receipt in receipts:
    #     receipt.schema.standard_v1.receipt.amounts_per_vat_id
    
    # total_amount1 = 0.0
    # total_amount2 = 0.0
    # for receipt in receipts:
    #     # amounts_per_vat_rate = receipt.schema.standard_v1.receipt.amounts_per_vat_rate
    #     amounts_per_vat_rate = receipt.amounts_per_vat_rate
    #     for amount_per_vat_rate in amounts_per_vat_rate:
    #         if amount_per_vat_rate.vat_rate == "NORMAL":
    #             total_amount1 += float(amount_per_vat_rate.amount)
    #         elif amount_per_vat_rate.vat_rate == "REDUCED_1":
    #             total_amount2 += float(amount_per_vat_rate.amount)

    # if total_amount1 > 0:
    #     apv = AmountPerVat()
    #     apv.vat = round(total_amount1 * 19.0 / 100.0, 2)
    #     apv.incl_vat = total_amount1
    #     apv.excl_vat = round(total_amount1 - apv.vat, 2)
    #     apv.vat_definition_export_id = 1
    #     bc.amounts_per_vat_id.append(apv)

    # if total_amount2 > 0:
    #     apv = AmountPerVat()
    #     apv.vat = round(total_amount2 * 7.0 / 100.0, 2)
    #     apv.incl_vat = total_amount2
    #     apv.excl_vat = round(total_amount2 - apv.vat, 2)
    #     apv.vat_definition_export_id = 2
    #     bc.amounts_per_vat_id.append(apv)

    return bc

def get_payment(receipts):
    p = Payment()
    mapptf = lambda x: x.amounts_per_payment_type
    all_amounts_per_payment_type = list(chain.from_iterable(map(mapptf, receipts)))
    sum = lambda x, y: x + y
    p.full_amount = reduce(sum, [float(a.amount) for a in all_amounts_per_payment_type], 0.0)
    p.cash_amount = reduce(sum, [float(a.amount) for a in all_amounts_per_payment_type if a.payment_type == "CASH"], 0.0)
    
    p.cash_amounts_by_currency = []
    clause = lambda x: (x.currency_code, "Bar" if x.payment_type == "CASH" else "Unbar")
    all_amounts_per_payment_type.sort(key= clause)

    for key, group in groupby(all_amounts_per_payment_type, lambda x: x.currency_code):
        a = AmountByCurrency()
        a.currency_code = key
        c = list(group)
        # print('group: ' + key + ' val: ' + str(c))
        a.amount = reduce(sum, [float(a.amount) for a in c], 0.0)
        p.cash_amounts_by_currency.append(a)
            
    p.payment_types = []
    for key, group in groupby(all_amounts_per_payment_type, clause):
        a = AmountByCurrency()
        a.currency_code = key[0]
        a.type = key[1]
        c = list(group)
        # print('group: ' + str(key) + ' val: ' + str(c))
        a.amount = reduce(sum, [float(a.amount) for a in c], 0.0)
        p.payment_types.append(a)
            
            

    # print('test')
    # print(str([r for r in all_amounts_per_payment_type]))
    # # print(str(list(all_amounts_per_payment_type)))
    # # p.full_amount = reduce(sum_amount, [r for r in receipts])
    

    # cash_receipts = filter(lambda x: x.amounts_per_payment_type.payment_type == "CASH", receipts)
    
    # p.cash_amount = reduce(sum_amount, cash_receipts)

    return p

def get_transaction_head(receipt):
    th = TransactionHead()
    th.type = "Beleg"
    th.storno = False
    th.closing_client_id = receipt.client_id
    th.timestamp_start = receipt.time_start
    th.timestamp_end = receipt.time_end
    th.tx_id = receipt._id
    th.references = []
    if hasattr(receipt, 'metadata') and hasattr(receipt.metadata, 'order_id'):
        r = Reference()
        r.order_id = receipt.metadata.order_id
        th.references.append(r)

    # TODO fix this to a consecutive number
    th.transaction_export_id = receipt.number

    return th

def get_transaction_data(raw_receipt):
    td = TransactionData()
    receipt = get_receipt(raw_receipt) # raw_receipt.schema.standard_v1.receipt
    td.amounts_per_vat_id = receipt.amounts_per_vat_id
    sum = lambda x, y: x + y

    td.full_amount_incl_vat = reduce(sum, [x.incl_vat for x in td.amounts_per_vat_id], 0.0)
    td.payment_types = []

    for appt in receipt.amounts_per_payment_type:
        a = AmountByCurrency()
        a.currency_code = appt.currency_code
        a.type = "Bar" if appt.payment_type == "CASH" else "Unbar"
        a.amount = float(appt.amount)
        td.payment_types.append(a)

    td.lines = []

    if hasattr(receipt, 'order'): #raw_receipt.schema.standard_v1.
        # n = len(receipt.order.line_items)
        for line in receipt.order.line_items:
            # TODO: fix discounts!
            if not line.is_discount:
                td.lines.append(get_line_data(line))
            else:
                # if line.line_number == 2 and line.is_discount:
                if line.is_discount_with_vat_calculated:
                    td.lines.append(get_line_data(line))


    else:
        print('No tiene order')
        print(str(receipt))

    return td

def get_transaction_security(receipt):
    ts = TransactionSecurity()
    ts.tss_tx_id = receipt.tss_id

    return ts

def get_transactions(receipts):
    transactions = []
    for receipt in receipts:
        t = Transaction()
        t.head = get_transaction_head(receipt)
        t.data = get_transaction_data(receipt)
        t.security = get_transaction_security(receipt)

        transactions.append(t)

    return transactions

def get_cash_statement(receipts):
    cs = CashStatement()
    cs.business_cases = [
        get_business_case(receipts)
    ]
    cs.payment = get_payment(receipts)

    return cs

def get_raw_receipts(transactions):
    # ff = lambda x: hasattr(x.schema, 'standard_v1') and hasattr(x.schema.standard_v1, 'receipt')
    # mf = lambda x: x.schema.standard_v1.receipt
    # receipts = map(mf, filter(ff, transactions.data))

    return list(filter(transaction_is_receipt, transactions.data))

def get_receipt(raw_receipt):
    return raw_receipt.schema.standard_v1.receipt

def get_receipts(raw_receipts):
    # mf = lambda x: x.schema.standard_v1.receipt
    receipts = map(get_receipt, raw_receipts)

    return list(receipts)

def set_receipt_amounts_per_vat_id(raw_receipt):
    amounts_per_vat_id = []
    receipt = get_receipt(raw_receipt)

    amounts_per_vat_rate = receipt.amounts_per_vat_rate #raw_receipt.schema.standard_v1.
    for amount_per_vat_rate in amounts_per_vat_rate:
        if float(amount_per_vat_rate.amount) > 0.0:
            amounts_per_vat_id.append(AmountPerVat(amount_per_vat_rate))

    receipt.amounts_per_vat_id = amounts_per_vat_id # raw_receipt.schema.standard_v1.

def add_amounts_per_vat_id(raw_receipts):
    for r in raw_receipts:
        set_receipt_amounts_per_vat_id(r)

def build_cash_closing(transactions, options, products_provider):
    cc = CashClosing()
    cc.cash_point_closing_export_id = options["last_cash_point_closing_export_id"] + 1

    cc.client_id = get_client_id(transactions)

    cc.head = get_head(transactions)
    add_order_to_receipt(transactions, products_provider)

    # mf = lambda x: hasattr(x.schema, 'standard_v1') and hasattr(x.schema.standard_v1, 'receipt')
    # receipts = map(lambda x: x.schema.standard_v1.receipt, filter(mf, transactions.data))
    raw_receipts = get_raw_receipts(transactions)
    add_amounts_per_vat_id(raw_receipts)
    receipts = get_receipts(raw_receipts)
    # print(json.dumps(receipts.__dict__))
    # print(json.dumps(list(receipts), default=lambda s: vars(s)))
    # print(json.loads(json.dumps(list(receipts), default=lambda s: vars(s))))
    # print(str(vars(list(receipts))))
    cc.cash_statement = get_cash_statement(receipts)
    cc.transactions = get_transactions(raw_receipts)
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
            # if hasattr(tx, 'schema') and hasattr(tx.schema, 'standard_v1') and hasattr(tx.schema.standard_v1, 'order'):
            order = tx.schema.standard_v1.order
            line_number = 1
            for l in order.line_items:
                try:
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
                            l.is_discount_with_vat_calculated = False
                            continue

                    l.amount = float(l.quantity) * float(l.price_per_unit)
                    l.vat_without_discount = l.amount * l.vat # TODO we still not need this
                    
                    l.business_case = get_line_business_case(l)
                except Exception as e:
                    txt = 'Tx: ' + str(tx.number) + ' ' + str(e) + '\n'
                    print( txt)
                    raise Exception(txt)



            orders[tx._id] = order

    for tx in txs:
        if transaction_is_receipt(tx):
            # if hasattr(tx, 'schema') and hasattr(tx.schema, 'standard_v1') and hasattr(tx.schema.standard_v1, 'receipt'):
            if hasattr(tx, 'metadata') and hasattr(tx.metadata, 'order_id'):
                tx.schema.standard_v1.receipt.order = orders[tx.metadata.order_id]
