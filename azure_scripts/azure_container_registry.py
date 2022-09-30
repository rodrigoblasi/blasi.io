#!/usr/bin/python3
"""This script collects metrics from azure container registry."""
import argparse
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description="Azure Metrics Zabbix discovery script"
    )
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str,
                        )
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str,
                        )
    parser.add_argument("--interval", dest="interval", default="PT5M",
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'PT1M',
                            'PT5M',
                            'PT15M',
                            'PT30M']) +
                        "]",
                        required=False, type=str,
                        )
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'TotalPullCount',
                            'SuccessfulPullCount',
                            'TotalPushCount',
                            'SuccessfulPushCount',
                            'RunDuration',
                            'AgentPoolCPUTime',
                            'StorageUsed']) +
                        "]",
                        required=True, type=str,
                        )
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'count',
                            'total',
                            'average',
                            'maximum',
                            'minimum',
                            'none']) +
                        "]",
                        required=True, type=str,
                        )
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
            args.sys_id, credentials, subscription_id, 'Microsoft.ContainerRegistry/registries')

        assert resource_id is not None, "Resource_id not found"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            MonitorManagementClient(credentials, subscription_id),
            args.interval,
            args.statistic.lower()
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)

    except:
        azure_errors.throws("container-registry")


if __name__ == "__main__":
    main()
