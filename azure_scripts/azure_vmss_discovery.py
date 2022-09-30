#!/usr/bin/python3

"""This script collects metrics from azure Virtual Machine Scale Sets(VMSS)."""

import argparse
import json
import requests
import azure_tags
import azure_client
import azure_errors
import azure_base

URL_DEFAULT = "https://management.azure.com/subscriptions/"


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
    parser.add_argument("--kind", dest="kind",
                        help="Discovery type based in the metric. \
                         Available: ['cluster','instance']",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def handle_request(url, access_token):
    """Handle the resquests in azure api for vmss"""

    payload = ""
    headers = {'Authorization': f'Bearer {access_token}'}
    querystring = {"api-version": "2021-04-01"}

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)

    get_response_status_code(response)
    return response.json()


def get_response_status_code(response):
    """Check if the status code from API is between 200 and 202"""

    if not response.status_code in range(200, 203):
        raise SystemExit


def get_cluster_information(access_token, subscription_id):
    """Send the request to API and the resourceID"""

    url = URL_DEFAULT+subscription_id +\
        "/providers/Microsoft.Compute/virtualMachineScaleSets"

    output_request = handle_request(url, access_token)

    return output_request


def get_instances_names(access_token, resource_id):
    """Send the request to API and the resourceID"""

    url = "https://management.azure.com" + resource_id + "/virtualMachines"

    output_request = handle_request(url, access_token)
    return output_request


def handle_vmss(access_token, resource_id):
    """Function to collect the instances names"""

    instances_names = []
    instances = get_instances_names(access_token, resource_id)

    for instance in instances['value']:
        instances_names.append(instance['name'])
    return instances_names


def handle_discovery_instances(instances_name, resource_id, vmss_name):
    """Output for zabbix discovery"""

    dict_output = {}
    dict_output['data'] = []
    for instance in instances_name:
        dict_output['data'].append(
            {"{#VMSSNAME}": vmss_name,
             "{#INSTANCENAME}": instance,
             "{#RESOURCEID}": resource_id})

    dict_output = json.dumps(dict_output)
    return dict_output


def handle_discovery_cluter(resource_id, cluster_name):
    """Function that structures the cluster name output for zabbix"""

    dict_output = {}
    dict_output['data'] = [
        {"{#VMSSNAME}": cluster_name, "{#RESOURCEID}": resource_id}]
    dict_output = json.dumps(dict_output)
    return dict_output


def main():
    """Main function"""

    try:
        args = parse_arguments()

        args.client_name = azure_base.extract_client_name(args.client_name)
        output_authentication = azure_client.login_azure_api(args.client_name)
        access_token = output_authentication[0]
        subscription_id = output_authentication[1]

        vmss_cluster = get_cluster_information(access_token, subscription_id)
        vmss_cluster = azure_tags.get_vmss_info_by_tag(
            args.sys_id, vmss_cluster)

        resource_id = vmss_cluster[0]
        vmss_name = vmss_cluster[1]

        if args.kind == 'cluster':
            discovery_output = handle_discovery_cluter(resource_id, vmss_name)
        if args.kind == 'instance':
            instances_name = handle_vmss(access_token, resource_id)
            discovery_output = handle_discovery_instances(
                instances_name, resource_id, vmss_name)

        print(discovery_output)

    except:
        azure_errors.throws('vmss')


if __name__ == '__main__':
    main()
