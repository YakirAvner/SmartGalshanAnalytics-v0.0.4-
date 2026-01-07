import csv
import glob
import openpyxl
import os
import pandas as pd
from pathlib import Path
import sqlite3



BASE_DIR = Path(__file__).resolve().parent


class DBConnector:
    
    def __init__(self, base_local_dir):
        self.base_local_dir = base_local_dir
        self.df = pd.DataFrame(
            columns=['Database_Name', 'Max_Temperature', 'Time_of_Max_Temperature', 'Number_of_Detections'])

    def load_databases(self):
        # Connecting to each DB in the list.
        # Define the database connector pattern with wildcards
        print(f"db_connector_pattern: {self.base_local_dir}")
        db_files = glob.glob(os.path.join(
            self.base_local_dir, '**', '**Galshan.db'), recursive=True)
        print(f"db_files found: {db_files}")
        for dbName in db_files:
            try:
                conn = sqlite3.connect(dbName)
                conn.row_factory = sqlite3.Row  # 👈 THIS makes rows behave like dictionaries
                if conn:
                    print("Connected to SQLite")
                    max_temperature = conn.cursor()
                    time_max_temperature = conn.cursor()
                    num_of_detections = conn.cursor()

                    # MT abbreviation: Max Temperature.
                    mt_result = max_temperature.execute(
                        "SELECT MAX(Device_Temperature) from Snapshots;").fetchone()
                    MT = mt_result[0] if mt_result and mt_result[0] is not None else "N/A"

                    # TMT abbreviation: Time of Max Temperature.
                    tmt_result = time_max_temperature.execute("""
                                                        SELECT time
                                                        FROM Snapshots
                                                        WHERE device_temperature = (SELECT MAX(device_temperature) FROM Snapshots)
                                                                LIMIT 1;
                                                        """).fetchone()
                    TMT = tmt_result[0] if tmt_result else "N/A"
                    
                    # Counting the number of detections.
                    det_result = num_of_detections.execute(
                        "SELECT COUNT(*) from Detections").fetchone()
                    num_of_detections = det_result[0] if det_result else 0

                    self.df.loc[len(self.df)] = [dbName, MT,
                                                  TMT, num_of_detections]
            except sqlite3.Error as e:
                print(f"Failed to connect to SQLite db: {dbName}")
            finally:
                if conn:
                    conn.close()

    def save_csv(self, csv_filename):
        # this_filename = to the current directory + filename
        this_filename = BASE_DIR / csv_filename
        exists = this_filename.exists()
        self.df.to_csv(this_filename, index=False,
                       mode='a' if exists else 'w', header=not exists)

    def save_excel(self, excel_filename):
        # this_filename = to the current directory + filename
        this_filename = BASE_DIR / excel_filename
        exists = this_filename.exists()
        if not exists:
            # Create a new Excel file
            with pd.ExcelWriter(this_filename, engine='openpyxl') as writer:
                self.df.to_excel(writer, index=False)
        else:
            # Append data to existing Excel file
            with pd.ExcelWriter(this_filename, engine='openpyxl', if_sheet_exists='overlay') as writer:
                for row in self.df.iterrows():
                    if row not in this_filename:
                        self.df.append(row)
                    else:
                        print(f"Row {row} already exists in the Excel file. Skipping append.") 
            # with pd.ExcelWriter(this_filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            #     self.df.to_excel(writer, index=False, header=False,
            #                      startrow=writer.sheets['Sheet1'].max_row)
