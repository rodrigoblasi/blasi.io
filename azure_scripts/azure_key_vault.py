#!/usr/bin/python3

"""This script collects metrics from Azure Key Vault."""
import argparse
from datetime import date, timedelta, datetime
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_key_vault script')
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
                        ", ".join([
                            'None', 'Availability',
                            'SaturationShoebox', 'ServiceApiLatency',
                            'ServiceApiHit'
                        ]) + "]",
                        required=True, type=str)

    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'average', 'minimum', 'maximum',
                            'total', 'count'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--activity-type", dest="activity_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--activity-name", dest="activity_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--status-code", dest="status_code",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--status-code-class", dest="status_code_class",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--transaction-type", dest="transaction_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def create_dimensions_filter(args):
    """create dimensions filter function"""
    dimensions = [
        "activity_type",
        "activity_name",
        "status_code",
        "status_code_class",
        "transaction_type"
    ]

    dimensions_filter = []
    for dimension in dimensions:
        if getattr(args, dimension) is not None:
            dimensions_filter.append(f"{dimension} eq '{getattr(args, dimension)}'")

    return " and ".join(dimensions_filter) if len(dimensions_filter) > 0 else None


def main():
    """Main function"""

    end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_time = (date.today() - timedelta(1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    timespan = f"{start_time}/{end_time}"

    try:
        args = parse_arguments()
        dimensions_filter = create_dimensions_filter(args)
        args.client_name = azure_base.extract_client_name(args.client_name)

        credentials, subscription_id = \
            azure_client.login_azure(args.client_name)

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            "Microsoft.KeyVault/vaults"
        )

        assert resource_id is not None, "Resource_id not found"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            MonitorManagementClient(credentials, subscription_id),
            args.interval,
            args.statistic,
            timespan,
            dimensions_filter
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)

    except:
        azure_errors.throws('key-vault')


if __name__ == '__main__':
    main()
