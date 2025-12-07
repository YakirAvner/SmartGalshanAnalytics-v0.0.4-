import os
import paramiko as pmk
import posixpath
import socket
import stat
from threading import Thread


class IP_DB_Copier:
    def __init__(self, device_name_list, device_ip_list):
        self.device_name_list = device_name_list
        self.device_ip_list = device_ip_list

    def connect_to_SGPhone(self):
        base_local_dir = r"C:\Users\Yakir\SG_Devices" 
        os.makedirs(base_local_dir, exist_ok=True)
        for phone_name, ip in zip(self.device_name_list, self.device_ip_list):
            # Connecting to each DB in the list.
            # Define the database connector from the given IP
            try:
                hostname, port = ip.split(":")
                port = int(port)
            except ValueError:
                print(f"Invalid IP format: {ip}")
                continue
            print(f"Connecting to device {phone_name} at IP {ip}")
            username = "g188"
            password = "1470"
            phone_source_folder = r"/Documents"
            client = pmk.SSHClient()
            client.set_missing_host_key_policy(pmk.AutoAddPolicy())
            local_dir = os.path.join(base_local_dir, phone_name)
            os.makedirs(local_dir, exist_ok=True)

            try:
                client.connect(hostname=hostname, port=port,
                               username=username, password=password)
                sftp = client.open_sftp()
                self.go_through_folders(sftp, local_dir, phone_source_folder)

            except (pmk.SSHException, socket.timeout, TimeoutError, OSError) as e:
                print(f"Failed to connect to device at IP: {hostname} with an {e} error")

    def go_through_folders(self, sftp, local_dir, phone_source_folder):
        # Looping inside the dates of the file.  
        for date_folder in sftp.listdir_attr(phone_source_folder):
            # Checks if the remote item (date_file) is a DIRECTORY!!!
            if stat.S_ISDIR(date_folder.st_mode):
                db_folder = f"{phone_source_folder}/{date_folder.filename}"
                # Loops the date_folders
                for item in sftp.listdir_attr(db_folder):
                    # Checks if the remote item (db_file) is a DIRECTORY!!! & and named "SQLite".
                    if item.filename == "SQLite" and stat.S_ISDIR(item.st_mode):
                        SQLite_file = f"{db_folder}/{item.filename}"
                        # Loops the SQLite folder.
                        for Galshan_db in sftp.listdir_attr(SQLite_file):
                            # Checks if the files name is "Galshan.db".
                            if Galshan_db.filename == "Galshan.db":
                                remote_db = f"{SQLite_file}/{Galshan_db.filename}"
                                local_db = os.path.join(local_dir, f"{date_folder.filename}_{Galshan_db.filename}")

                                #sftp.get(remote_db, local_db)
                                self.copy_and_check_db(sftp, local_db, remote_db)
    
    def copy_and_check_db(self, sftp, local_db, remote_db):
        if os.path.exists(local_db):
            print(f"The {local_db} is already copied in the {os.path.dirname(local_db)} from the {remote_db} db.")
        else:
            print(f"The {local_db} isn't copied in the {os.path.dirname(local_db)} from the {remote_db} db. \nCopying {remote_db} to {local_db}... ")
            sftp.get(remote_db, local_db)
            
