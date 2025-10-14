#!/usr/bin/env python3
import re

def status_parser(crab_status_output:str)->dict:
    # Search for failed and finished optionally so that if either are not there the
    # search doesn't fail
    failed_pattern_search = r".*failed\s+\d.*%.*"
    finished_pattern_search = r".*finished\s+\d.*%.*"

    failed_match = re.search(failed_pattern_search, crab_status_output)
    finished_match = re.search(finished_pattern_search, crab_status_output)

    return {"Failed": bool(failed_match), "Finished" : bool(finished_match)}



if __name__ == "__main__":
    with open("../tests/example_crab_status_output.txt") as f:
        data = f.read()
    status_parser(data)
