"""
File:           models.py
Author:         Hugo Chavar
Created on:     08/11/23, 09:30 am
"""
# from django.db import models
# from django.contrib.auth import get_user_model
from enum import Enum
from unittest.mock import Mock
from constants import BASE_TIMESTAMP

# from api.models.base_model import BaseModel
# from api.models.restaurant import Restaurant

import time
import math

import os
from dotenv import load_dotenv

load_dotenv()

ENV_LAST_CC_EXPORT_ID = "LAST_CASH_POINT_CLOSING_EXPORT_ID"
ENV_LAST_RECEIPT_NUMBER = "LAST_RECEIPT_NUMBER"
ENV_LAST_PROCESSED_TX_NUMBER = "LAST_PROCESSED_TX_NUMBER"
ENV_API_KEY = "API_KEY"
ENV_API_SECRET = "API_SECRET"
ENV_TSS_ID = "TSS_ID"
ENV_CASH_REGISTER_ID = "CASH_REGISTER_ID"

LAST_CASH_POINT_CLOSING_EXPORT_ID = os.getenv(ENV_LAST_CC_EXPORT_ID)
LAST_RECEIPT_NUMBER = os.getenv(ENV_LAST_RECEIPT_NUMBER)
LAST_PROCESSED_TX_NUMBER = os.getenv(ENV_LAST_PROCESSED_TX_NUMBER)
API_KEY = os.getenv(ENV_API_KEY)
API_SECRET = os.getenv(ENV_API_SECRET)
TSS_ID = os.getenv(ENV_TSS_ID)
CASH_REGISTER_ID = os.getenv(ENV_CASH_REGISTER_ID)


# User = get_user_model()

class ClientStates(Enum):
    NOT_CREATED = 0
    BILLING_ADDRESS_CREATED = 1
    ORGANIZATION_CREATED = 2
    API_KEY_CREATED = 3
    TSS_CREATED = 4
    TSS_UNINITIALIZED = 5
    TSS_PIN_CHANGED = 6
    TSS_INITIALIZED = 7
    CLIENT_CREATED = 8
    CASH_REGISTER_CREATED = 9


 
## Mocked version

# def get_credentials(self):
#     return {
#         "api_key": str(self.api_key),
#         "api_secret": str(self.api_secret)
#     }


# def get_refresh_credentials(self):
#     return {
#         "refresh_token": self.refresh_token
#     }


FiskalyClient = Mock()
FiskalyClient.objects = Mock()

# Add a method to the mock object
def get(self, id):
    if id == 1:
        mock_obj = Mock(
            id=1,
            restaurant = None,
            fiskaly_client_id = None,
            serial_number = None,
            tss_id = TSS_ID,
            tss_serial_number = None,
            tss_state = None,
            tss_admin_puk = None,
            tss_admin_pin = None,
            client_state = None,
            organization_id = None,
            billing_address_id = None,
            api_key = API_KEY,
            api_secret = API_SECRET,
            vat_id_valid = None,
            client_state_information = None,
            access_token = None,
            access_token_expires_at = None,
            refresh_token = None,
            refresh_token_expires_at = None,
            last_processed_tx_number = LAST_PROCESSED_TX_NUMBER,
            base_timestamp = BASE_TIMESTAMP,
            last_cash_point_closing_export_id =  LAST_CASH_POINT_CLOSING_EXPORT_ID, # default = 0
            last_receipt_number = LAST_RECEIPT_NUMBER, # default = 0
            cash_register = CASH_REGISTER_ID # TODO: add this to the model
            # get_credentials=get_credentials.__get__(self, type(self))
            # get_credentials= lambda self: {
            #     "api_key": self.api_key,
            #     "api_secret": self.api_secret                
            # }
        )
        mock_obj.get_credentials = lambda: {
            "api_key": mock_obj.api_key,
            "api_secret": mock_obj.api_secret
        }
        return mock_obj
    else:
        raise Exception('Object not found')

FiskalyClient.objects.get = get.__get__(FiskalyClient.objects, type(FiskalyClient.objects))


