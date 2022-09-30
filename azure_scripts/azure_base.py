#!/usr/bin/python3

"""This script collects the tags from the components and check the sys id's"""

import re


def component_handler(resource_id, metric, client, interval, aggregation, timespan=None, dimensions_filter=None):
    """Function to collect the component metrics"""
    metrics_data = client.metrics.list(
        resource_id,
        interval=interval,
        metricnames=metric,
        aggregation=aggregation,
        timespan=timespan,
        filter=dimensions_filter
    ) if timespan is not None else \
        client.metrics.list(
            resource_id,
            interval=interval,
            metricnames=metric,
            aggregation=aggregation,
            filter=dimensions_filter
    )
    output = metrics_data.value[0].timeseries[0].data[-1]
    output = output.as_dict()
    output = output[aggregation]
    return round(output)


def convert_to_bytes(number):
    """Function to convert to Byte"""

    byte_output = ""
    units = ['KB', 'MB', 'GB', 'TB', 'PB']
    switcher = {
        'B': 1,
        'KB': 1024,
        'MB': 1048576,
        'GB': 1073741824,
        'TB': 1099511627776,
        'PB': 1125899906842624
    }

    for unit in units:
        if unit in number:
            unit_value = switcher.get(unit, "Conversion does not exist!")
            byte_output = number.replace(unit, '')
            byte_output = float(re.sub(r'[,]', '', byte_output)) * unit_value
            return round(byte_output)
    return ""


def remove_underscore(metric):
    """Removes the '_' to spaces"""

    formatted_metric = metric.replace('_', ' ')
    return formatted_metric


def extract_client_name(client_name):
    """Get the value from client_name variable and return only the client name"""

    client_name = client_name.split(".")
    return client_name[0].lower()


if __name__ == '__main__':
    print("Favor utilizar outro script para chamar esse.")
