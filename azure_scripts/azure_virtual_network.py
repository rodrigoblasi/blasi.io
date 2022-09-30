#!/usr/bin/python3

"""This script collects metrics from azure Virtual Network."""

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
    parser.add_argument("--file-system", dest="file_system",
                        help="", default=None,
                        required=False, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--interval", dest="interval", default='PT5M',
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'PT1M',
                            'PT5M',
                            'PT15M',
                            'PT30M',
                            'PT1H',
                            'PT6H',
                            'PT12H',
                            'P1D']) +
                        "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'PingMeshAverageRoundtripMs',
                            'PingMeshProbesFailedPercent',
                            'PacketsInDDoS',
                            'PacketsDroppedDDoS',
                            'PacketsForwardedDDoS',
                            'TCPPacketsInDDoS',
                            'TCPPacketsDroppedDDoS',
                            'TCPPacketsForwardedDDoS',
                            'UDPPacketsInDDoS',
                            'UDPPacketsDroppedDDoS',
                            'UDPPacketsForwardedDDoS',
                            'BytesInDDoS',
                            'BytesDroppedDDoS',
                            'BytesForwardedDDoS',
                            'TCPBytesInDDoS',
                            'TCPBytesDroppedDDoS',
                            'TCPBytesForwardedDDoS',
                            'UDPBytesInDDoS',
                            'UDPBytesDroppedDDoS',
                            'UDPBytesForwardedDDoS',
                            'IfUnderDDoSAttack',
                            'DDoSTriggerTCPPackets',
                            'DDoSTriggerUDPPackets',
                            'DDoSTriggerSYNPackets']) +
                        "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'maximum',
                            'average'
                        ]) +
                        "]",
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

        resource_id = azure_tags.get_network_id_by_tag(
            args.sys_id, credentials, subscription_id, "Network01-RG")

        assert resource_id is not None, "Resource_id not found"

        client = MonitorManagementClient(
            credentials,
            subscription_id
        )

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            client,
            args.interval,
            args.statistic,
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)
    except:
        azure_errors.throws('virtual-network')


if __name__ == '__main__':
    main()
