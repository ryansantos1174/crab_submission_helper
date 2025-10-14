#!/usr/bin/env python3
"""
Notes:
The selection name is on column D, the fist selection starts at row 8.
The All column for the selections is on column E

"""
import subprocess
from pathlib import Path
import re
import gspread
from google.oauth2.service_account import Credentials
from parser import status_parser
import sys
# === CONFIGURATION ===
GLOB_PATTERN = "crab_*2023*"
BASE_DIR = Path("../DisappTrks/BackgroundEstimation/test/crab")
SHEET_ID = "1YeKU_0nEG56fJtiPiHs54O1dULYMrmO23WKt5-06ENs"  # Change to your sheet name
CREDENTIALS_PATH = Path("credentials.json")

# Authenticate with Google
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
]
creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

for crab_dir in BASE_DIR.glob(GLOB_PATTERN):
    # Get rid of "crab_" at the beginning of file path
    task = "_".join(crab_dir.name.split("_")[1:])
# Look for pattern: underscore + year+letter + underscore + version
    match = re.search(r'_(\d{4}[A-Z])_(v\d+)_(?:Muon|EGamma)(v\d)', task)
    if match:
        year_part = match.group(1)  # '2023C'
        version_part = match.group(2)  # 'v1'
        dataset_version = match.group(3)
        print(year_part, version_part, dataset_version)
    print(f"Checking {task}...")

    # Get all worksheet titles
    worksheet_titles = [sheet.title for sheet in sh.worksheets()]

    # Look for a worksheet that contains both year_part and version_part
    index = next(
        (i for i, title in enumerate(worksheet_titles)
         if year_part in title and version_part in title),
        None
    )

    if index is not None:
        sheet = sh.get_worksheet(index)
        print(f"Found worksheet: {sheet.title}")
    else:
        print("No matching worksheet found")

    # Read current sheet contents into a dict for fast lookup
    # existing contains the selection and the index at which they start
    existing = {row[3]: i+8 for i, row in enumerate(sheet.get_all_values()[7:]) if row}
    existing.pop("", None)  # removes key "" if it exists, does nothing otherwise

    result = subprocess.run(
        ["crab", "status", "-d", str(crab_dir)],
        capture_output=True, text=True
    )

    # Determine status
    status_dict = status_parser(result.stdout)

    status = if status_dict["Finished"] and not status_dict["Failed"]
    value = "finished" if status else "processing"

    for selection in existing.keys():
        if selection.lower() in task.lower():
            if "nlayers" in task.lower():
                range_name = f"G{row_index}"
            else:
                if dataset_version == "v0":
                    range_name=f"E{row_index}"
                if dataset_version == "v1":
                    range_name=f"E{row_index}"

            # Update existing row
            row_index = existing[selection]  # +1 because of header
            sheet.update(range_name=range_name, values=[[status]])
            print(f"Updated google sheet row {row_index}")
