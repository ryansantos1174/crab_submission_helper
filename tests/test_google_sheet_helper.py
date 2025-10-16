#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from lib.google_sheet_helper import (
    setup_google_sheet,
    find_worksheet,
    edit_cell,
    find_cell,
    update_task_status,
)
from pathlib import Path

class TestGoogleSheetHelpers(unittest.TestCase):

    @patch("lib.google_sheet_helper.Credentials")
    @patch("lib.google_sheet_helper.gspread")
    def test_setup_google_sheet(self, mock_gspread, mock_creds):
        mock_gc = MagicMock()
        mock_gspread.authorize.return_value = mock_gc
        mock_gc.open_by_key.return_value = "mock_sheet"

        result = setup_google_sheet("abc123", "fake_credentials.json")

        mock_creds.from_service_account_file.assert_called_once_with(
            Path("fake_credentials.json"), scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        mock_gspread.authorize.assert_called_once()
        mock_gc.open_by_key.assert_called_once_with("abc123")
        self.assertEqual(result, "mock_sheet")

    def test_find_worksheet_found(self):
        mock_sheet = MagicMock()
        mock_sheet.worksheets.return_value = [
            MagicMock(title="Background Estimate 2023C v1"),
            MagicMock(title="Background Estimate 2023D v3"),
        ]
        result = find_worksheet(mock_sheet, "2023C", "v1")
        self.assertEqual(result, 0)

    def test_find_worksheet_not_found(self):
        mock_sheet = MagicMock()
        mock_sheet.worksheets.return_value = [
            MagicMock(title="Background Estimate 2023C v1"),
            MagicMock(title="Background Estimate 2023D v3"),
        ]
        result = find_worksheet(mock_sheet, "2023C", "v3")
        self.assertIsNone(result)

    # Not really testing much
    def test_edit_cell_force(self):
        mock_ws = MagicMock()
        edit_cell(mock_ws, 1, 2, "DONE", force=True)
        mock_ws.update_cell.assert_called_once_with(1, 2, "DONE")

    @patch("lib.google_sheet_helper.logger")
    def test_edit_cell_skip_existing(self, mock_logging):
        mock_ws = MagicMock()
        mock_ws.cell.return_value.value = "existing"
        edit_cell(mock_ws, 1, 2, "NEW", force=False)
        mock_logging.warning.assert_called_once()

    def test_find_cell_found(self):
        mock_ws = MagicMock()
        mock_ws.find.return_value = MagicMock(row=5, col=2)
        self.assertEqual(find_cell(mock_ws, "taskX"), (5, 2))

    def test_find_cell_not_found(self):
        mock_ws = MagicMock()
        mock_ws.find.return_value = None
        self.assertEqual(find_cell(mock_ws, "taskX"), (None, None))

    @patch("lib.google_sheet_helper.parse_crab_task")
    @patch("lib.google_sheet_helper.setup_google_sheet")
    @patch("lib.google_sheet_helper.find_worksheet")
    @patch("lib.google_sheet_helper.find_cell")
    @patch("lib.google_sheet_helper.edit_cell")
    def test_update_task_status(
        self, mock_edit, mock_find_cell, mock_find_ws, mock_setup, mock_parse
    ):
        mock_sheet = MagicMock()
        mock_ws = MagicMock()
        mock_setup.return_value = mock_sheet
        mock_sheet.get_worksheet.return_value = mock_ws
        mock_parse.return_value = ("sel", "2023A", "v1", "0")
        mock_find_ws.return_value = 0
        mock_find_cell.return_value = (5, 1)

        update_task_status("sheet_id", "creds.json", "crab_task", "DONE")

        mock_edit.assert_called_once_with(mock_ws, 5, 2, "DONE", force=False)
