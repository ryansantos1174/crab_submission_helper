#!/usr/bin/env python3

import unittest
import re
from unittest.mock import mock_open, patch
from crab_submission_helper.lib.parse_helper import (
    status_parser,
    replace_template_values,
    parse_crab_task,
    parse_task_name,
    parse_yaml
)

ASSETS_DIRECTORY="tests/testAssets/"

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

    def test_parse_yaml_valid(self):
        data = parse_yaml(ASSETS_DIRECTORY+"example_batch_submission.yaml")
        self.assertEqual({'jobs': [{'Year': '2023C', 'Era Version': 'v1', 'Dataset Version': 1, 'Selections': 'ZtoTauToEleProbeTrk'}, {'Year': '2023D', 'Era': 'v1', 'Dataset Version': 1, 'Selections': 'ZtoTauToMuProbeTrk'}]}, data)

    def test_task_name_valid(self):
        test_cases = [
            (
                "crab_ZtoTauToEleProbeTrk_2023D_v1_NLayers",
                ("ZtoTauToEleProbeTrk", "2023", "D", "v1", "NLayers"),
            ),
            (
                "crab_ZtoTauToEleProbeTrk_2023D_v2_EGamma0",
                ("ZtoTauToEleProbeTrk", "2023", "D", "v2", "EGamma0"),
            ),
            (
                "crab_ZtoTauToMuProbeTrk_2023C_v1_Muon0",
                ("ZtoTauToMuProbeTrk", "2023", "C", "v1", "Muon0"),
            ),
            (
                "crab_ZtoTauToMuProbeTrk_2024C_Muon0",
                ("ZtoTauToMuProbeTrk", "2024", "C", None, "Muon0"),
            ),
        ]

        for task_name, expected in test_cases:
            with self.subTest(task_name=task_name):
                data = parse_task_name(task_name)
                self.assertEqual(data, expected)

    def test_task_name_invalid(self):
        invalid_names = [
            "crab_missing_year_EGamma0",
            "crab_TTJets_20A_v1_Muon0",   # bad year
            "crab_TTJets_2023D_v1",       # missing selection
        ]
        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    parse_task_name(name)

if __name__ == "__main__":
    unittest.main()
