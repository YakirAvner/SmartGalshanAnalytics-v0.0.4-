import argparse
from daily_ip_db_copier import Daily_IP_DB_Copier as dipdc
from DB_Connector import DBConnector as dbc
from ip_db_copier import IP_DB_Copier as ipdc
import openpyxl
import os
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
print("Running SG-Analytics main.py...")
devices = parse_device()
dnl = list(devices.keys())
dipl = list(devices.values())
base_local_dir = r"C:\SG_Devices_DBs"
if not os.path.exists(base_local_dir):
    print(f"{base_local_dir} does not exist. Creating it...")
    ipdc_connector = ipdc(dnl, dipl, base_local_dir)
    ipdc_connector.connect_to_SGPhone()
else:
    print(f"{base_local_dir} exists. Proceeding to daily DB copy...")
    dipdc_connector = dipdc(dnl, dipl, base_local_dir)
    dipdc_connector.connect_to_SGPhone()
db_connector = dbc(base_local_dir)
db_connector.load_databases()  # fills df and writes data.csv
db_connector.save_csv('data_csv.csv')  # saves data.csv
db_connector.save_excel('data_excel.xlsx')  # saves data.xlsx