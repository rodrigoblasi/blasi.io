#!/usr/bin/python3

"""This script collects metrics from azure wvd."""

import argparse
import requests
import azure_tags
import azure_client
import azure_errors
import azure_base


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix discovery script')
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--zbx-hostname", dest="zbx_hostname",
                        help="Zabbix visible name",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: ['status']",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def get_response_status_code(response):
    """Check if the status code from API is between 200 and 202"""

    if not response.status_code in range(200, 203):
        raise SystemExit


def handle_request(url, access_token):
    """Handle the resquests in azure api for wvd"""

    payload = ""
    headers = {'Authorization': f'Bearer {access_token}'}
    querystring = {"api-version": "2021-01-14-preview"}

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)

    get_response_status_code(response)
    return response.json()


def get_host_pools(access_token, subscription_id):
    """Send the request to API and colect hostpools list"""

    url = "https://management.azure.com/subscriptions/"+subscription_id +\
        "/providers/Microsoft.DesktopVirtualization/hostPools"

    output_request = handle_request(url, access_token)
    return output_request


def get_session_host(access_token, resource_group, hostpool, subscription_id):
    """Send the request to API and colect session host list"""

    url = "https://management.azure.com/subscriptions/"+subscription_id +\
        "/resourceGroups/"+resource_group +\
        "/providers/Microsoft.DesktopVirtualization/hostPools/"+hostpool+"/sessionHosts"

    output_request = handle_request(url, access_token)
    return output_request


def handle_metric(status):
    """Function to collect session hosts metrics"""

    if status != 'Available':
        return 0
    return 1


def handle_session_host(session_hosts, zbx_hostname):
    """Function to collect the session host id and name"""

    for session_host in session_hosts:
        name = handle_session_name(session_host['name'])
        if zbx_hostname == name:
            status = session_host['properties']['status']

    return handle_metric(status)


def handle_zbx_hostname(zbx_hostname):
    """Get only the name from zabbix alias host from session host"""
    zbx_hostname = zbx_hostname.split('.')[1].strip()
    return zbx_hostname


def handle_session_name(session_name):
    """Get only the name session host"""
    session_name = session_name.split('/')[1].split('.')[0]
    return session_name.strip()


def main():
    """Main function"""

    try:
        args = parse_arguments()

        zbx_hostname = handle_zbx_hostname(args.zbx_hostname)
        args.client_name = azure_base.extract_client_name(args.client_name)
        output_authentication = azure_client.login_azure_api(args.client_name)
        access_token = output_authentication[0]
        subscription_id = output_authentication[1]

        json_hostpools = get_host_pools(access_token, subscription_id)
        output_hostpool = azure_tags.get_host_pool_by_tag(
            args.sys_id, json_hostpools)

        resource_group = output_hostpool[0]
        hostpool = output_hostpool[1]
        json_session_host = get_session_host(
            access_token, resource_group, hostpool, subscription_id)
        metric_output = handle_session_host(
            json_session_host['value'], zbx_hostname)

        print(metric_output)

    except:
        azure_errors.throws('wvd')


if __name__ == '__main__':
    main()
