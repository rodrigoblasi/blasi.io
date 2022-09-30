#!/usr/bin/python3

"""This script collects metrics from azure AKS."""

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
                        help="Discovery type based in the metric. Available: ['cluster','node']",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def handle_request(url, access_token):
    """Handle the resquests in azure api for aks"""

    payload = ""
    headers = {'Authorization': f'Bearer {access_token}'}
    querystring = {"api-version": "2021-03-01"}

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
        "/providers/Microsoft.ContainerService/managedClusters"

    output_request = handle_request(url, access_token)

    return output_request


def get_vmss_id(vmss, agent_pools):
    """Gets the VM ID """

    vmss_name_agent_pool = []
    for agent_pool in agent_pools:
        for vm_name in vmss['value']:
            if vm_name['tags']['poolName'] == agent_pool:
                vmss_name_agent_pool.append(
                    {"name": vm_name['name'], "poolName": agent_pool})
    return vmss_name_agent_pool


def handle_output_vmss(vmss_json):
    """Manage the json output from get get_vmss_names"""

    vmss_array = []
    for vm_name in vmss_json['value']:
        vmss_array.append(vm_name['name'])
    return vmss_array


def get_vmss_names(access_token, subscription_id, resource_group):
    """Send the request to API and the resourceID"""

    url = URL_DEFAULT + subscription_id + "/resourceGroups/" + \
        resource_group + \
        "/providers/Microsoft.Compute/virtualMachineScaleSets"

    output_request = handle_request(url, access_token)
    response = handle_output_vmss(output_request)
    return response


def get_nodes_names(access_token, subscription_id, resource_group, vmss_name):
    """Send the request to API and the resourceID"""

    url = URL_DEFAULT + subscription_id + "/resourceGroups/" + \
        resource_group + \
        "/providers/Microsoft.Compute/virtualMachineScaleSets/" + \
        vmss_name + "/virtualMachines"

    output_request = handle_request(url, access_token)
    return output_request


def handle_vmss(vmss_name, access_token, subscription_id, node_resource_group):
    """Function to collect the nodes names by poolname"""

    nodes_names = []
    for vm_name in vmss_name:
        nodes = get_nodes_names(
            access_token, subscription_id, node_resource_group, vm_name)
        for node in nodes['value']:
            nodes_names.append(node['properties']['osProfile']['computerName'])
    return nodes_names


def handle_discovery_nodes(nodes_names, resource_id, cluster_name):
    """Output for zabbix discovery"""

    dict_output = {}
    dict_output['data'] = []
    for node in nodes_names:
        dict_output['data'].append(
            {"{#CLUSTERNAME}": cluster_name,
             "{#NODENAME}": node,
             "{#RESOURCEID}": resource_id})

    dict_output = json.dumps(dict_output)
    return dict_output


def handle_discovery_cluter(resource_id, cluster_name):
    """Function that structures the cluster name output for zabbix"""

    dict_output = {}
    dict_output['data'] = [
        {"{#CLUSTERNAME}": cluster_name, "{#RESOURCEID}": resource_id}]
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

        aks_information = get_cluster_information(
            access_token, subscription_id)
        aks_information = azure_tags.get_cluster_info_by_tag(
            args.sys_id, aks_information)

        resource_id = aks_information[0]
        node_resource_group = aks_information[1]
        cluster_name = aks_information[2]

        if args.kind == 'cluster':
            discovery_output = handle_discovery_cluter(
                resource_id, cluster_name)
        if args.kind == 'node':
            vmss_name = get_vmss_names(
                access_token, subscription_id, node_resource_group)
            node_name = handle_vmss(
                vmss_name, access_token, subscription_id, node_resource_group)
            discovery_output = handle_discovery_nodes(
                node_name, resource_id, cluster_name)

        print(discovery_output)

    except:
        azure_errors.throws('aks')


if __name__ == '__main__':
    main()
