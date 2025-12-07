import sqlite3
import pandas as pd
import csv
import os
import glob
import openpyxl
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class DBConnector:
    def __init__(self, df):
        self.df = df

    def load_databases(self):
        # Connecting to each DB in the list.
        # Define the database connector pattern with wildcards
        db_connector_pattern = r"C:\Users\user\Desktop\Yakir Avner\DBTraining\Galshan*\Galshan*DB"
        print(f"db_connector_pattern: {db_connector_pattern}")
        db_files = glob.glob(os.path.join(
            db_connector_pattern, '**', 'Galshan*.db'), recursive=True)
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
                    MT = max_temperature.execute(
                        "SELECT MAX(Device_Temperature) from Snapshots;").fetchone()[0]

                    # TMT abbreviation: Time of Max Temperature.
                    TMT = time_max_temperature.execute("""
                                                        SELECT time
                                                        FROM Snapshots
                                                        WHERE device_temperature = (SELECT MAX(device_temperature) FROM Snapshots)
                                                                LIMIT 1;
                                                        """).fetchone()[0]
                    # Counting the number of detections.
                    num_of_detections = num_of_detections.execute(
                        "SELECT COUNT(*) from Detections").fetchone()[0]

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

    def save_excel(self, this_filename):
        # this_filename = to the current directory + filename
        this_filename = BASE_DIR / this_filename
        exists = this_filename.exists()
        if not exists:
            # Create a new Excel file
            with pd.ExcelWriter(this_filename, engine='openpyxl') as writer:
                self.df.to_excel(writer, index=False)
        else:
            # Append data to existing Excel file
            with pd.ExcelWriter(this_filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                self.df.to_excel(writer, index=False, header=False,
                                 startrow=writer.sheets['Sheet1'].max_row)
