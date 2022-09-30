#!/usr/bin/python3

"""This script collects metrics from azure FILE SHARE."""
import argparse
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_file_share script')
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str)
    parser.add_argument("--file-system", dest="file_system",
                        help="", default=None,
                        required=False, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--interval", dest="interval", default='PT1H',
                        help="Azure availables intervals: ['PT1M','PT5M',\
                            'PT15M', 'PT30M', 'PT1H', 'PT6H', 'PT12H', 'P1D']",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [ 'UsedCapacity','FileCapacity'\
                        'FileCount','FileShareCapacityQuota','FileShareCount',\
                        'FileShareProvisionedIOPS', 'FileShareSnapshotCount', \
                        'FileShareSnapshotSize', 'Transactions', 'Ingress', 'Egress',\
                        'SuccessServerLatency', 'SuccessE2ELatency', 'Availability']",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: ['total','average',\
                            'maximum', 'minimum']",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def main():
    """Main function"""

    try:
        args = parse_arguments()

        args.client_name = azure_base.extract_client_name(args.client_name)
        output_authentication = azure_client.login_azure(args.client_name)
        credentials = output_authentication[0]
        subscription_id = output_authentication[1]

        resource_id = azure_tags.get_storage_id_by_tag(args.sys_id,
                                                       credentials, subscription_id)

        assert resource_id is not None, "Resource Id Not Found"

        client = MonitorManagementClient(
            credentials,
            subscription_id
        )

        if args.file_system is not None:
            resource_id += f"/fileServices/{args.file_system}"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            client,
            args.interval,
            args.statistic
        )

        print(output_metric)
    except:
        azure_errors.throws('file-share')


if __name__ == '__main__':
    main()
