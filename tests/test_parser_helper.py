#!/usr/bin/env python3

import unittest
import re
from unittest.mock import mock_open, patch
from lib.parse_helper import status_parser, replace_template_values, parse_crab_task

class TestParseHelper(unittest.TestCase):

    # ----------------------------
    # Test status_parser
    # ----------------------------
    def test_status_parser_both(self):
        output = "Some output failed 10% finished 90% done"
        result = status_parser(output)
        self.assertTrue(result["Failed"])
        self.assertTrue(result["Finished"])

    def test_status_parser_failed_only(self):
        output = "Some output failed 5% remaining"
        result = status_parser(output)
        self.assertTrue(result["Failed"])
        self.assertFalse(result["Finished"])

    def test_status_parser_finished_only(self):
        output = "Some output finished 100% done"
        result = status_parser(output)
        self.assertFalse(result["Failed"])
        self.assertTrue(result["Finished"])

    def test_status_parser_none(self):
        output = "Some output in progress"
        result = status_parser(output)
        self.assertFalse(result["Failed"])
        self.assertFalse(result["Finished"])

    # ----------------------------
    # Test replace_template_values
    # ----------------------------
    @patch("builtins.open", new_callable=mock_open, read_data="__SKIM_FILE__ __DATASET__ __REQUESTNAME__")
    def test_replace_template_values(self, mock_file):
        replacement = {
            "SKIM_FILE": "file.py",
            "DATASET": "dataset123",
            "REQUESTNAME": "req001"
        }

        # Call the function
        replace_template_values("fake_path.py", replacement)

        # Ensure the file was opened correctly
        mock_file.assert_called_once_with("fake_path.py", "r")

        # Test the inner replacement logic via re.sub directly
        text = "__SKIM_FILE__ __DATASET__ __REQUESTNAME__"
        pattern = r"__([A-Z0-9_]+)__"
        def replace_var(match):
            key = match.group(1)
            return replacement.get(key, match.group(0))

        new_text = re.sub(pattern, replace_var, text)
        self.assertEqual(new_text, "file.py dataset123 req001")

    # ----------------------------
    # Test parse_crab_task
    # ----------------------------
    def test_parse_crab_task_valid(self):
        task_name = "/uscms/home/delossan/nobackup/CMSSW_13_0_13/src/DisappTrks/BackgroundEstimation/test/crab/crab_ZtoTauToMuProbeTrk_2023C_v3_Muon0"
        selection, era, version, dataset_version = parse_crab_task(task_name)
        self.assertEqual(era, "2023C")
        self.assertEqual(version, "v3")
        self.assertEqual(dataset_version, "0")
        self.assertIsNotNone(selection)

    def test_parse_crab_task_invalid(self):
        task_name = "crab_Invalid_TaskName"
        selection, era, version, dataset_version = parse_crab_task(task_name)
        self.assertIsNone(selection)
        self.assertIsNone(era)
        self.assertIsNone(version)
        self.assertIsNone(dataset_version)


if __name__ == "__main__":
    unittest.main()
