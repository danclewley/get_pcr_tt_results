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
import time
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
# see https://developers.strava.com/docs/reference/#api-Segments-getLeaderboardBySegmentId
SEGMENT_URL = "https://www.strava.com/api/v3/segments/{}/leaderboard"

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
parser.add_argument("--pritty_print",
                    action="store_true",
                    default=False,
                    help="Format table for better output")
parser.add_argument("--start_date",
                    required=True,
                    help="Start date in format YY-MM-DDTHH:MM:SS")
parser.add_argument("--end_date",
                    required=True,
                    help="End date in format YY-MM-DDTHH:MM:SS")
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

start_time = time.strptime(args.start_date, "%Y-%m-%dT%H:%M:%S")
end_time = time.strptime(args.end_date, "%Y-%m-%dT%H:%M:%S")

start_time_epoch = time.mktime(start_time)
end_time_epoch = time.mktime(end_time)

# If results are for current month then only get results for month
# else need to get for year.
if end_time.tm_mon == time.gmtime().tm_mon:
    date_range = "this_month"
else:
    date_range = "this_year"

# Set date
date_data = parse.urlencode({"date_range" : date_range,
                             "per_page" : "200"},)

# Get all segment efforts
seg_req = request.Request(SEGMENT_URL.format(segment_id), date_data.encode(),
                      {"Authorization" : "Bearer {}".format(args.dev_key)},
                      method="GET")
seg_req_str = request.urlopen(seg_req).read()
seg_req_dict = json.loads(seg_req_str.decode())
seg_req_dict = seg_req_dict["entries"]

# Sort by time
seg_req_dict =  sorted(seg_req_dict, key=_get_time)

header = ["Name", "Time", "Position", "Gender", "Date", "PB", "URL"]
results_lines = []

for pos, effort in enumerate(seg_req_dict):
    name = effort["athlete_name"]
    time_sec = effort["elapsed_time"]
    time_hours = str(timedelta(seconds=(time_sec)))
    date = effort["start_date_local"]
    date_epoch = time.mktime(time.strptime(date[:-1], "%Y-%m-%dT%H:%M:%S"))

    sex = ""
    pb_string = ""
    activity_url = ""
    out_line = [name, time_hours, pos+1, sex,
                date, pb_string, activity_url]

    if date_epoch > start_time_epoch and date_epoch < end_time_epoch:
        results_lines.append(out_line)

if args.pritty_print and HAVE_TABULATE:
    print(tabulate.tabulate(results_lines, header, tablefmt="fancy_grid"))
else:
    print(",".join(header))
    for line in results_lines:
        line = [str(i) for i in line]
        print(",".join(line))

