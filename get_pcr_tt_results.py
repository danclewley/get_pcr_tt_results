#!/usr/bin/env python3
"""
PCR TT results script.

Uses Strava API to get results within a given date range
(i.e., the TT weekend) and prints a table of results
which can be copied to main spreadsheet.

Requires developer API key, see https://strava.github.io/api/

Example usage:

get_pcr_tt_results.py --tt1 --dev_key YOUR_KEY --start_date 2017-05-27 --end_date 2017-05-29

Author: Dan Clewley
Date: 2017-06-02

"""

import argparse
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

# Read input from command line
parser = argparse.ArgumentParser(description="Get PCR TT efforts within a given date range")
segment_group = parser.add_mutually_exclusive_group(required=True)
segment_group.add_argument("--segment_id",
                           help="Manually enter segment ID")
segment_group.add_argument("--tt1",
                           action="store_true",
                           default=False,
                           help="List efforts for TT1")
segment_group.add_argument("--tt2",
                           action="store_true",
                           default=False,
                           help="List efforts for TT2")
segment_group.add_argument("--tt3",
                           action="store_true",
                           default=False,
                           help="List efforts for TT3")
segment_group.add_argument("--tt321",
                           action="store_true",
                           default=False,
                           help="List efforts for the triple 3-2-1")
parser.add_argument("--num_attempts",
                    action="store_true",
                    default=False,
                    help="Print number of times an athlete has attemted the "
                         "segment")
parser.add_argument("--pritty_print",
                    action="store_true",
                    default=False,
                    help="Format table for better output")
parser.add_argument("--start_date",
                    required=True,
                    help="Start date in format YY-MM-DD (assumes time is 00:00:00)")
parser.add_argument("--end_date",
                    required=True,
                    help="End date in format YY-MM-DD (assumes time is 23:59:59)")
parser.add_argument("--dev_key",
                    required=True,
                    help="Strava development key for authentication")
args = parser.parse_args()

segment_id = None

# Get segment ID from defaults
if args.tt1:
    segment_id = TT1_SEGMENT_ID
elif args.tt2:
    segment_id = TT2_SEGMENT_ID
elif args.tt3:
    segment_id = TT3_SEGMENT_ID
elif args.tt321:
    segment_id = TT321_SEGMENT_ID
else:
    segment_id = args.segment_id

def _get_time(item):
    """
    Get time from segment JSON.
    Used for sorting
    """
    return item["elapsed_time"]

# Set date
date_data = parse.urlencode({"start_date_local" : "{}T00:00:00Z".format(args.start_date), 
                             "end_date_local"   : "{}T23:59:59Z".format(args.end_date),
                             "per_page" : "100"},)

# Get all segment efforts
seg_req = request.Request(SEGMENT_URL.format(segment_id), date_data.encode(),
                      {"Authorization" : "Bearer {}".format(args.dev_key)},
                      method="GET")
seg_req_str = request.urlopen(seg_req).read()
seg_req_dict = json.loads(seg_req_str.decode())

# Sort by time
seg_req_dict =  sorted(seg_req_dict, key=_get_time)

header = ["Name", "Time", "Position", "Gender", "Date", "PB", "URL"]
results_lines = []

total_attempts_athelete = {}

for pos, effort in enumerate(seg_req_dict):
    athlete_id = effort["athlete"]["id"]
    activity_id = effort["activity"]["id"]
    activity_url = ACTIVITY_URL.format(activity_id)
    time_sec = effort["elapsed_time"]
    time_hours = str(timedelta(seconds=(time_sec)))
    date = effort["start_date_local"]

    # Check for personal segment rank
    # If None is first time for segment
    if effort["pr_rank"] == 1:
        pb_string = "PB"
    else:
        pb_string = ""

    # Get athlete name and gender
    athlete_req = request.Request(ATHLETE_URL.format(athlete_id), None,
                                         {"Authorization" : "Bearer {}".format(args.dev_key)})
    athlete_req_str = request.urlopen(athlete_req).read()
    athlete_req_dict = json.loads(athlete_req_str.decode())

    name = "{} {}".format(athlete_req_dict["firstname"], athlete_req_dict["lastname"])
    sex = athlete_req_dict["sex"]

    # Itterate total attempts for athelete
    try:
        total_attempts_athelete[name] += 1
    except KeyError:
        total_attempts_athelete[name] = 1

    out_line = [name, time_hours, pos+1, sex,
                date, pb_string, activity_url]

    results_lines.append(out_line)


if args.pritty_print and HAVE_TABULATE:
    print(tabulate.tabulate(results_lines, header, tablefmt="fancy_grid"))
else:
    print(",".join(header))
    for line in results_lines:
        line = [str(i) for i in line]
        print(",".join(line))


if args.num_attempts:
    print("\n\n")
    print("Name, NumAttempts")
    for key, value in total_attempts_athelete.items():
        print(key, value)
