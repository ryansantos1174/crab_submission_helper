import unittest
import json
import os
import crab_manager
import pandas as pd
import tempfile

class TestCrabHelper(unittest.TestCase):
    handler = crab_manager.CrabHandler()

    data_file = os.path.join(os.path.dirname(__file__), "stat.json")

    def test_get_failed_job_ids(self):
        df = pd.read_json(self.data_file).transpose()
        failed_jobs_indices = self.handler.get_failed_job_ids(df)
        self.assertEqual(list(failed_jobs_indices["LatestJobId"]), ['127769374.0', '127769376.0', '127769377.0'])

    def test_config_generator(self):
        # Create an instance if config_generator is a method
        # If your method is in a class, say ConfigWriter, then:

        parameters = {
            "year": "2022",
            "era": "A",
            "isRealData": True,
            "filenames": '"file1.root", "file2.root"',
            "lumiBlocks": '"123:1-123:100"',
        }

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_name = tmp.name

        try:
            self.handler.config_generator(temp_name, parameters)

            # Read the output file
            with open(temp_name, "r") as f:
                content = f.read()

            assert '"2022"' in content
            assert '"A"' in content
            assert "realData=True" in content
            assert "file1.root" in content
            assert "123:1-123:100" in content

        finally:
            os.remove(temp_name)

    def test_grab_failed_lumis_and_files(self):
        """
        The function inside crab_manager runs crab report which I don't need
        to do for the test. The test here is copy and pasted from that function
        skipping the crab report command 
        """

        failed_lumis = self.handler.process_failed_lumis_file(os.path.join(os.path.dirname(__file__), "notFinishedLumis.json"))
        with open(os.path.join(os.path.dirname(__file__), "failedFiles.json")) as file:
            failed_files_json = json.load(file)
            failed_files = [path for paths in failed_files_json.values() for path in paths]

        return_dict = dict(lumiBlocks=failed_lumis, filenames=failed_files)
        self.assertEqual(return_dict, {"lumiBlocks" : ['367475:361',
                                                       '367515:233-367515:237',
                                                       '367515:320',
                                                       '367515:322-367515:323',
                                                       '367515:326-367515:328',
                                                       '367515:330-367515:331',
                                                       '367515:333-367515:337',
                                                       '367515:344-367515:345',
                                                       '367515:347-367515:349',
                                                       '367515:421',
                                                       '367515:426',
                                                       '367515:428-367515:434',
                                                       '367515:437',
                                                       '367515:439',
                                                       '367515:453-367515:454',
                                                       '367515:464',
                                                       '367515:476',
                                                       '367515:478',
                                                       '367515:480-367515:482',
                                                       '367515:486',
                                                       '367515:489-367515:490',
                                                       '367515:493',
                                                       '367515:496-367515:497',
                                                       '367515:499',
                                                       '367515:504',
                                                       '367515:522-367515:523',
                                                       '367515:525-367515:526',
                                                       '367515:531',
                                                       '367515:533',
                                                       '367515:561',
                                                       '367515:565',
                                                       '367515:570'],
                                       "filenames": ["/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/2530000/ab597954-8362-471a-af29-20b75b3ba722.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/29ee99bf-ff2c-4762-aec8-72a03ae474cd.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/fd5fb838-2406-4cf7-9a3f-9cc8c0f20221.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/fd5fb838-2406-4cf7-9a3f-9cc8c0f20221.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/c164a8b0-fbd9-4029-aca2-793cead75b56.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/f168edfa-fa8b-4fb5-9ad8-d3b4439c1e0b.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/f168edfa-fa8b-4fb5-9ad8-d3b4439c1e0b.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/7f02cd8e-bb0b-4b40-8b64-b403014c2ec1.root",
                                                     "/store/data/Run2023C/Muon0/MINIAOD/22Sep2023_v1-v1/30000/9592d62a-5e3e-4872-a8fa-a4845ed5e20f.root"]})
                             

        
if __name__ == "__main__":
    unittest.main()
