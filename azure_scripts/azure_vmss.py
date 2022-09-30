#!/usr/bin/python3

"""This script collects metrics from azure Virtual Machine Scale Sets(VMSS)."""

import argparse
import requests
import azure_client
import azure_errors
import azure_vmss_discovery
import azure_base


def parse_arguments():
    """Arguments function"""

    parser = argparse.ArgumentParser(
        description='Azure Metrics Zabbix discovery script')
    parser.add_argument("--resource-id", dest="resource_id",
                        help="Resource id of the managed vmss",
                        required=True, type=str)
    parser.add_argument("--client-name", dest="client_name",
                        help="Represents the name of the client inserted in zabbix macro",
                        required=True, type=str)
    parser.add_argument("--metric-name", dest="metric_name",
                        help="Azure availables metrics - cluster:['CPU_Credits_Consumed, \
                            CPU_Credits_Remaining,Disk_Read_Bytes,Disk_Write_Bytes, \
                            Network_Out_Total,Network_In_Total,Percentage_CPU'] \
                            instance:['Disk_Read_Bytes,Disk_Write_Bytes, \
                            Network_Out_Total,Network_In_Total,Percentage_CPU']",
                        required=True, type=str)
    parser.add_argument("--statistic", dest="statistic",
                        help="Azure availables statistics: ['average, total']",
                        required=True, type=str)
    parser.add_argument("--interval", dest="interval", default='PT5M',
                        help="Azure availables intervals: ['PT1M','PT5M', 'PT15M', 'PT30M']",
                        required=False, type=str)
    parser.add_argument("--instance-name", dest="instance_name",
                        help="Azure instance name from virtual Machine Scale Sets.",
                        required=False, type=str)
    args = parser.parse_args()

    return args


def request_metric(access_token, resource_id, querystring):
    """Request metric"""

    url_default = "https://management.azure.com"
    url = url_default + resource_id + "/providers/microsoft.insights/metrics"

    payload = ""
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)

    azure_vmss_discovery.get_response_status_code(response)
    return response.json()


def handle_metric(json_metric, aggregation):
    """Filter the exactly output metric"""

    output = json_metric['value'][0]['timeseries'][0]['data'][-1]
    if aggregation in output:
        output = output[aggregation]
        return round(output)
    return 0


def convert_metric(metric):
    """Removes the '_' to spaces"""

    formatted_metric = metric.replace('_', ' ')
    return formatted_metric


def main():
    """Main function"""

    try:
        args = parse_arguments()

        args.client_name = azure_base.extract_client_name(args.client_name)
        output_authentication = azure_client.login_azure_api(args.client_name)
        access_token = output_authentication[0]

        params = {
            "interval": args.interval,
            "metricnames": convert_metric(args.metric_name),
            "aggregation": args.statistic
        }

        if args.instance_name:
            query = f"VMName eq '{args.instance_name}'"
            params.update({"$filter": query})

        params.update({"api-version": "2019-07-01"})

        output_metric = request_metric(access_token, args.resource_id, params)
        output_metric = handle_metric(output_metric, args.statistic)
        print(output_metric)

    except:
        azure_errors.throws('vmss')


if __name__ == '__main__':
    main()
