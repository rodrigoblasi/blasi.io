#!/usr/bin/python3

"""This script collects metrics from Azure bastion."""
import argparse
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base
from azure_discovery import discovery


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_bastion script')
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str)

    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)

    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'Availability',
                            'SaturationShoebox', 'ServiceApiLatency',
                            'ServiceApiHit'
                        ]) + "]",
                        required=False, default=None, type=str)

    parser.add_argument("--dimensions", dest="dimensions",
                        help="dimensions",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def main():
    """Main function"""

    try:
        args = parse_arguments()
        args.client_name = azure_base.extract_client_name(args.client_name)
        credentials, subscription_id = \
            azure_client.login_azure(args.client_name)

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id,
            credentials,
            subscription_id,
            "Microsoft.network/bastionHosts"
        )

        assert resource_id is not None, "Resource_id not found"

        client = MonitorManagementClient(credentials, subscription_id)

        dimensions = discovery(args, resource_id, client)

        assert dimensions is not None, "Dimensions not found"

        print(dimensions)

    except Exception as ex:
        if ex.__class__ != SystemExit:
            azure_errors.throws('bastion')


if __name__ == '__main__':
    main()
