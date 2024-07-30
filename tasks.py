"""
File:           tasks.py
Author:         Hugo Chavar
Created on:     10/12/23, 11:00 am

Celery tasks
"""
# from celery import shared_task
from rest_framework.exceptions import ValidationError
from django.conf import settings
from api.models import Restaurant
from .fiskaly_service import FiskalyService
from .models import FiskalyClient, ClientStates


class Task():
    client = None
    task_state = ClientStates.NOT_CREATED.value

    def __init__(self, client, service):
        self.client = client
        self.service = service
    
    def not_completed(self):
        return self.client.client_state < self.task_state
    
    def save(self):
        self.client.client_state = self.task_state
        self.client.save()

    def execute(self, data):
        pass

    def run(self, data):
        self.execute(data)
        self.client.client_state = self.task_state
        self.client.save()
        

class BillingAddressCreationTask(Task):
    
    task_state = ClientStates.BILLING_ADDRESS_CREATED.value

    def execute(self, data):
        billing_address = data.get('billing_address')
        if not billing_address:
            raise ValidationError('"billing_address" must be provided')
        response = self.service.create_billing_address(billing_address)

        self.client.vat_id_valid = response['vat_id_valid']
        self.client.billing_address_id = response['_id']


class ManagedOrganizationCreationTask(Task):

    task_state = ClientStates.ORGANIZATION_CREATED.value
    
    def execute(self, data):
        name = data.get('name')
        if not name:
            raise ValidationError('"name" must be provided')
        vat_id = data.get('vat_id')
        if not vat_id:
            raise ValidationError('"vat_id" must be provided')
        address_line1 = data.get('address_line1')
        if not address_line1:
            raise ValidationError('"address_line1" must be provided')
        country_code = data.get('country_code')
        if not country_code:
            raise ValidationError('"country_code" must be provided')
        response = self.service.create_managed_organization(data)

        self.client.organization_id = response['_id']


class ApiKeyCreationTask(Task):

    task_state = ClientStates.API_KEY_CREATED.value
    
    def execute(self, data):
        response = self.service.create_api_key(
            self.client.organization_id,
            self.client.restaurant_id
        )

        self.client.api_key = response['key']
        self.client.api_secret = response['secret']


class LoginManagedOrganizationTask(Task):

    def not_completed(self):
        return True
    
    def execute(self, data):
        self.service.credentials = self.client.get_credentials()
        self.service.update_token()

    def run(self, data):
        self.execute(data)


class TssCreationTask(Task):

    task_state = ClientStates.TSS_CREATED.value
    
    def execute(self, data):
        response = self.service.create_tss(self.client.restaurant)

        self.client.tss_id = response['_id']
        self.client.tss_state = response['state']
        self.client.tss_serial_number = response['serial_number']
        self.client.tss_admin_puk = response['admin_puk']


class TssUninitializationTask(Task):

    task_state = ClientStates.TSS_UNINITIALIZED.value
    
    def execute(self, data):
        response = self.service.tss_change_state(self.client.tss_id, "UNINITIALIZED")

        self.client.tss_state = response['state']


class TssInitializationTask(Task):

    task_state = ClientStates.TSS_INITIALIZED.value
    
    def execute(self, data):
        response = self.service.tss_change_state(self.client.tss_id, "INITIALIZED")

        self.client.tss_state = response['state']


class TssPinChangeTask(Task):

    task_state = ClientStates.TSS_PIN_CHANGED.value
    
    def execute(self, data):
        response = self.service.change_admin_pin_tss(self.client)

        self.client.tss_admin_pin = response


class LoginAdminTask(Task):

    def not_completed(self):
        return not self.service.admin_logged
    
    def execute(self, data):
        self.service.admin_auth(self.client)

    def run(self, data):
        self.execute(data)


class LogoutAdminTask(Task):

    def not_completed(self):
        return self.service.admin_logged
    
    def execute(self, data):
        self.service.admin_logout(self.client)

    def run(self, data):
        self.execute(data)


class ClientCreationTask(Task):

    task_state = ClientStates.CLIENT_CREATED.value
    
    def execute(self, data):
        response = self.service.create_client(self.client)

        self.client.fiskaly_client_id = response['_id']
        self.client.serial_number = f'{self.client.restaurant.id:08}'


class CashRegisterCreationTask(Task):

    task_state = ClientStates.CASH_REGISTER_CREATED.value
    
    def execute(self, data):
        self.service.create_cash_register(self.client, "MASTER")


# @shared_task()
def create_fiskaly_client(restaurant_id, client_data):
    """ Perform the creation of a managed organization and the client"""
    service = FiskalyService()
    service.credentials = {
        "api_key": settings.FISKALY_API_KEY,
        "api_secret": settings.FISKALY_API_SECRET
    }
    service.update_token()

    restaurant = Restaurant.objects.get(id=restaurant_id)

    client, _ = FiskalyClient.objects.get_or_create(
        restaurant=restaurant
    )
    
    # clear previous information about errors
    client.client_state_information = None

    tasks = [
        BillingAddressCreationTask(client, service),
        ManagedOrganizationCreationTask(client, service),
        ApiKeyCreationTask(client, service),
        LoginManagedOrganizationTask(client, service),
        TssCreationTask(client, service),
        TssUninitializationTask(client, service),
        TssPinChangeTask(client, service),
        LoginAdminTask(client, service),
        TssInitializationTask(client, service),
        ClientCreationTask(client, service),
        CashRegisterCreationTask(client, service),
        LogoutAdminTask(client, service)
    ]

    try:
        for task in tasks:
            if task.not_completed():
                task.run(client_data)

    except Exception as e:
        # we need to know the reason of failure
        client.client_state_information = str(e)
        client.save()

# @shared_task()
def create_fiskaly_cash_closing(restaurant_id, client_data):
    """ Perform the creation of a cash closing for a given client"""
    service = FiskalyService()
    service.credentials = {
        "api_key": settings.FISKALY_API_KEY,
        "api_secret": settings.FISKALY_API_SECRET
    }
    service.update_token()

    restaurant = Restaurant.objects.get(id=restaurant_id)

    client, _ = FiskalyClient.objects.get(
        restaurant=restaurant
    )
    
    # clear previous information about errors
    client.client_state_information = None

    options = {
        "last_cash_point_closing_export_id": client.last_cash_point_closing_export_id,
        "cash_register": "e2bc3f5a-1130-4d08-ac54-0fb6730d3963",
        "last_receipt_number": client.last_receipt_number,
    }



    client.last_receipt_number = cash_closing_obj.transactions[-1]["head"]["number"]
    client.last_cash_point_closing_export_id += 1

    client.save()

    tasks = [
        LoginManagedOrganizationTask(client, service),
    ]

    try:
        for task in tasks:
            if task.not_completed():
                task.run(client_data)

    except Exception as e:
        # we need to know the reason of failure
        client.client_state_information = str(e)
        client.save()
