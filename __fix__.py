import json
import random
from types import SimpleNamespace
from functools import reduce


class Product():
   def __init__(self, id, title, price, vat) -> None:
      self.id = id
      self.title = title
      self.price = price
      self.vat = vat

class ProductProvider():
     
    prod_dict_by_title = dict([
        ("asds", Product(1848,"asds",12,7)),
        ("50 vat", Product(1849,"50 vat",10,50)),
        ("10 vat", Product(1850,"10 vat",10,10)),
        ("sd", Product(1852,"sd",22,4)),
        ("Coffe 19", Product(1853,"Coffe 19",6,19)),
        ("Sandwich 7", Product(1854,"Sandwich 7",23,7)),
        ("Water 7", Product(1855,"Water 7",3,7)),
        ("Pizza 19", Product(1856,"Pizza 19",38,19)),
        ("Bao Pork Belly to Share", Product(1857,"Bao Pork Belly to Share",14.9,19)),
        ("Gyoza", Product(1858,"Gyoza",14.9,19)),
        ("Vegan Nooba Salad", Product(1859,"Vegan Nooba Salad",7.9,19)),
        ("Satay Gai", Product(1860,"Satay Gai",16.9,19)),
        ("Ginger Salmon", Product(1861,"Ginger Salmon",17.9,19)),
        ("Fried no shrimp", Product(1862,"Fried no shrimp",14.9,19)),
        ("Nooba Salad", Product(1863,"Nooba Salad",8,19)),
        ("HOMEMADE GINGER PANNA COTTA", Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7)),
        ("FROZEN MOCHI", Product(1865,"FROZEN MOCHI",2.9,7)),
        ("YOOTEA", Product(1866,"YOOTEA",5.9,7)),
        ("BIBIM MYUN", Product(1867,"BIBIM MYUN",29.9,7)),
        ("ALLEGRA", Product(1868,"ALLEGRA",4.7,7)),
        ("GINGER NOODLE SALAD", Product(1869,"GINGER NOODLE SALAD",21.9,7))
    ])

    prod_dict_by_id = dict([
        (1848, Product(1848,"asds",12,7)),
        (1849, Product(1849,"50 vat",10,50)),
        (1850, Product(1850,"10 vat",10,10)),
        (1852, Product(1852,"sd",22,4)),
        (1853, Product(1853,"Coffe 19",6,19)),
        (1854, Product(1854,"Sandwich 7",23,7)),
        (1855, Product(1855,"Water 7",3,7)),
        (1856, Product(1856,"Pizza 19",38,19)),
        (1857, Product(1857,"Bao Pork Belly to Share",14.9,19)),
        (1858, Product(1858,"Gyoza",14.9,19)),
        (1859, Product(1859,"Vegan Nooba Salad",7.9,19)),
        (1860, Product(1860,"Satay Gai",16.9,19)),
        (1861, Product(1861,"Ginger Salmon",17.9,19)),
        (1862, Product(1862,"Fried no shrimp",14.9,19)),
        (1863, Product(1863,"Nooba Salad",8,19)),
        (1864, Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7)),
        (1865, Product(1865,"FROZEN MOCHI",2.9,7)),
        (1866, Product(1866,"YOOTEA",5.9,7)),
        (1867, Product(1867,"BIBIM MYUN",29.9,7)),
        (1868, Product(1868,"ALLEGRA",4.7,7)),
        (1869, Product(1869,"GINGER NOODLE SALAD",21.9,7))
    ])

    def get_by_id(self, id):
        return self.prod_dict_by_id[id]

    def get_by_title(self, title):
        return self.prod_dict_by_title[title]

def get_dict(myObject):
    built_dict={}
    if not hasattr(myObject, "__dict__"):
        return myObject
    # new_subdic = vars(self)
    new_subdic = {k: v for k, v in vars(myObject).items()} # if not k.startswith('_')
    for key, value in new_subdic.items():
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool) or isinstance(value, float):
            new_subdic[key] = value
        elif isinstance(value, list):
            new_subdic[key] = [get_dict(v) for v in value]
        elif isinstance(value, object):
            new_subdic[key] = get_dict(value)
        else:
            new_subdic[key] = value
    return new_subdic


def myFunc(x):
    #   print(str(x.number))
    if hasattr(x.schema, 'standard_v1'):
        return hasattr(x.schema.standard_v1, 'receipt')
    else:
        # print(str(x.schema))
        return False

TRANSACTIONS_FILENAME = 'ListofTransactions_orig.json'
NEW_TRANSACTIONS_FILENAME = 'ListofTransactions4.json'

with open(TRANSACTIONS_FILENAME, encoding='utf-8', mode='r') as f:
    j = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

    txs = j.data
    orders_count = 0
    receipts_count = 0
    receipts = []
    orders = []

    for tx in txs:
        n = str(tx.number)
        if hasattr(tx, 'schema') and hasattr(tx.schema, 'standard_v1') and hasattr(tx.schema.standard_v1, 'receipt'):
            if tx.number not in [33]:
                receipts.append(tx)
                # tx.amount = float(tx.schema.standard_v1.receipt.amounts_per_payment_type[0].amount)
                receipts_count += 1
                # print('receipt ' + n + ' amount: ' + str(tx.amount))
                # print('Orders: ' + str(orders_count) + ' Receipts: ' + str(receipts_count))
            else:
                print('IGNORED receipt ' + n )
        elif hasattr(tx, 'schema') and hasattr(tx.schema, 'standard_v1') and hasattr(tx.schema.standard_v1, 'order'):
            
            sm = lambda x,y: x+y
            l = tx.schema.standard_v1.order.line_items
            # tx.amount = reduce(sm, [int(i.quantity)*float(i.price_per_unit) for i in l], 0.0)
            orders.append(tx)
            # print('order ' + n + ' amount: ' + str(tx.amount))
            orders_count += 1
            # print('Orders: ' + str(orders_count) + ' Receipts: ' + str(receipts_count))
        else:
            print('ERROR')

    print('-----------------')
    provider = ProductProvider()
    for i in range(51):
        r = receipts[i]
        o = orders[i]
        if not hasattr(r, 'metadata'):
            print('receipt ' + str(r.number) + 'no metadata')
        elif not hasattr(r.metadata, 'order_id'):
            # print('receipt ' + str(r.number) + 'add order id: ' + o._id)
            r.metadata.order_id = o._id 
        # else:
        #     print('receipt ' + str(r.number) + 'has order_id')
        lis = o.schema.standard_v1.order.line_items
        for li in lis:
            lv = li.text.split(' - ', 1)
            # print(str(lv))
            if len(lv) < 2 and li.text != "Discount":
                product = provider.get_by_title(li.text)

                # n = random.randint(1853, 1869)
                li.text = str(product.id) + ' - ' + li.text
                # print('*********')


        # print(str(i) + ' - order: ' + str(o.amount) + ' receipt: ' + str(r.amount))


    # print(str(j))
    print('Orders: ' + str(orders_count) + ' Receipts: ' + str(receipts_count))
    # print(cash_closing_obj.client_id)

    # # print(json.dumps(cash_closing_obj.__dict__))
    with open(NEW_TRANSACTIONS_FILENAME, encoding='utf-8', mode='w') as res:
       res.write(json.dumps(get_dict(j)))
       
    
    # print(cash_closing_obj.toJSON())
    # jo = cash_closing_obj.toJSON()
    # print(type(cash_closing_obj.get_dict()))
    # print('')
    # print(json.dumps(cash_closing_obj.get_dict()))
    # with open(NEW_TRANSACTIONS_FILENAME, encoding='utf-8', mode='w') as unf:
    #    unf.write(json.dumps(cash_closing_obj.get_dict()))

