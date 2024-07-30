"""
File:           models.py
Author:         Hugo Chavar
Created on:     08/11/23, 09:30 am
"""
from django.db import models
from django.contrib.auth import get_user_model
from enum import Enum

from api.models.base_model import BaseModel
from api.models.restaurant import Restaurant

import time
import math

User = get_user_model()

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



class FiskalyClient(BaseModel):
    """ Store the fiskaly client information """
    restaurant = models.OneToOneField(
        Restaurant, on_delete=models.CASCADE
    )
    fiskaly_client_id = models.UUIDField(null=True)
    serial_number = models.CharField(null=True, max_length=70)
    tss_id = models.UUIDField(null=True)
    tss_serial_number = models.CharField(null=True, max_length=70)
    tss_state = models.CharField(null=True, max_length=20)
    tss_admin_puk = models.CharField(null=True, max_length=20)
    tss_admin_pin = models.CharField(null=True, max_length=20)
    client_state = models.PositiveSmallIntegerField(null=False, default=0)
    organization_id = models.UUIDField(null=True)
    billing_address_id = models.UUIDField(null=True)
    api_key = models.CharField(null=True, max_length=70)
    api_secret = models.CharField(null=True, max_length=70)
    
    # Fiskaly confirmation that VAT data is Ok
    vat_id_valid = models.BooleanField(default=False)
    
    client_state_information = models.TextField(null=True)
    access_token = models.TextField(null=True)
    access_token_expires_at = models.PositiveBigIntegerField(null=True)
    refresh_token = models.TextField(null=True)
    refresh_token_expires_at = models.PositiveBigIntegerField(null=True)
    cash_register = models.UUIDField(null=True)
    last_cash_point_closing_export_id = models.PositiveIntegerField(null=False, default=0)
    last_receipt_number  = models.PositiveIntegerField(null=False, default=0)


    def get_credentials(self):
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret
        }


    def get_refresh_credentials(self):
        return {
            "refresh_token": self.refresh_token
        }


    def is_creation_complete(self):
        return self.client_state == ClientStates.CASH_REGISTER_CREATED.value


    def access_token_expires_in(self):
        time_rounded = int(math.ceil(time.time() / 100.0)) * 100
        return  self.access_token_expires_at - time_rounded


    def refresh_token_expires_in(self):
        time_rounded = int(math.ceil(time.time() / 100.0)) * 100
        return self.refresh_token_expires_at - time_rounded


