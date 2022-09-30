#!/usr/bin/python3

"""This script collects metrics from azure Container Instance."""

import argparse
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
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
    parser.add_argument("--interval", dest="interval", default='PT5M',
                        help="Azure availables intervals: ['PT1M','PT5M', 'PT15M', 'PT30M']",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: ['CpuUsage','MemoryUsage']",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: ['average']",
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

        resource_id = azure_tags.get_resource_id_by_tag(args.sys_id,\
            credentials,subscription_id,'Microsoft.ContainerInstance/containerGroups')

        client = MonitorManagementClient(
            credentials,
            subscription_id
        )

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            client,
            args.interval,
            args.statistic
        )
        print(output_metric)

    except:
        azure_errors.throws('container-instance')


if __name__ == '__main__':
    main()
