#!/usr/bin/python3

"""This script collects metrics from azure Service Plan."""

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
    parser.add_argument("--interval", dest="interval", default='PT1H',
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'PT1M',
                            'PT5M',
                            'PT15M',
                            'PT30M',
                            'PT1H',
                            'PT6H',
                            'PT12H',
                            'P1D'
                        ]) + "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'BytesReceived',
                            'BytesSent',
                            'CpuPercentage',
                            'DiskQueueLength',
                            'HttpQueueLength',
                            'MemoryPercentage',
                            'SocketInboundAll',
                            'SocketLoopback',
                            'SocketOutboundAll',
                            'SocketOutboundEstablished',
                            'SocketOutboundTimeWait',
                            'TcpCloseWait',
                            'TcpClosing',
                            'TcpEstablished',
                            'TcpFinWait1',
                            'TcpFinWait2',
                            'TcpLastAck',
                            'TcpSynReceived',
                            'TcpSynSent',
                            'TcpTimeWait'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'none',
                            'average',
                            'minimum',
                            'maximum',
                            'total',
                            'count'
                        ]) + "]",
                        required=True, type=str)
    args = parser.parse_args()

    return args


def main():
    """Main function"""

    try:
        args = parse_arguments()

        credentials, subscription_id = \
            azure_client.login_azure(args.client_name)

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            "Microsoft.Web/serverFarms"
        )

        assert resource_id is not None, "Resource id not found"

        client = MonitorManagementClient(credentials, subscription_id)

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            client,
            args.interval,
            args.statistic,
        )

        assert output_metric is not None, "Metric not found"

        print(output_metric)
    except:
        azure_errors.throws('service-plan')


if __name__ == '__main__':
    main()
