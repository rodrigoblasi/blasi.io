#!/usr/bin/python3

"""This script collects the tags from the components and check the sys id's"""

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.dns import DnsManagementClient


def get_id_by_tag(sys_id, credentials, subscription_id, resource_type):
    """Generic function to get an id given a sys-id and resource type"""

    client = ResourceManagementClient(credentials, subscription_id)
    print("peguei o client")
    resource_type_list = resource_type if isinstance(resource_type, list) \
        else [resource_type]
    print("peguei o resource_type_list")
    for r_type in resource_type_list:
        resources = client.resources.list(filter=f"resourceType eq '{r_type}'")
        print("r_type")
        for resource in resources:
            print("olhado resource")
            print(resource)
            if resource.tags is not None:
                print("tenho tag")
                lower_tags = dict((key.lower(), val)
                                  for key, val in resource.tags.items())
                if 'sys_id' in lower_tags and lower_tags['sys_id'] == sys_id:
                    return resource.id
    print("vou ternar none")
    return 


def list_resources_groups(resource_client):
    """Function list all resources in azure"""

    groups = resource_client.resource_groups.list()
    resource_groups_list = []

    for resource_group in list(groups):
        resource_groups_list.append(resource_group.name)

    return resource_groups_list


def get_resource_id_by_tag(sys_id, credentials, subscription_id, resource_type):
    """Function to get the database resource id by filtering the SYS_ID tag."""

    resource_client = ResourceManagementClient(credentials, subscription_id)

    resource_groups_list = list_resources_groups(resource_client)

    for resource_group in resource_groups_list:
        resource_list = resource_client.resources.list_by_resource_group(
            resource_group,
            filter=f"resourceType eq '{resource_type}'"
        )
        for resource in list(resource_list):
            if 'SYS_ID' in str(resource) and resource.tags['SYS_ID'] == sys_id:
                return resource.id
    return ""


def list_storages_accounts(storage_client):
    """Function list all storages in azure"""

    accounts = storage_client.storage_accounts.list()
    storage_accounts_list = []

    for storage_account in list(accounts):
        if storage_account.name == 'filesharemonitorzbx':
            print(".")
        storage_accounts_list.append(storage_account.name)

    return storage_accounts_list


def get_storage_id_by_tag(sys_id, credentials, subscription_id):
    """Function to get the database storage id by filtering the SYSID tag."""

    storage_client = StorageManagementClient(credentials, subscription_id)

    accounts = storage_client.storage_accounts.list()

    for storage_account in list(accounts):
        labels = storage_account.tags
        lower_labels = dict((k.lower(), v) for k, v in labels.items())
        for resource in list(lower_labels):
            if 'sys_id' in str(resource) and lower_labels['sys_id'] == sys_id:
                return storage_account.id
    return ""


def get_files_services_by_id(sys_id, credentials, subscription_id):
    """Function to get the database storage id by filtering the SYSID tag."""

    storage_client = StorageManagementClient(credentials, subscription_id)

    resource_id = get_storage_id_by_tag(sys_id, credentials, subscription_id)

    resource_group_name = resource_id.split('/')[4]
    account_name = resource_id.split('/')[8]
    services = storage_client.file_services.list(
        resource_group_name, account_name)
    data = []
    for service in services.value:
        data.append(service.name)

    return data


def get_network_id_by_tag(sys_id, credentials, subscription_id, resource_group_name):
    """Function to get the database storage id by filtering the SYS_ID tag."""

    network_client = NetworkManagementClient(credentials, subscription_id)
    accounts = list(network_client.virtual_networks.list(resource_group_name))

    while accounts:
        network_account = accounts.pop().as_dict()
        labels = network_account['tags']
        lower_labels = dict((k.lower(), v) for k, v in labels.items())
        for resource in list(lower_labels):
            if 'sys_id' in str(resource) and lower_labels['sys_id'] == sys_id:
                return network_account['id']
        return ""


def get_dns_id_by_tag(sys_id, credentials, subscription_id):
    """Function to get the database storage id by filtering the SYSID tag."""

    dns_client = DnsManagementClient(credentials, subscription_id)
    zones = list(dns_client.zones.list())

    while zones:
        zone = zones.pop().as_dict()
        labels = zone['tags']
        lower_labels = dict((k.lower(), v) for k, v in labels.items())
        for resource in list(lower_labels):
            if 'sys_id' in str(resource) and lower_labels['sys_id'] == sys_id:
                return zone['id']
    return ""


def get_host_pool_by_tag(sys_id, json_hostpools):
    """Function to get the resource group and host pool by sys id tag"""

    for hostpool in json_hostpools['value']:
        if hostpool['tags'].get('SYS_ID') == sys_id:
            hostpool_name = hostpool['name']
            resource_group = hostpool['id'].split('/')[4]
            return resource_group, hostpool_name
    return ""


def get_file_share_id_by_tag(sys_id, json_file_shares):
    """Function to get the resource group and host pool by sys id tag"""

    database_id = json_file_shares['id'].split('/')[2]
    labels = json_file_shares['tags']
    lower_labels = dict((k.lower(), v) for k, v in labels.items())
    if lower_labels['sysid'] == sys_id:
        return database_id
    return ""


def get_cluster_info_by_tag(sys_id, clusters):
    """Function to get the resource group by sys id tag"""

    for cluster in clusters['value']:
        if 'SYS_ID' in cluster['tags'] and cluster['tags'].get('SYS_ID') == sys_id:
            resource = cluster['id']
            name = cluster['name']
            node_resource_group = cluster['properties']['nodeResourceGroup']
            return resource, node_resource_group, name
    return ""


def get_vmss_info_by_tag(sys_id, vmss_cluster):
    """Function to get the resource group by sys id tag"""

    for vmss in vmss_cluster['value']:
        if 'SYS_ID' in vmss['tags'] and vmss['tags'].get('SYS_ID') == sys_id:
            resource = vmss['id']
            name = vmss['name']
            return resource, name
    return ""


if __name__ == '__main__':
    print("Favor utilizar outro script para chamar esse.")
