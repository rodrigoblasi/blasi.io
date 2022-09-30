#!/usr/bin/python3

"""This script collects metrics from Azure Logic App."""
import argparse
from datetime import date, timedelta, datetime
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base

metrics = [
    'AppConnections',
    'AverageMemoryWorkingSet',
    'AverageResponseTime',
    'BytesReceived',
    'BytesSent',
    'CpuTime',
    'CurrentAssemblies',
    'FileSystemUsage',
    'FunctionExecutionCount',
    'FunctionExecutionUnits',
    'Gen0Collections',
    'Gen1Collections',
    'Gen2Collections',
    'Alças',
    'HealthCheckStatus',
    'Http101',
    'Http2xx',
    'Http3xx',
    'Http401',
    'Http403',
    'Http404',
    'Http406',
    'Http4xx',
    'Http5xx',
    'HttpResponseTime',
    'IoOtherBytesPerSecond',
    'IoOtherOperationsPerSecond',
    'IoReadBytesPerSecond',
    'IoReadOperationsPerSecond',
    'IoWriteBytesPerSecond',
    'IoWriteOperationsPerSecond',
    'MemoryWorkingSet',
    'PrivateBytes',
    'Requests',
    'RequestsInApplicationQueue',
    'Threads',
    'TotalAppDomains',
    'TotalAppDomainsUnloaded'
]


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_logic_app script')
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--interval", dest="interval", default='PT1H',
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'PT1M', 'PT5M', 'PT15M', 'PT30M',
                            'PT1H', 'PT6H', 'PT12H', 'PT1D'
                        ]) + "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join(metrics) + "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'average', 'total'
                        ]) + "]",
                        required=True, type=str)

    parser.add_argument("--instance", dest="instance",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def main():
    """Main function"""

    end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_time = (date.today() - timedelta(1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    timespan = f"{start_time}/{end_time}"

    try:
        args = parse_arguments()
        args.client_name = azure_base.extract_client_name(args.client_name)

        credentials, subscription_id = \
            azure_client.login_azure(args.client_name)

        resource_type = "Microsoft.web/sites"

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            resource_type
        )

        assert resource_id is not None, "Resource_id not found"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            MonitorManagementClient(credentials, subscription_id),
            args.interval,
            args.statistic,
            timespan
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)

    except:
        azure_errors.throws('logic-app')


if __name__ == '__main__':
    main()
