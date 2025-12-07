import os
import glob
import pandas as pd
import csv

class MonthDaySeparation:
    # Splitting Months & Days Function.
    def __init__(self, df):
        self.df = df
    def month_day_attraction(date_folder):
        date_list = os.listdir(date_folder)
        split_date_list = []
        for folder in date_list:
            date_index = os.path.basename(folder)
            new_folder_name = f"{"-".join(date_index.split('-')[::-1])}"
            split_date_list.append(new_folder_name.split('-'))
        return split_date_list

    # 🔹 NEW: Define the database path pattern with wildcards
    db_date_pattern = r"C:\Users\user\Desktop\Yakir Avner\DBTraining\Galshan*\DocumentsGalshan*"
    print(f"db_pattern: {db_date_pattern}")
    # 🔹 NEW: expand the wildcard into real folders
    folders = [p for p in glob.glob(db_date_pattern) if os.path.isdir(p)]
    print("Matched folders:", folders)
    if not folders:
        print("No folders matched the pattern.")
    else:
        for folder in folders:
            print(f"\nProcessing folder: {folder}")
            month_day_list = month_day_attraction(folder)
            print("month_day_list:", month_day_list)
    
    # for SDL in month_day_attraction:
    #     for x in SDL:
    #         # Add the months and day seperately in the excel spread sheet.
    #         print("Waiting for me")
