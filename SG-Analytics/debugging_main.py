import argparse
from DB_Connector import DBConnector as dbc
from ip_db_copier import IP_DB_Copier as ipdc
import openpyxl
import pandas as pd
import paramiko as pmk


def parse_device():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_IP", nargs='+', required=True,
                        help="IP address of the SG devices")
    args = parser.parse_args()
    device_IPs = args.device_IP
    devices = {}
    for item in device_IPs:
        name, ip = item.split('=', 1)
        devices[name] = ip
    return devices

# If the program is running in the main file, then:
if __name__ == "__debugging_main__":
    devices = parse_device()
    dnl = list(devices.keys())
    dipl = list(devices.values())
    ipdc = ipdc(dnl, dipl)
    base_local_dir = ipdc.connect_to_SGPhone()
    print("base_local_dir from main.py:", base_local_dir)
    db_connector = dbc(base_local_dir)
    db_connector.load_databases()  # fills df and writes data.csv
    # db_connector.save_csv('data.csv')  # saves data.csv
    # db_connector.save_excel('data.xlsx')  # saves data.xlsx