#!/usr/bin/python3

"""This script collects metrics from azure CosmosDB."""

import argparse
import re
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base

dimensions_allowed = [
    {
        "value": "ResourceName",
        "localizedValue": "resource_name"
    },
    {
        "value": "ChildResourceName",
        "localizedValue": "child_resource_name"
    },
    {
        "value": "DatabaseName",
        "localizedValue": "database_name"
    },
    {
        "value": "CollectionName",
        "localizedValue": "collection_name"
    },
    {
        "value": "Region",
        "localizedValue": "region"
    },
    {
        "value": "StatusCode",
        "localizedValue": "status_code"
    },
    {
        "value": "OperationType",
        "localizedValue": "operation_type"
    },
    {
        "value": "ResourceType",
        "localizedValue": "resource_type"
    },
    {
        "value": "ErrorCode",
        "localizedValue": "error_code"
    },
    {
        "value": "CommandName",
        "localizedValue": "command_name"
    },
    {
        "value": "Status",
        "localizedValue": "status"
    },
    {
        "value": "ConnectionMode",
        "localizedValue": "connection_mode"
    },
    {
        "value": "PublicAPIType",
        "localizedValue": "public_api_type"
    },
    {
        "value": "KeyType",
        "localizedValue": "key_type"
    },
    {
        "value": "CacheExercised",
        "localizedValue": "cache_exercised"
    },
    {
        "value": "OperationName",
        "localizedValue": "operation_name"
    },
    {
        "value": "ClosureReason",
        "localizedValue": "closure_reason"
    },
    {
        "value": "PartitionKeyRangeId",
        "localizedValue": "partition_key_range_id"
    },
    {
        "value": "NotStarted",
        "localizedValue": "not_started"
    },
    {
        "value": "ReplicationInProgress",
        "localizedValue": "replication_in_progress"
    },
    {
        "value": "SourceRegion",
        "localizedValue": "source_region"
    },
    {
        "value": "TargetRegion",
        "localizedValue": "target_region"
    },
    {
        "value": "DiagnosticSettingsName",
        "localizedValue": "diagnostic_settings_name"
    },
    {
        "value": "ResourceGroupName",
        "localizedValue": "resource_group_name"
    },
    {
        "value": "TargetContainerName",
        "localizedValue": "target_container_name"
    }
]


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
                            'P1D']) +
                        "]",
                        required=False, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join([
                            'AddRegion',
                            'AutoscaleMaxThroughput',
                            'AvailableStorage',
                            'CassandraConnectionClosures',
                            'CassandraConnectorAvgReplicationLatency',
                            'CassandraConnectorReplicationHealthStatus',
                            'CassandraKeyspaceCreate',
                            'CassandraKeyspaceDelete',
                            'CassandraKeyspaceThroughputUpdate',
                            'CassandraKeyspaceUpdate',
                            'CassandraRequestCharges',
                            'CassandraRequests',
                            'CassandraTableCreate',
                            'CassandraTableDelete',
                            'CassandraTableThroughputUpdate',
                            'CassandraTableUpdate',
                            'CreateAccount',
                            'DataUsage',
                            'DeleteAccount',
                            'DocumentCount',
                            'DocumentQuota',
                            'GremlinDatabaseCreate',
                            'GremlinDatabaseDelete',
                            'GremlinDatabaseThroughputUpdate',
                            'GremlinDatabaseUpdate',
                            'GremlinGraphCreate',
                            'GremlinGraphDelete',
                            'GremlinGraphThroughputUpdate',
                            'GremlinGraphUpdate',
                            'IndexUsage',
                            'MetadataRequests',
                            'MongoCollectionCreate',
                            'MongoCollectionDelete',
                            'MongoCollectionThroughputUpdate',
                            'MongoCollectionUpdate',
                            'MongoDatabaseDelete',
                            'MongoDatabaseThroughputUpdate',
                            'MongoDBDatabaseCreate',
                            'MongoDBDatabaseUpdate',
                            'MongoRequestCharge',
                            'MongoRequests',
                            'MongoRequestsCount',
                            'MongoRequestsDelete',
                            'MongoRequestsInsert',
                            'MongoRequestsQuery',
                            'MongoRequestsUpdate',
                            'NormalizedRUConsumption',
                            'ProvisionedThroughput',
                            'RegionFailover',
                            'RemoveRegion',
                            'ReplicationLatency',
                            'ServerSideLatency',
                            'ServiceAvailability',
                            'SqlContainerCreate',
                            'SqlContainerDelete',
                            'SqlContainerThroughputUpdate',
                            'SqlContainerUpdate',
                            'SqlDatabaseCreate',
                            'SqlDatabaseDelete',
                            'SqlDatabaseThroughputUpdate',
                            'SqlDatabaseUpdate',
                            'TableTableCreate',
                            'TableTableDelete',
                            'TableTableThroughputUpdate',
                            'TableTableUpdate',
                            'TotalRequests',
                            'TotalRequestUnits',
                            'UpdateAccountKeys',
                            'UpdateAccountNetworkSettings',
                            'UpdateAccountReplicationSettings',
                            'UpdateDiagnosticsSettings']) +
                        "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'count',
                            'total',
                            'average',
                            'maximum,']) +
                        "]",
                        required=True, type=str)
    parser.add_argument("--resource-name", dest="resource_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--child-resource-name", dest="child_resource_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--database-name", dest="database_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--collection-name", dest="collection_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--region", dest="region",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--status-code", dest="status_code",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--operation-type", dest="operation_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--resource-type", dest="resource_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--error-code", dest="error_code",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--command-name", dest="command_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--status", dest="status",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--connection-mode", dest="connection_mode",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--public-api-type", dest="public_api_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--key-type", dest="key_type",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--cache-exercised", dest="cache_exercised",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--operation-name", dest="operation_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--closure-reason", dest="closure_reason",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--partition-key-range-id", dest="partition_key_range_id",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--not-started", dest="not_started",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--replication-in-progress", dest="replication_in_progress",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--source-region", dest="source_region",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--target-region", dest="target_region",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--diagnostic-settings-name", dest="diagnostic_settings_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--resource-group-name", dest="resource_group_name",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--target-container-name", dest="target_container_name",
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

    try:
        args = parse_arguments()
        dimensions_filter = create_dimensions_filter(args)
        args.client_name = azure_base.extract_client_name(args.client_name)

        credentials, subscription_id = \
            azure_client.login_azure(args.client_name)

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            "Microsoft.DocumentDB/DatabaseAccounts")

        assert resource_id is not None, "Resource_id not found"

        output_metric = azure_base.component_handler(
            resource_id,
            args.metric_name,
            MonitorManagementClient(credentials, subscription_id),
            args.interval,
            args.statistic,
            None,
            dimensions_filter
        )

        assert output_metric is not None, "Output_metric not found"

        print(output_metric)
    except:
        azure_errors.throws('cosmos-db')


if __name__ == '__main__':
    main()
