"""
File:           fiskaly_service.py
Author:         Hugo Chavar
Created on:     07/11/23, 4:27 pm
"""
import requests
import uuid

from rest_framework.exceptions import ValidationError
from django.conf import settings


class FiskalyService():
    token = ""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ''
    }
    admin_logged = False

    credentials = {}
    

    def new_guid(self):
        return str(uuid.uuid4())


    def auth(self):
        url = f"{settings.FISKALY_URL}/auth"

        return self.send_request("POST", url, self.credentials)


    def update_token(self):
        data = self.auth()
        self.token = data["access_token"]


    def admin_auth(self, fiskaly_client):
        
        url = f"{settings.FISKALY_URL}/tss/{fiskaly_client.tss_id}/admin/auth"

        payload = {
            "admin_pin": fiskaly_client.tss_admin_pin
        }

        self.send_request("POST", url, payload)
        self.admin_logged = True


    def admin_logout(self, fiskaly_client):
        
        url = f"{settings.FISKALY_URL}/tss/{fiskaly_client.tss_id}/admin/logout"

        self.send_request("POST", url, {})
        self.admin_logged = False


    def send_request(self, type, url, payload):
        errors = ['fiskaly errors occured', url]
        retry = True
        times = 0
        while retry and times < 3:
            self.headers["Authorization"] = f'Bearer {self.token}'
            try:
                response = requests.request(type, url, headers=self.headers, json=payload)
            except Exception as e:
                errors.append("Failed to establish a connection to Fiskaly service")
                errors.append(str(e))
                break

            times += 1
            data = response.json()
            
            if not response.ok:
                errors.append(response.text)
                error_code = data.get("code")
                error_name = data.get("error")
                retry = False
                if response.status_code == 401:
                    if error_code == "E_UNAUTHORIZED" or error_name == "Unauthorized":
                        self.auth()
                        retry = True
                        continue

                else:
                    retry = False
                
            else:
                return data
        
        raise ValidationError(errors)


    def create_tss(self, restaurant):
        guid = self.new_guid()
        url = f"{settings.FISKALY_URL}/tss/{guid}"

        payload = {
            "metadata": {
                "name": restaurant.name,
                "restaurant_id": restaurant.id
            }
        }

        return self.send_request("PUT", url, payload)


    def tss_change_state(self, tss_id, state):
        url = f"{settings.FISKALY_URL}/tss/{tss_id}"

        payload = {
            "state": state
        }

        return self.send_request("PATCH", url, payload)


    def change_admin_pin_tss(self, fiskaly_client):
        url = f"{settings.FISKALY_URL}/tss/{fiskaly_client.tss_id}/admin"

        payload = {
            "admin_puk": fiskaly_client.tss_admin_puk,
            "new_admin_pin": settings.FISKALY_TSS_ADMIN_PIN
        }

        self.send_request("PATCH", url, payload)

        return settings.FISKALY_TSS_ADMIN_PIN


    def create_client(self, client):
        guid = self.new_guid()
        url = f"{settings.FISKALY_URL}/tss/{client.tss_id}/client/{guid}"

        restaurant = client.restaurant
        payload = {
            "serial_number": f'{restaurant.id:08}',
            "metadata": {
                "name": restaurant.name,
                "restaurant_id": restaurant.id
            }
        }

        return self.send_request("PUT", url, payload)


    def create_cash_register(self, client, type):
        url = f"{settings.FISKALY_DSFINVK_URL}/cash_registers/{client.fiskaly_client_id}"

        restaurant = client.restaurant
        payload = {
            "base_currency_code": restaurant.currency.code,
            "brand": "Doyo",
            "model": "POS",
            "cash_register_type": {
                "type": type,
                "tss_id": str(client.tss_id)
            },
            "software": {
                "brand": "Doyo",
                "version": "1"
            },
            "metadata": {
                "name": restaurant.name,
                "id": restaurant.id
            }
        }

        return self.send_request("PUT", url, payload)


    def create_billing_address(self, billing_address):
        url = f"{settings.FISKALY_ADMIN_URL}/billing-addresses"

        return self.send_request("POST", url, billing_address)


    def create_managed_organization(self, organization):
        url = f"{settings.FISKALY_ADMIN_URL}/organizations"
        organization['managed_by_organization_id'] = settings.FISKALY_ORG_ID
        del organization['billing_address']
        
        return self.send_request("POST", url, organization)


    def create_api_key(self, org_id, restaurant_id):
        url = f"{settings.FISKALY_ADMIN_URL}/organizations/{org_id}/api-keys"

        payload = {
            "name": f"{restaurant_id:04}",
            "status": "enabled",
            "managed_by_organization_id": settings.FISKALY_ORG_ID
        }

        return self.send_request("POST", url, payload)
    
    def build_params_string(self, n_limit, n_offset):
        """Builds a parameters string based on given limit and offset values.

        Args:
            n_limit (int or None): The limit value.
            n_offset (int or None): The offset value.

        Returns:
            str: The parameters string.
        """

        params = []
        if n_limit is not None:
            params.append(f"limit={n_limit}")
        if n_offset is not None:
            params.append(f"offset={n_offset}")

        return "&".join(params)

    def get_transactions(self, fiskaly_client, limit=None, offset=None):
        
        url = f"{settings.FISKALY_URL}/tss/{fiskaly_client.tss_id}/tx?{self.build_params_string(limit, offset)}"

        return self.send_request("GET", url, {})
