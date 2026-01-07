import paramiko as pmk
from threading import Thread
import os       
import socket
import stat
import hashlib
from datetime import date, timedelta 

class Daily_IP_DB_Copier:
    def __init__(self, device_name_list, device_ip_list, base_local_dir):
        self.device_name_list = device_name_list
        self.device_ip_list = device_ip_list
        self.base_local_dir = base_local_dir
    
    def connect_to_SGPhone(self):
        os.makedirs(self.base_local_dir, exist_ok=True)
        # Creating threads for each device connection
        threads = []
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
            local_dir = os.path.join(self.base_local_dir, phone_name)
            os.makedirs(local_dir, exist_ok=True)

            try:
                client.connect(hostname=hostname, port=port,
                               username=username, password=password)
                sftp = client.open_sftp()
                print(f"--Connected to device {phone_name} at IP {ip}--")
                t = Thread(target=self.go_through_folders, args=(sftp, local_dir, phone_source_folder))
                threads.append(t)

            except (pmk.SSHException, socket.timeout, TimeoutError, OSError) as e:
                print(f"Failed to connect to device at IP: {hostname} with an {e} error")
        
        # Starting all threads
        for t in threads:
            print("Starting a new thread for device connection and DB copy...")
            t.start()
        
        # Joining all threads
        for t in threads:
            t.join()
            print("All device connections and DB copies are complete.")

    def go_through_folders(self, sftp, local_dir, phone_source_folder):
        # Looping inside the dates of the file.  
        for date_folder in sftp.listdir_attr(phone_source_folder):
            if stat.S_ISDIR(date_folder.st_mode):
                date_folder_name = date_folder.filename
                remote_date_folder_path = f"{phone_source_folder}/{date_folder_name}"
                local_date_folder_path = os.path.join(local_dir, date_folder_name)
                os.makedirs(local_date_folder_path, exist_ok=True)
                today_str = str(date.today())
                yesterday = str(date.today() - timedelta(days=1))
                two_days_ago = str(date.today() - timedelta(days=2))
                if date_folder_name == today_str or date_folder_name == yesterday or date_folder_name == two_days_ago:
                    # Looping inside the files of the date folder.
                    for file_attr in sftp.listdir_attr(remote_date_folder_path):
                        file_name = file_attr.filename
                        if file_name.endswith("Galshan.db"):
                            remote_file_path = f"{remote_date_folder_path}/{file_name}"
                            local_file_path = os.path.join(local_date_folder_path, file_name)

                            try:
                                sftp.get(remote_file_path, local_file_path)
                                print(f"Copied {remote_file_path} to {local_file_path}")
                            except Exception as e:
                                print(f"Failed to copy {remote_file_path} to {local_file_path}: {e}")
                else: 
                    print(f"Skipping folder: {date_folder_name}; not in the last 3 days.")
    
    def copy_and_check_db(self, sftp, local_db, remote_db):
        print(f"Checking if {local_db} is already copied or not...")
        
        if os.path.exists(local_db):
            # Database exists locally - check if it has changed remotely
            remote_checksum = self.get_remote_file_checksum(sftp, remote_db)
            local_checksum = self.get_local_file_checksum(local_db)
            
            if remote_checksum == local_checksum:
                print(f"✓ The {local_db} is already copied and matches remote {remote_db} (No changes detected)")
            else:
                print(f"⚠ The {local_db} exists but DIFFERS from remote {remote_db} (Changes detected!)\nUpdating {local_db} from {remote_db}... ")
                sftp.get(remote_db, local_db)
                print(f"✓ Successfully updated {local_db}")
        else:
            print(f"The {local_db} isn't copied in the {os.path.dirname(local_db)} from the {remote_db} db. \nCopying {remote_db} to {os.path.dirname(local_db)}... ")
            sftp.get(remote_db, local_db)
            print(f"✓ Successfully copied {remote_db} to {local_db}")

    def get_remote_file_checksum(self, sftp, remote_file):
        try:
            md5 = hashlib.md5()
            with sftp.file(remote_file, "rb") as f:
                try:
                    f.prefetch()
                except Exception:
                    pass

                for chunk in iter(lambda: f.read(65536), b""):
                    md5.update(chunk)

            return md5.hexdigest()

        except Exception as e:
            print(f"Error calculating remote checksum for {remote_file}: {e}")
            return None

    def get_local_file_checksum(self, local_file):
        try:
            with open(local_file, "rb") as f:
                return hashlib.file_digest(f, "md5").hexdigest()
        except Exception as e:
            print(f"Error calculating local checksum for {local_file}: {e}")
            return None