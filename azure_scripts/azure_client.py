#!/usr/bin/python3

"""This script authenticates into microsoft azure"""

import configparser
import requests
from azure.identity import DefaultAzureCredential, ClientSecretCredential


def collect_client_credentials(client_name):
    """Function to colect the client credentials"""

    conf_file_path = f"/usr/lib/zabbix/externalscripts/conf/azure_{client_name}.conf"
    with open(conf_file_path, "r") as conf_file:
        config = configparser.ConfigParser()
        config.read_file(conf_file)

        account_name = config.sections()[0]
        subscription_id = config.get(account_name, 'subscription_id')
        tenant_id = config.get(account_name, 'tenant_id')
        client_id = config.get(account_name, 'client_id')
        client_secret = config.get(account_name, 'client_secret')

    return tenant_id, client_id, client_secret, subscription_id


def login_azure(client_name):
    """Login function"""

    client_account = collect_client_credentials(client_name)

    credential = DefaultAzureCredential()

    credential = ClientSecretCredential(
        tenant_id=client_account[0],
        client_id=client_account[1],
        client_secret=client_account[2]
    )

    return credential, client_account[3]


def resquest_azure_http(client_name):
    """Send the request to API and colect token"""

    client_account = collect_client_credentials(client_name)

    grant_type = "grant_type=client_credentials"
    tenant_id = client_account[0]
    client_id = "client_id="+client_account[1]
    client_secret = "client_secret="+client_account[2]
    subscription_id = client_account[3]
    resource = "resource=https://management.azure.com"

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

    payload = "&".join([grant_type, client_id, client_secret, resource])
    headers = {'Content-Type': "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, data=payload, headers=headers)
    return response, subscription_id


def login_azure_api(client_name):
    """Login function directly"""

    request = resquest_azure_http(client_name)
    json_response = request[0]
    subscription_id = request[1]

    if not json_response.status_code in range(200, 203):
        raise SystemExit

    access_token = json_response.json()['access_token']

    return access_token, subscription_id


if __name__ == '__main__':
    print("Please use another script to call it.")
