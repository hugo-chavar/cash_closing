import json
import time
from types import SimpleNamespace
import cash_closing

class Product():
   def __init__(self, id, title, price, vat) -> None:
      self.id = id
      self.title = title
      self.price = price
      self.vat = vat

class ProductProvider():
    #  products = [
    #     Product(1853,"Coffe 19",6,19),
    #     Product(1854,"Sandwich 7",23,7),
    #     Product(1855,"Water 7",3,7),
    #     Product(1856,"Pizza 19",38,19),
    #     Product(1857,"Bao Pork Belly to Share",14.9,19),
    #     Product(1858,"Gyoza",14.9,19),
    #     Product(1859,"Vegan Nooba Salad",7.9,19),
    #     Product(1860,"Satay Gai",16.9,19),
    #     Product(1861,"Ginger Salmon",17.9,19),
    #     Product(1862,"Fried no shrimp",14.9,19),
    #     Product(1863,"Nooba Salad",8,19),
    #     Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7),
    #     Product(1865,"FROZEN MOCHI",2.9,7),
    #     Product(1866,"YOOTEA",5.9,7),
    #     Product(1867,"BIBIM MYUN",29.9,7),
    #     Product(1868,"ALLEGRA",4.7,7),
    #     Product(1869,"GINGER NOODLE SALAD",21.9,7)
    #  ]
    
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
      

TRANSACTIONS_FILENAME = 'ListofTransactions.json'
CASH_CLOSING_FILENAME = 'result2.json'
CASH_CLOSING_UNFORMATTED_FILENAME = 'resultUNF.json'

options = {
    "last_cash_point_closing_export_id": 53,
    "cash_register": "9c497ff0-4e91-472a-875b-2606fbba367a"
}

with open(TRANSACTIONS_FILENAME, encoding='utf-8', mode='r') as f:
    j = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

    # print(str(j))
    print('')

    cash_closing_obj = cash_closing.build_cash_closing(j, options, ProductProvider())
    # print(cash_closing_obj.client_id)

    # # print(json.dumps(cash_closing_obj.__dict__))
    with open(CASH_CLOSING_FILENAME, encoding='utf-8', mode='w') as res:
       res.write(cash_closing_obj.toJSON())
    
    # print(cash_closing_obj.toJSON())
    # jo = cash_closing_obj.toJSON()
    # print(type(cash_closing_obj.get_dict()))
    # print('')
    # print(json.dumps(cash_closing_obj.get_dict()))
    with open(CASH_CLOSING_UNFORMATTED_FILENAME, encoding='utf-8', mode='w') as unf:
       unf.write(json.dumps(cash_closing_obj.get_dict()))

