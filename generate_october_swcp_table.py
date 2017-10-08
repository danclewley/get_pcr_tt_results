#!/usr/bin/env python3
"""
PCR October SWCP TT results script.

Uses Strava API to get results within a given date range
(i.e., the TT weekend) and prints a table of results
which can be copied to main spreadsheet.

Requires developer API key, see https://strava.github.io/api/

Author: Dan Clewley
Date: 2017-10-02

"""

import argparse
import copy
from datetime import timedelta
import json
import sys

if sys.version_info.major < 3:
    import urllib2 as request
    import urllib as parse
else:
    from urllib import parse
    from urllib import request

HAVE_TABULATE = True
try:
    import tabulate
except ImportError:
    HAVE_TABULATE = False

# URL to get all info from a segment
# see https://strava.github.io/api/v3/segments/
SEGMENT_URL = "https://www.strava.com/api/v3/segments/{}/all_efforts"

# URL to get info about an athelete
# see https://strava.github.io/api/v3/athlete/
ATHLETE_URL = "https://www.strava.com/api/v3/athletes/{}"

# URL to display an activity (non API)
ACTIVITY_URL = "https://www.strava.com/activities/{}"

# Segment IDs
TT1_SEGMENT_ID = 10014031
TT2_SEGMENT_ID = 10014001
TT3_SEGMENT_ID = 10074233
TT321_SEGMENT_ID = 13052821

if __name__ == "__main__":

    # Read input from command line
    parser = argparse.ArgumentParser(description="Get PCR TT efforts within a given date range")
    parser.add_argument("--start_date",
                        required=False,
                        help="Start date in format YY-MM-DD (assumes time is 00:00:00)",
                        default="2017-10-01")
    parser.add_argument("--end_date",
                        required=False,
                        help="End date in format YY-MM-DD (assumes time is 23:59:59)",
                        default="2017-10-31")
    parser.add_argument("--dev_key",
                        required=True,
                        help="Strava development key for authentication")
    parser.add_argument("--pritty_print",
                    action="store_true",
                    default=False,
                    help="Format table for better output")
    args = parser.parse_args()
    
    all_segments = {"TT1" : TT1_SEGMENT_ID,
                    "TT2" : TT2_SEGMENT_ID,
                    "TT3" : TT3_SEGMENT_ID,
                    "Triple" : TT321_SEGMENT_ID}
    segment_points = {"TT1" : 1,
                      "TT2" : 2,
                      "TT3" : 3,
                      "Triple" : 3}


    # Results dictionary template - used for each athelete
    results_dict = {"TT1" : 0, "TT2" : 0, "TT3" : 0,
                    "Triple" : 0, "PBs" : 0, "Total" : 0}

    # Set up dictionary for atheletes, pairs are athletes : results_dict
    results_athelete = {}
    
    # Set date
    date_data = parse.urlencode({"start_date_local" : "{}T00:00:00Z".format(args.start_date), 
                                        "end_date_local"   : "{}T23:59:59Z".format(args.end_date)})
    
    for segment_name, segment_id in all_segments.items():
        # Get all segment efforts
        seg_req = request.Request(SEGMENT_URL.format(segment_id), date_data.encode(),
                              {"Authorization" : "Bearer {}".format(args.dev_key)},
                              method="GET")
        seg_req_str = request.urlopen(seg_req).read()
        
        seg_req_dict = json.loads(seg_req_str.decode())

        for pos, effort in enumerate(seg_req_dict):
            athlete_id = effort["athlete"]["id"]
            activity_id = effort["activity"]["id"]
            activity_url = ACTIVITY_URL.format(activity_id)
            time_sec = effort["elapsed_time"]
            time_hours = str(timedelta(seconds=(time_sec)))
            date = effort["start_date_local"]
        
            # Get athlete name and gender
            athlete_req = request.Request(ATHLETE_URL.format(athlete_id), None,
                                                 {"Authorization" : "Bearer {}".format(args.dev_key)})
            athlete_req_str = request.urlopen(athlete_req).read()
            athlete_req_dict = json.loads(athlete_req_str.decode())
        
            name = "{} {}".format(athlete_req_dict["firstname"], athlete_req_dict["lastname"])
            sex = athlete_req_dict["sex"]
            
        
            # Add to totals
            try:
                results_athelete[name][segment_name] += 1
                results_athelete[name]["Total"] += segment_points[segment_name]
            # If first attempt set up results structure and add points
            except KeyError:
                results_athelete[name] = copy.copy(results_dict)
                results_athelete[name][segment_name] = 1
                results_athelete[name]["Total"] += segment_points[segment_name]

            # If segment was PB this
            if effort["pr_rank"] == 1:
                results_athelete[name]["PBs"] += 1
                results_athelete[name]["Total"] += 5

    # Print out table
    header = ["Name", "TT1", "TT2", "TT3", "The Triple", "PBs", "Points"]

    results_lines = []

    for athelete, results in results_athelete.items():
        tt1_attempts = results["TT1"]
        tt2_attempts = results["TT2"]
        tt3_attempts = results["TT3"]
        triple_attempts = results["Triple"]
        pb_attempts = results["PBs"]
        total_points = results["Total"]

        out_line = [athelete, tt1_attempts, tt2_attempts, tt3_attempts,
                    triple_attempts, pb_attempts, total_points]
        results_lines.append(out_line)


    if args.pritty_print and HAVE_TABULATE:
        print(tabulate.tabulate(results_lines, header, tablefmt="fancy_grid"))
    else:
        print(",".join(header))
        for line in results_lines:
            line = [str(i) for i in line]
            print(",".join(line))
