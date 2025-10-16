#!/usr/bin/env python3
import subprocess
from pathlib import Path
import re
import gspread
from google.oauth2.service_account import Credentials
from lib.parse_helper import status_parser, parse_crab_task
import sys
from typing import Optional
import logging

logger = logging.getLogger(__name__)
def setup_google_sheet(sheet_id:str, credentials_file:str)->gspread.worksheet:
    # Your service account needs to have this api enabled. If you reference the
    # sheet by ID, you don't need any other apis enabled
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    CREDENTIALS_PATH = Path(credentials_file)
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id)

def find_worksheet(sheet, era, version)->Optional[int]:
    """
    Find worksheet that matches the given era and version
    """
    worksheets = [sheet.title for sheet in sheet.worksheets()]

    # Look for a worksheet that contains both year_part and version_part
    index = next(
        (i for i, title in enumerate(worksheets)
         if era in title and version in title),
        None
    )
    return index

def edit_cell(worksheet, row:int, column:int, value:str, force:bool = False)->None:
    """
    Edit google sheet cell. By default this will not edit the cell if there
    is already a value inside. This allows for users to manually edit the google sheet in
    case of the need for manual intervention. This option can be overriden with the force
    flag

    Note: The format of the google sheet for data processing is
    selection, dataset0, dataset1, nlayers, merged
    """
    if force:
        worksheet.update_cell(row, column, value)
    else:
        if worksheet.cell(row, column).value:
            logger.warning(f"Cell {row}, {column} already has a value inside. If you would like to override pass force=True to edit_cell()")
        else:
            worksheet.update_cell(row, column, value)




def find_cell(worksheet, task_name:str)->Optional[tuple[int, ...]]:
    """
    Find cell that contains task_name.

    Note: Currently, task_name must match exactly to the cell
    """

    cell = worksheet.find(task_name)
    if cell:
        return cell.row, cell.col
    else:
        return None, None


def update_task_status(worksheet_ID, credentials_file, task_name, status, force)->None:
    """
    Update the status of a selection in a worksheet.

    Arguments:
    worksheet_ID: Google sheet ID that can be obtained from URL
    credentials_file: Credentials file used to validate service account needed to edit google sheet
    task_name: The name of the task as listed in the crab directory
    status: The status of the current selection
    """
    sheet = setup_google_sheet(worksheet_ID, credentials_file)

    selection, era, version, dataset_version = parse_crab_task(task_name)
    if not all([selection,era,version,dataset_version]):
        logger.error(f"Unable to parse all information from task name: {task_name}")
        return

    worksheet_index = find_worksheet(sheet, era, version)
    worksheet = sheet.get_worksheet(worksheet_index)

    if worksheet_index is None:
        logger.error(f"Not able to find worksheet that matches given era and version: {era}, {version}")
        return

    row, column = find_cell(worksheet, selection)
    if not all([row, column]):
        logger.error(f"Not able to find selection inside of sheet: {selection}")
        return

    # Determine whether you are processing NLayers, EGamma/Muon0 or EGamma/Muon1
    if str(dataset_version) == "0":
        col_offset = 1
    elif str(dataset_version) == "1":
        col_offset = 2
    elif "NLayers" in selection:
        col_offset = 3
    else:
        logger.error(f"Unable to verify what dataset version was processed ((Muon|EGamma)0 or NLayers): {task_name}")

    edit_cell(worksheet, row, column+col_offset, status, force=force)
