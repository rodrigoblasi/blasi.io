#!/usr/bin/python3

"""This script contain the error dictionary """

error_dictionary = {
    "mariadb": -1,
    "mysql": -2,
    "wvd": -3,
    "sql-managed-instances": -4,
    "site-to-site-vpn": -5,
    "application-gateway": -6,
    "storage-account": -7,
    "express-route": -8,
    "container-instance": -9,
    "sql-database": -10,
    "cdn": -11,
    "aks": -12,
    "vmss": -13,
    "traffic": -14,
    "nat-gateway": -15,
    "load-balancer": -16,
    "managed-disks": -17,
    "file-share": -18,
    "virtual-network": -19,
    "dns": -20,
    "firewall": -21,
    "cache-redis": -22,
    "postgresql-database": -23,
    "service-plan": -24,
    "webapp": -25,
    "dedicated-sql-pool": -26,
    "cosmos-db": -27,
    "frontdoors": -28,
    "container-registry": -29,
    "key-vault": -30,
    "automation-account": -31,
    "bastion": -32,
    "logic-app": -33,
    "virtual-network-gateway": -34,
    "azure-client": -101,
    "discovery": -102
}


def throws(error_component):
    """Raise error"""

    print(error_dictionary.get(error_component))
    raise SystemExit


if __name__ == '__main__':
    print("Favor utilizar outro script para chamar esse.")
