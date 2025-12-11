import argparse
from DB_Connector import DBConnector as dbc
from ip_db_copier import IP_DB_Copier as ipdc
from daily_ip_db_copier import Daily_IP_DB_Copier as dipdc
import openpyxl
import os
import pandas as pd
import paramiko as pmk
from datetime import datetime


def parse_device():
    device_IPs = [ 
        # "SG9=2.54.238.146:51807",
        # "SG20=109.253.65.75:51807",
        # "SG21=2.54.89.11:51807",
        "SG23=2.54.238.136:51807",
        # "SG24=2.55.117.174:51807",
        "SG25=2.54.88.254:51807",
        "SG26=2.54.89.1:51807",
        # "SG28=2.54.89.8:51807",
        # "SG29=2.54.89.3:51807",
        # "SG44=2.54.89.4:51807"
        ]
    devices = {}
    for item in device_IPs:
        name, ip = item.split('=', 1)
        devices[name] = ip
    return devices

# If the program is running in the main file, then:
if __name__ == "__main__":
    devices = parse_device()
    dnl = list(devices.keys())
    dipl = list(devices.values())
    base_local_dir = r"C:\SG_Devices_DBs"
    if not os.path.exists(base_local_dir):
        ipdc = ipdc(dnl, dipl, base_local_dir)
        ipdc.connect_to_SGPhone()
    else:
        dipdc = dipdc(dnl, dipl, base_local_dir)
        dipdc.connect_to_SGPhone()
    db_connector = dbc(base_local_dir)
    db_connector.load_databases()  # fills df and writes data.csv
    db_connector.save_csv('data_csv.csv')  # saves data.csv
    db_connector.save_excel('data_excel.xlsx')  # saves data.xlsx