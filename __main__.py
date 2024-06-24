import json
import time
from types import SimpleNamespace
from product_provider import ProductProvider
import cash_closing

# class Product():
#    def __init__(self, id, title, price, vat) -> None:
#       self.id = id
#       self.title = title
#       self.price = price
#       self.vat = vat

# class ProductProvider():
#     #  products = [
#     #     Product(1853,"Coffe 19",6,19),
#     #     Product(1854,"Sandwich 7",23,7),
#     #     Product(1855,"Water 7",3,7),
#     #     Product(1856,"Pizza 19",38,19),
#     #     Product(1857,"Bao Pork Belly to Share",14.9,19),
#     #     Product(1858,"Gyoza",14.9,19),
#     #     Product(1859,"Vegan Nooba Salad",7.9,19),
#     #     Product(1860,"Satay Gai",16.9,19),
#     #     Product(1861,"Ginger Salmon",17.9,19),
#     #     Product(1862,"Fried no shrimp",14.9,19),
#     #     Product(1863,"Nooba Salad",8,19),
#     #     Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7),
#     #     Product(1865,"FROZEN MOCHI",2.9,7),
#     #     Product(1866,"YOOTEA",5.9,7),
#     #     Product(1867,"BIBIM MYUN",29.9,7),
#     #     Product(1868,"ALLEGRA",4.7,7),
#     #     Product(1869,"GINGER NOODLE SALAD",21.9,7)
#     #  ]
    
#     prod_dict_by_title = dict([
#         ("ESPRESSI", Product(13472,"ESPRESSI",2.1,7)),
#         ("DOPPIO ESPRESSI", Product(13473,"DOPPIO ESPRESSI",3.2,7)),
#         ("MILCHKAFFEE", Product(13475,"MILCHKAFFEE",3.9,7)),
#         ("LATTE MACCHIATO", Product(13476,"LATTE MACCHIATO",3.8,7)),
#         ("CAPPUCCINO", Product(13477,"CAPPUCCINO",3.7,7)),
#         ("LONG BLACK", Product(13478,"LONG BLACK",3.2,7)),
#         ("FLAT WHITE", Product(13479,"FLAT WHITE",4.2,7)),
#         ("V60 POUR-OVER", Product(13480,"V60 POUR-OVER",4.9,7)),
#         ("APOTHEKE (300 ml)", Product(13481,"APOTHEKE (300 ml)",5.1,7)),
#         ("IMMUNSHOT INGWER (100 ml)", Product(13482,"IMMUNSHOT INGWER (100 ml)",4,7)),
#         ("ORANGENSAFT (300 ml)", Product(13483,"ORANGENSAFT (300 ml)",4.4,7)),
#         ("DATES DREAM (300 ml)", Product(13484,"DATES DREAM (300 ml)",4,7)),
#         ("HOT CHOCOLATE", Product(13485,"HOT CHOCOLATE",4.2,7)),
#         ("MATCHACCINO (Hot)", Product(13486,"MATCHACCINO (Hot)",3.3,7)),
#         ("MATCHA LATTE (Hot)", Product(13487,"MATCHA LATTE (Hot)",3.8,7)),
#         ("GOLDEN MILK", Product(13488,"GOLDEN MILK",4.2,7)),
#         ("CHAI LATTE", Product(13489,"CHAI LATTE",4.2,7)),
#         ("ICED MATCHA LATTE", Product(13490,"ICED MATCHA LATTE",4.7,7)),
#         ("FRANKO® FLAT", Product(13491,"FRANKO® FLAT",3.9,7)),
#         ("FRANKO® PRESSO", Product(13492,"FRANKO® PRESSO",3.5,7)),
#         ("ICED LATTE", Product(13493,"ICED LATTE",4.5,7)),
#         ("ESPRESSO TONIC", Product(13494,"ESPRESSO TONIC",3.5,7)),
#         ("TEE GLASS", Product(13495,"TEE GLASS",3.8,7)),
#         ("GROSSE KANNE", Product(13496,"GROSSE KANNE",5.9,7)),
#         ("TUNESIAN TEA", Product(13497,"TUNESIAN TEA",5.9,7)),
#         ("AFGHANISCHER", Product(13498,"AFGHANISCHER",6.5,7)),
#         ("FRITZ-KOLA", Product(13499,"FRITZ-KOLA",3.1,7)),
#         ("FRTIZ-KOLA ZERO", Product(13500,"FRTIZ-KOLA ZERO",3.1,7)),
#         ("BIONADE NATURTRÜB  BLUTORANGE", Product(13501,"BIONADE NATURTRÜB  BLUTORANGE",3.1,7)),
#         ("FRITZ-ANJOLA", Product(13502,"FRITZ-ANJOLA",3.3,7)),
#         ("SPRUDELWASSER", Product(13503,"SPRUDELWASSER",2.5,7)),
#         ("DER MORGEN DANACH", Product(13505,"DER MORGEN DANACH",13.9,19)),
#         ("VEGGIE BRUNO", Product(13506,"VEGGIE BRUNO",13.99,19)),
#         ("DU BIST HIPSTER", Product(13507,"DU BIST HIPSTER",13.8,19)),
#         ("PARA YOK", Product(13508,"PARA YOK",11.9,19)),
#         ("BLUEBERRY VIBE", Product(13509,"BLUEBERRY VIBE",10.9,19)),
#         ("FRANKY’S COOKIES Double Chocolate", Product(13511,"FRANKY’S COOKIES Double Chocolate",3.9,7)),
#         ("Franky's Chocolate Chip Cookie", Product(13512,"Franky's Chocolate Chip Cookie",3.9,7)),
#         ("FRANKY’S COOKIES Pistazie", Product(13513,"FRANKY’S COOKIES Pistazie",3.9,7)),
#         ("ACAI BOWL", Product(13514,"ACAI BOWL",9.9,7)),
#         ("GRILLED CHEESE BRUSKETT", Product(13515,"GRILLED CHEESE BRUSKETT",12.9,19)),
#         ("SHAKSHUKA CLASSIC", Product(13518,"SHAKSHUKA CLASSIC",9.9,19)),
#         ("SHAKSHUKA MERGUEZ", Product(13519,"SHAKSHUKA MERGUEZ",10.6,19)),
#         ("PASTIRMA & EI SANDWICH", Product(13520,"PASTIRMA & EI SANDWICH",6.9,19)),
#         ("DAS SANDWICH DES FLIEGENDEN HOLLÄNDERS", Product(13521,"DAS SANDWICH DES FLIEGENDEN HOLLÄNDERS",5.8,19)),
#         ("I’M VEGAN SANDWICH", Product(13522,"I’M VEGAN SANDWICH",5.8,19)),
#         ("Ice Chai Latte", Product(13523,"Ice Chai Latte",4.5,7)),
#         ("Dirty Ice Chai Latte", Product(13524,"Dirty Ice Chai Latte",4.9,7)),
#         ("Limoncello Fresh", Product(13525,"Limoncello Fresh",5.2,7)),
#         ("Spanish Iced Latte", Product(13526,"Spanish Iced Latte",4.9,7)),
#         ("Ice Coconut Matcha", Product(13527,"Ice Coconut Matcha",5,7)),
#         ("Ice Strawberry Matcha", Product(13528,"Ice Strawberry Matcha",5,7)),
#         ("BIONADE NATURTRÜB ZITRONE", Product(13529,"BIONADE NATURTRÜB ZITRONE",3.1,7)),
#         ("BIONADE HOLUNDER", Product(13530,"BIONADE HOLUNDER",3.1,7)),
#         ("BIONADE NATURTRÜB  ORANGE", Product(13531,"BIONADE NATURTRÜB  ORANGE",3.1,7)),
#         ("PESTO SMASHED AVOCADOSTULLE  & PARMESAN", Product(13516,"PESTO SMASHED AVOCADOSTULLE  & PARMESAN",12.1,19)),
#         ("Pastrima SMASHED AVOCADOSTULLE MIT EI", Product(13517,"Pastrima SMASHED AVOCADOSTULLE MIT EI",11.9,19)),
#         ("Matcha Dose (30g für c.a 20-25 Matcha Getränke)", Product(13557,"Matcha Dose (30g für c.a 20-25 Matcha Getränke)",19.9,7)),
#         ("CORTADO", Product(13474,"CORTADO",3.2,7)),
#         ("Franky's Roll Pistazie", Product(13546,"Franky's Roll Pistazie",4.9,7)),
#         ("Franky's Roll Lemon Cheesecake", Product(13547,"Franky's Roll Lemon Cheesecake",4.9,7)),
#         ("Franky's Roll Cookie", Product(13548,"Franky's Roll Cookie",4.8,7)),
#         ("Grilled Cheese Olive", Product(13549,"Grilled Cheese Olive",5.1,7)),
#         ("Mini Franky's Roll Pistacio", Product(13550,"Mini Franky's Roll Pistacio",2.2,7)),
#         ("Mini Franky's Roll Cookie", Product(13551,"Mini Franky's Roll Cookie",2.2,7)),
#         ("Flying Turkey Grilled", Product(13552,"Flying Turkey Grilled",5.4,7)),
#         ("Grilled Pastirma Sandwich", Product(13553,"Grilled Pastirma Sandwich",5.9,7)),
#         ("Bananenbrot CHOCO (VEGAN)", Product(13558,"Bananenbrot CHOCO (VEGAN)",3.9,7)),
#         ("Banenenbrot Blueberry (VEGAN)", Product(13559,"Banenenbrot Blueberry (VEGAN)",3.9,7)),
#         ("SEIDENSTRASSE", Product(13504,"SEIDENSTRASSE",15.99,19)),
#         ("SAN SEBASTIAN CHEESECAKE", Product(13510,"SAN SEBASTIAN CHEESECAKE",4.9,7)),
#         ("Mille Feuille", Product(13600,"Mille Feuille",4,7)),
#         ("asds", Product(1848,"asds",12,7)),
#         ("50 vat", Product(1849,"50 vat",10,50)),
#         ("10 vat", Product(1850,"10 vat",10,10)),
#         ("sd", Product(1852,"sd",22,4)),
#         ("Coffe 19", Product(1853,"Coffe 19",6,19)),
#         ("Sandwich 7", Product(1854,"Sandwich 7",23,7)),
#         ("Water 7", Product(1855,"Water 7",3,7)),
#         ("Pizza 19", Product(1856,"Pizza 19",38,19)),
#         ("Bao Pork Belly to Share", Product(1857,"Bao Pork Belly to Share",14.9,19)),
#         ("Gyoza", Product(1858,"Gyoza",14.9,19)),
#         ("Vegan Nooba Salad", Product(1859,"Vegan Nooba Salad",7.9,19)),
#         ("Satay Gai", Product(1860,"Satay Gai",16.9,19)),
#         ("Ginger Salmon", Product(1861,"Ginger Salmon",17.9,19)),
#         ("Fried no shrimp", Product(1862,"Fried no shrimp",14.9,19)),
#         ("Nooba Salad", Product(1863,"Nooba Salad",8,19)),
#         ("HOMEMADE GINGER PANNA COTTA", Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7)),
#         ("FROZEN MOCHI", Product(1865,"FROZEN MOCHI",2.9,7)),
#         ("YOOTEA", Product(1866,"YOOTEA",5.9,7)),
#         ("BIBIM MYUN", Product(1867,"BIBIM MYUN",29.9,7)),
#         ("ALLEGRA", Product(1868,"ALLEGRA",4.7,7)),
#         ("GINGER NOODLE SALAD", Product(1869,"GINGER NOODLE SALAD",21.9,7))
#     ])

#     prod_dict_by_id = dict([
#         (13472, Product(13472,"ESPRESSI",2.1,7)),
#         (13473, Product(13473,"DOPPIO ESPRESSI",3.2,7)),
#         (13475, Product(13475,"MILCHKAFFEE",3.9,7)),
#         (13476, Product(13476,"LATTE MACCHIATO",3.8,7)),
#         (13477, Product(13477,"CAPPUCCINO",3.7,7)),
#         (13478, Product(13478,"LONG BLACK",3.2,7)),
#         (13479, Product(13479,"FLAT WHITE",4.2,7)),
#         (13480, Product(13480,"V60 POUR-OVER",4.9,7)),
#         (13481, Product(13481,"APOTHEKE (300 ml)",5.1,7)),
#         (13482, Product(13482,"IMMUNSHOT INGWER (100 ml)",4,7)),
#         (13483, Product(13483,"ORANGENSAFT (300 ml)",4.4,7)),
#         (13484, Product(13484,"DATES DREAM (300 ml)",4,7)),
#         (13485, Product(13485,"HOT CHOCOLATE",4.2,7)),
#         (13486, Product(13486,"MATCHACCINO (Hot)",3.3,7)),
#         (13487, Product(13487,"MATCHA LATTE (Hot)",3.8,7)),
#         (13488, Product(13488,"GOLDEN MILK",4.2,7)),
#         (13489, Product(13489,"CHAI LATTE",4.2,7)),
#         (13490, Product(13490,"ICED MATCHA LATTE",4.7,7)),
#         (13491, Product(13491,"FRANKO® FLAT",3.9,7)),
#         (13492, Product(13492,"FRANKO® PRESSO",3.5,7)),
#         (13493, Product(13493,"ICED LATTE",4.5,7)),
#         (13494, Product(13494,"ESPRESSO TONIC",3.5,7)),
#         (13495, Product(13495,"TEE GLASS",3.8,7)),
#         (13496, Product(13496,"GROSSE KANNE",5.9,7)),
#         (13497, Product(13497,"TUNESIAN TEA",5.9,7)),
#         (13498, Product(13498,"AFGHANISCHER",6.5,7)),
#         (13499, Product(13499,"FRITZ-KOLA",3.1,7)),
#         (13500, Product(13500,"FRTIZ-KOLA ZERO",3.1,7)),
#         (13501, Product(13501,"BIONADE NATURTRÜB  BLUTORANGE",3.1,7)),
#         (13502, Product(13502,"FRITZ-ANJOLA",3.3,7)),
#         (13503, Product(13503,"SPRUDELWASSER",2.5,7)),
#         (13505, Product(13505,"DER MORGEN DANACH",13.9,19)),
#         (13506, Product(13506,"VEGGIE BRUNO",13.99,19)),
#         (13507, Product(13507,"DU BIST HIPSTER",13.8,19)),
#         (13508, Product(13508,"PARA YOK",11.9,19)),
#         (13509, Product(13509,"BLUEBERRY VIBE",10.9,19)),
#         (13511, Product(13511,"FRANKY’S COOKIES Double Chocolate",3.9,7)),
#         (13512, Product(13512,"Franky's Chocolate Chip Cookie",3.9,7)),
#         (13513, Product(13513,"FRANKY’S COOKIES Pistazie",3.9,7)),
#         (13514, Product(13514,"ACAI BOWL",9.9,7)),
#         (13515, Product(13515,"GRILLED CHEESE BRUSKETT",12.9,19)),
#         (13518, Product(13518,"SHAKSHUKA CLASSIC",9.9,19)),
#         (13519, Product(13519,"SHAKSHUKA MERGUEZ",10.6,19)),
#         (13520, Product(13520,"PASTIRMA & EI SANDWICH",6.9,19)),
#         (13521, Product(13521,"DAS SANDWICH DES FLIEGENDEN HOLLÄNDERS",5.8,19)),
#         (13522, Product(13522,"I’M VEGAN SANDWICH",5.8,19)),
#         (13523, Product(13523,"Ice Chai Latte",4.5,7)),
#         (13524, Product(13524,"Dirty Ice Chai Latte",4.9,7)),
#         (13525, Product(13525,"Limoncello Fresh",5.2,7)),
#         (13526, Product(13526,"Spanish Iced Latte",4.9,7)),
#         (13527, Product(13527,"Ice Coconut Matcha",5,7)),
#         (13528, Product(13528,"Ice Strawberry Matcha",5,7)),
#         (13529, Product(13529,"BIONADE NATURTRÜB ZITRONE",3.1,7)),
#         (13530, Product(13530,"BIONADE HOLUNDER",3.1,7)),
#         (13531, Product(13531,"BIONADE NATURTRÜB  ORANGE",3.1,7)),
#         (13516, Product(13516,"PESTO SMASHED AVOCADOSTULLE  & PARMESAN",12.1,19)),
#         (13517, Product(13517,"Pastrima SMASHED AVOCADOSTULLE MIT EI",11.9,19)),
#         (13557, Product(13557,"Matcha Dose (30g für c.a 20-25 Matcha Getränke)",19.9,7)),
#         (13474, Product(13474,"CORTADO",3.2,7)),
#         (13546, Product(13546,"Franky's Roll Pistazie",4.9,7)),
#         (13547, Product(13547,"Franky's Roll Lemon Cheesecake",4.9,7)),
#         (13548, Product(13548,"Franky's Roll Cookie",4.8,7)),
#         (13549, Product(13549,"Grilled Cheese Olive",5.1,7)),
#         (13550, Product(13550,"Mini Franky's Roll Pistacio",2.2,7)),
#         (13551, Product(13551,"Mini Franky's Roll Cookie",2.2,7)),
#         (13552, Product(13552,"Flying Turkey Grilled",5.4,7)),
#         (13553, Product(13553,"Grilled Pastirma Sandwich",5.9,7)),
#         (13558, Product(13558,"Bananenbrot CHOCO (VEGAN)",3.9,7)),
#         (13559, Product(13559,"Banenenbrot Blueberry (VEGAN)",3.9,7)),
#         (13504, Product(13504,"SEIDENSTRASSE",15.99,19)),
#         (13510, Product(13510,"SAN SEBASTIAN CHEESECAKE",4.9,7)),
#         (13600, Product(13600,"Mille Feuille",4,7)),
#         (1848, Product(1848,"asds",12,7)),
#         (1849, Product(1849,"50 vat",10,50)),
#         (1850, Product(1850,"10 vat",10,10)),
#         (1852, Product(1852,"sd",22,4)),
#         (1853, Product(1853,"Coffe 19",6,19)),
#         (1854, Product(1854,"Sandwich 7",23,7)),
#         (1855, Product(1855,"Water 7",3,7)),
#         (1856, Product(1856,"Pizza 19",38,19)),
#         (1857, Product(1857,"Bao Pork Belly to Share",14.9,19)),
#         (1858, Product(1858,"Gyoza",14.9,19)),
#         (1859, Product(1859,"Vegan Nooba Salad",7.9,19)),
#         (1860, Product(1860,"Satay Gai",16.9,19)),
#         (1861, Product(1861,"Ginger Salmon",17.9,19)),
#         (1862, Product(1862,"Fried no shrimp",14.9,19)),
#         (1863, Product(1863,"Nooba Salad",8,19)),
#         (1864, Product(1864,"HOMEMADE GINGER PANNA COTTA",6.9,7)),
#         (1865, Product(1865,"FROZEN MOCHI",2.9,7)),
#         (1866, Product(1866,"YOOTEA",5.9,7)),
#         (1867, Product(1867,"BIBIM MYUN",29.9,7)),
#         (1868, Product(1868,"ALLEGRA",4.7,7)),
#         (1869, Product(1869,"GINGER NOODLE SALAD",21.9,7))
#     ])

#     def get_by_id(self, id):
#         return self.prod_dict_by_id[id]

#     def get_by_title(self, title):
#         return self.prod_dict_by_title[title]
      

TRANSACTIONS_FILENAME = 'merged_file_filter1.json'
CASH_CLOSING_FILENAME = 'result2_prod_8.json'
CASH_CLOSING_UNFORMATTED_FILENAME = 'resultUNF_prod_0.json'

options = {
    "last_cash_point_closing_export_id": 0,
    "cash_register": "e2bc3f5a-1130-4d08-ac54-0fb6730d3963",
    "last_receipt_number": 0,
}

print(f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} ")

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

