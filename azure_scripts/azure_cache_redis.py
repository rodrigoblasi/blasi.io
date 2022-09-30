#!/usr/bin/python3

"""This script collects metrics from Azure Cache Redis."""
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
        description='Azure Metrics Zabbix azure_cache_redis script')
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
                            'PT12H'
                        ]) + "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'cachehits',
                            'cacheLatency',
                            'cachemisses',
                            'cachemissrate',
                            'cacheRead',
                            'cacheWrite',
                            'connectedclients',
                            'errors',
                            'evictedkey',
                            'operationsPerSecond',
                            'serverLoad',
                            'totalcommandsprocessed',
                            'totalkeys',
                            'usedmemory',
                            'usedmemorypercentage'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'count',
                            'total',
                            'average',
                            'minimum',
                            'maximum'
                        ]) + "]",
                        required=True, type=str)
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

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            ["Microsoft.Cache/Redis", "Microsoft.Cache/RedisEnterprise"]
        )

        client = MonitorManagementClient(credentials, subscription_id)

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            client,
            args.interval,
            args.statistic,
            timespan
        )

        print(output_metric)

    except:
        azure_errors.throws('cache-redis')


if __name__ == '__main__':
    main()
