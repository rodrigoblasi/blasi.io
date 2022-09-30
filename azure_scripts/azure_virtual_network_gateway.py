#!/usr/bin/python3

"""This script collects metrics from Azure Virtual Network Gateway."""
import argparse
from datetime import date, timedelta, datetime
from azure.mgmt.monitor import MonitorManagementClient
import azure_client
import azure_tags
import azure_errors
import azure_base

metrics = [
    'AverageBandwidth',
    'BgpPeerStatus',
    'BgpRoutesAdvertised',
    'BgpRoutesLearned',
    'ExpressRouteGatewayBitsPerSecond',
    'ExpressRouteGatewayCountOfRoutesAdvertisedToPeer',
    'ExpressRouteGatewayCountOfRoutesLearnedFromPeer',
    'ExpressRouteGatewayCpuUtilization',
    'ExpressRouteGatewayFrequencyOfRoutesChanged',
    'ExpressRouteGatewayNumberOfVmInVnet',
    'ExpressRouteGatewayPacketsPerSecond',
    'MmsaCount',
    'P2SBandwidth',
    'P2SConnectionCount',
    'QmsaCount',
    'TunnelAverageBandwidth',
    'TunnelEgressBytes',
    'TunnelEgressPacketDropCount',
    'TunnelEgressPacketDropTSMismatch',
    'TunnelEgressPackets',
    'TunnelIngressBytes',
    'TunnelIngressPacketDropCount',
    'TunnelIngressPacketDropTSMismatch',
    'TunnelIngressPackets',
    'TunnelNatAllocations',
    'TunnelNatedBytes',
    'TunnelNatedPackets',
    'TunnelNatFlowCount',
    'TunnelNatPacketDrop',
    'TunnelPeakPackets',
    'TunnelReverseNatedBytes',
    'TunnelReverseNatedPackets',
    'TunnelTotalFlowCount',
    'UserVpnRouteCount',
    'VnetAddressPrefixCount'
]


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix azure_virtual_network_gateway script')
    parser.add_argument("--sys-id", dest="sys_id",
                        help="Represents the CI in service now",
                        required=True, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics: [" +
                        ", ".join(metrics) + "]",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: [" +
                        ", ".join([
                            'average', 'maximum', 'total'
                        ]) + "]",
                        required=True, type=str)
    parser.add_argument("--interval", dest="interval", default='PT1H',
                        help="Azure availables intervals: [" +
                        ", ".join([
                            'PT1M', 'PT5M', 'PT15M', 'PT30M',
                             'PT1H', 'PT6H', 'PT12H', 'PT1D'
                        ]) + "]",
                        required=False, type=str)

    parser.add_argument("--instance", dest="Instance",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--bgppeeraddress", dest="BgpPeerAddress",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--roleinstance", dest="roleInstance",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--connectionname", dest="ConnectionName",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--remoteip", dest="RemoteIP",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--protocol", dest="Protocol",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--flowtype", dest="FlowType",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--droptype", dest="DropType",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--routetype", dest="RouteType",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    parser.add_argument("--natrule", dest="NatRule",
                        help="<Optional> Metric dimension to be collected",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def create_dimensions_filter(args):
    """create dimensions filter function"""
    dimensions = [
        "Instance",
        "BgpPeerAddress",
        "roleInstance",
        "ConnectionName",
        "RemoteIP",
        "Protocol",
        "FlowType",
        "DropType",
        "RouteType",
        "NatRule"
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

        resource_id = azure_tags.get_id_by_tag(
            args.sys_id, credentials, subscription_id,
            "microsoft.network/virtualnetworkgateways"
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

    except Exception as ex:
        azure_errors.throws('virtual-network-gateway')


if __name__ == '__main__':
    main()
