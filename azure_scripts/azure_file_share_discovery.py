#!/usr/bin/python3

"""This script collects metrics from azure FILE SHARE."""

import json
import argparse
import azure_errors
import azure_client
import azure_tags
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
    args = parser.parse_args()

    return args


def output_format(file_services):
    """Parsed the output to get the metric"""
    output = {
        "data": []
    }
    for service in file_services:
        output["data"].append({"{#FILE_SYSTEM}": service})

    return json.dumps(output)


def main():
    """Main function"""

    try:
        args = parse_arguments()

        args.client_name = azure_base.extract_client_name(args.client_name)
        output_authentication = azure_client.login_azure(args.client_name)
        credentials = output_authentication[0]
        subscription_id = output_authentication[1]

        file_services = azure_tags.get_files_services_by_id(args.sys_id,
                                                            credentials, subscription_id)
        output = output_format(file_services)

        print(output)
    except:
        azure_errors.throws('file-share')


if __name__ == '__main__':
    main()
