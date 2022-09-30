#!/usr/bin/python3

"""
This script contains the logic to discover all dimensions
from any Azure components
"""

import copy
import json
import azure_errors

def get_dimensions(client, resource_id, args):
    """Function to collect the dimensions metrics"""
    values = [{}]
    for dimension in args.dimensions:
        new_values = []
        for value in values:
            metric_filter = build_filter(dimension, value)
            possible_values = request_dimension(
                client,
                resource_id,
                args.metric_name,
                metric_filter)
            assert len(possible_values) > 0, "Dimension without values"
            for possible_value in possible_values:
                new_value = copy.deepcopy(value)
                new_value.update({dimension: possible_value})
                new_values.append(new_value)
        values = new_values

    return values


def build_filter(dim, val):
    """Function to create the filter"""
    filters = []
    for dimension in val:
        filters.append(f"{dimension} eq '{val[dimension]}'")
    filters.append(f"{dim} eq '*'")

    return " and ".join(filters)


def request_dimension(client, resource_id, metric, metric_filter):
    """This function do a request to API for collect the dimensions values"""
    try:
        metrics_data = client.metrics.list(
            resource_id,
            metricnames=metric,
            result_type="metadata",
            filter=metric_filter
        )

        return list(
            map(
                lambda meta: meta.value, metrics_data.value[0].timeseries[0].metadatavalues)
            )
    except:
        return []


def format_zabbix_key(key):
    """Format the output for zabbix, replacing - for _ and uppercasing the string"""
    zabbix_key = key.upper().replace("-", "_")
    return f"{{#{zabbix_key}}}"


def format_output(dimensions_list):
    """Format the output to json"""
    new_list = []
    for dimensions in dimensions_list:
        new_list.append(dict((format_zabbix_key(k), v)
                        for k, v in dimensions.items()))
    return json.dumps({"data": new_list})


def get_metric(client, resource_id, dimensions):
    """Gets the first metric which has all requested dimensions"""
    definitions = client.metric_definitions.list(resource_id)

    definition = next(definitions)
    while definition:
        metric_dimensions = list(
            map(lambda dimension: dimension.value, definition.dimensions))
        if all(dimension in metric_dimensions for dimension in dimensions):
            return definition.name.value
        definition = next(definitions)

    return None

def discovery(args, resource_id, client):
    """Discovery function"""
    try:
        args.dimensions = args.dimensions.split('+')

        if args.metric_name is None:
            args.metric_name = get_metric(client, resource_id, args.dimensions)

        dimensions = get_dimensions(client, resource_id, args)

    except:
        azure_errors.throws('discovery')

    assert dimensions is not None, "No dimension was found."
    return format_output(dimensions)

if __name__ == '__main__':
    print("Favor utilizar outro script para chamar esse.")
