#!/usr/bin/python3
"""This script collects metrics from azure dedicated sql pool."""
import argparse
from datetime import date, timedelta, datetime
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base

metrics = [
    'app_cpu_percent',
    'physical_data_read_percent',
    'connection_successful',
    'connection_failed',
    'blocked_by_firewall',
    'dwu_limit',
    'dwu_consumption_percent',
    'dwu_used',
    'cache_hit_percent',
    'cache_used_percent',
    'local_tempdb_usage_percent',
    'app_memory_percent',
    'active_queries',
    'queued_queries',
    'allocated_data_storage',
    'app_cpu_billed',
    'base_blob_size_bytes',
    'cpu_limit',
    'cpu_percent',
    'cpu_used',
    'deadlock',
    'delta_num_of_bytes_read',
    'delta_num_of_bytes_total',
    'delta_num_of_bytes_written',
    'diff_backup_size_bytes',
    'dtu_consumption_percent',
    'dtu_limit',
    'dtu_used',
    'full_backup_size_bytes',
    'log_backup_size_bytes',
    'log_write_percent',
    'memory_usage_percent',
    'sessions_percent',
    'snapshot_backup_size_bytes',
    'sqlserver_process_core_percent',
    'sqlserver_process_memory_percent',
    'armazenamento',
    'storage_percent',
    'tempdb_data_size',
    'tempdb_log_size',
    'tempdb_log_used_percent',
    'wlg_active_queries',
    'wlg_active_queries_timeouts',
    'wlg_allocation_relative_to_system_percent',
    'wlg_allocation_relative_to_wlg_effective_cap_percent',
    'wlg_effective_cap_resource_percent',
    'wlg_effective_min_resource_percent',
    'wlg_queued_queries',
    'workers_percent',
    'xtp_storage_percent'
]


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
                        required=False, type=str,
                        )
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join(metrics) +
                        "]",
                        required=True,
                        type=str,
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
    parser.add_argument("--isuserdefined", dest="IsUserDefined",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--workloadgroupname", dest="WorkloadGroupName",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def create_dimensions_filter(args):
    """create dimensions filter function"""
    dimensions = [
        "IsUserDefined",
        "WorkloadGroupName"
    ]

    dimensions_filter = []
    for dimension in dimensions:
        if getattr(args, dimension) is not None:
            dimensions_filter.append(
                f"{dimension} eq '{getattr(args, dimension)}'")

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

        resurse_type = "Microsoft.Sql/servers/databases"

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            resurse_type)

        assert resource_id is not None, "Resource_id not found"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            MonitorManagementClient(credentials, subscription_id),
            args.interval,
            args.statistic.lower(),
            timespan,
            dimensions_filter
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)
    except:
        azure_errors.throws("dedicated-sql-pool")


if __name__ == "__main__":
    main()
