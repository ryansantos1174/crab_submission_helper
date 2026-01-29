#!/usr/bin/env python3
from pathlib import Path
from typing import Optional
import logging

import gspread
from google.oauth2.service_account import Credentials

from .parse_helper import parse_crab_task
from .config import JobStatus


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

    Note: The google sheet should have column headers like "Dataset 0", "Dataset 1",
    "NLayers Dataset 0", etc. to indicate where data should be written.
    """
    if force:
        worksheet.update_cell(row, column, value)
    else:
        if worksheet.cell(row, column).value:
            logger.warning("Cell %s, %s already has a value inside. If you would like to override pass force=True to edit_cell()", row, column)
        else:
            worksheet.update_cell(row, column, value)

def format_cell(worksheet, row:int, column:int, attribute_dict:dict):
    a1_notation:str = gspread.utils.rowcol_to_a1(row, column)
    worksheet.format(a1_notation, attribute_dict)

def find_cell(worksheet, task_name:str)->Optional[tuple[int, ...]]:
    """
    Find cell that contains task_name.

    Note: Currently, task_name must match exactly to the cell
    """

    cell = worksheet.find(task_name)

    if cell:
        return cell.row, cell.col

    return None, None

def find_column_by_header(worksheet, header_name: str) -> Optional[int]:
    """
    Find column index by searching the worksheet for a matching header.
    Returns 1-indexed column number or None if not found.
    """
    cell = worksheet.find(header_name)
    if cell:
        return cell.col
    return None

def get_column_header(task_name: str, dataset_version: str) -> str:
    """
    Build the expected column header based on task type and dataset version.
    E.g., "Dataset 0", "Dataset 1", "NLayers Dataset 0", etc.
    """
    if "NLayers" in task_name:
        return f"NLayers Dataset {dataset_version}"
    else:
        return f"Dataset {dataset_version}"

def update_task_status(worksheet_ID, credentials_file, task_name, status, entry, force=False)->None:
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
        logger.error("Unable to parse all information from task name: %s", task_name)
        return

    worksheet_index = find_worksheet(sheet, era, version)
    worksheet = sheet.get_worksheet(worksheet_index)

    if worksheet_index is None:
        logger.error("Not able to find worksheet that matches given era and version: %s, %s", era, version)
        return

    row, column = find_cell(worksheet, selection)
    if not all([row, column]):
        logger.error("Not able to find selection inside of sheet: %s", selection)
        return

    # Find the target column by looking up the header name
    column_header = get_column_header(task_name, dataset_version)
    target_column = find_column_by_header(worksheet, column_header)

    if target_column is None:
        logger.error("Unable to find column with header '%s' in worksheet", column_header)
        return

    edit_cell(worksheet, row, target_column, entry, force=force)

    # Format cell based off of status
    if status == JobStatus.Finished:
        format_dict = {"backgroundColor": {
            "red": 0.0,
            "green": 1.0,
            "blue":0.0
        }
                       }
    elif status == JobStatus.Processing:
        format_dict = {
            "backgroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 0.0
            }
        }
    elif status == JobStatus.Failed:
        format_dict = {
            "backgroundColor": {
                "red": 1.0,
                "green": 0.0,
                "blue": 0.0
            }
        }
    else:
        logger.error("Unable to determine status, not formatting cell.")
        return

    format_cell(worksheet, row, target_column, format_dict)
