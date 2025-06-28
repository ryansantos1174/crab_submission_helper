import unittest
import os
import crab_manager
import pandas as pd

class TestCrabHelper(unittest.TestCase):
    handler = crab_manager.CrabHandler()

    data_file = os.path.join(os.path.dirname(__file__), "stat.json")

    def test_get_failed_job_ids(self):
        df = pd.read_json(self.data_file).transpose()
        failed_jobs_indices = self.handler.get_failed_job_ids(df)
        self.assertEqual(list(failed_jobs_indices["JobIds"]), ['127769374.0', '127769376.0', '127769377.0'])

    def test_check_location(self):
        df = pd.read_json(self.data_file).transpose()
        failed_jobs = self.handler.get_failed_job_ids(df)
        print(self.handler.check_location(failed_jobs))
        

        
if __name__ == "__main__":
    unittest.main()
