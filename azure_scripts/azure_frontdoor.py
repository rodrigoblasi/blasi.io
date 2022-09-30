#!/usr/bin/python3

"""This script collects metrics from Azure Frontdoor."""
import argparse
import re
from datetime import date, timedelta, datetime
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base

dimensions_allowed = [
    {
        "value": "HttpStatus",
        "localizedValue": "http_status"
    },
    {
        "value": "HttpStatusGroup",
        "localizedValue": "http_status_group"
    },
    {
        "value": "ClientRegion",
        "localizedValue": "client_region"
    },
    {
        "value": "ClientCountry",
        "localizedValue": "client_country"
    },
    {
        "value": "Backend",
        "localizedValue": "backend"
    },
    {
        "value": "BackendPool",
        "localizedValue": "backend_pool"
    },
    {
        "value": "PolicyName",
        "localizedValue": "policy_name"
    },
    {
        "value": "RuleName",
        "localizedValue": "rule_name"
    },
    {
        "value": "Action",
        "localizedValue": "action"
    }
]


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_frontdoor script')
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
                            'PT1D'
                        ]) + "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'BackendHealthPercentage',
                            'BackendRequestCount',
                            'BackendRequestLatency',
                            'RequestCount',
                            'RequestSize',
                            'ResponseSize',
                            'TotalLatency',
                            'WebApplicationFirewallRequestCount'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'average',
                            'minimum',
                            'maximum',
                            'total',
                            'none',
                            'count'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--http-status", dest="http_status",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--http-status-group", dest="http_status_group",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--client-region", dest="client_region",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--client-country", dest="client_country",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--backend", dest="backend",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--backend-pool", dest="backend_pool",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--policy-name", dest="policy_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--rule-name", dest="rule_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--action", dest="action",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def create_dimensions_filter(args):
    """create dimensions filter function"""
    argument = args.__dict__
    dimensions_filter = ""
    for dimensions in dimensions_allowed:
        if argument[dimensions['localizedValue']] is not None:
            dimensions_name = dimensions['value']
            dimensions_value = argument[dimensions['localizedValue']]
            dimensions_filter += f"{dimensions_name} eq '{dimensions_value}' and "

    return re.sub(" and $", "", dimensions_filter) if dimensions_filter != "" else None


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
            "Microsoft.Network/frontdoors"
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
        azure_errors.throws('frontdoors')


if __name__ == '__main__':
    main()
