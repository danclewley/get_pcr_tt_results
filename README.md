# PCR TT Results Script #

A script to pull out Strava segment results over a given time period.

Specifically to pull out the three Plymouth Coastal Runners TT segments during the last weekend
of the month:

Segments are

* TT1: https://www.strava.com/segments/10014031
* TT2: https://www.strava.com/segments/10014001
* TT3: https://www.strava.com/segments/10074233
* Triple: https://www.strava.com/segments/13052821

## Getting API Key ##

This script requires a Strava API key.

You can create using a normal Strava account on http://labs.strava.com/developers/

Click on 'Manage your App' and this should give you options to create a new app.

For the options I used:

* Application Name - PCR
* Catergory - Other
* Website - https://www.strava.com
* Application Description - Left blank
* Authorization Callback Domain - strava.com

Once you have created your 'App' it will show a table with all the information. Look for 'Your Access Token'
and click show, it will be a long stream of random numbers and letters this is what you use to authenticate
the script (same as logging in via the website), it is passed in as `--dev_key`

## Install under Windows ##

Under Windows Python is not installed by default but may have been installed via another program. Open a 'Command prompt'
(search via start menu) and type:

```
python
```

If it returns information about the Python version followed by a new line starting with `>>>` you're good to go.
Type `exit()` to quit.

If not you need to install Python. I normally install via https://conda.io/miniconda.html, choose the Python 3
version (3.6 at time of writing) and follow the steps to install. Then open a command prompt and try typing `python`
again.

Change to where the script was downloaded to, for example:

```
cd C:\Users\Dan\Downloads
```

and type:

```
python get_pcr_tt_results.py
```

After pressing enter it should show:
```
usage: get_pcr_tt_results.py [-h]
(--segment_id SEGMENT_ID | --tt1 | --tt2 | --tt3)
        --start_date START_DATE --end_date END_DATE
        --dev_key DEV_KEY
get_pcr_tt_results.py: error: the following arguments are required: --start_date, --end_date, --dev_key
```
This means the script is working but you need to pass it the inputs, see the 'Usage' section.


## Install under macOS ##

Python is already installed under macOS by default. You should be able to run the script by opening the 'Terminal'
app (use spotlight to find it, the icon is a black box with `>_` in it). Once open type:

```
python ~/Downloads/get_pcr_tt_results.py
```

You can just type `python` and drag the '.py' file to the terminal window if you don't know the path.
Press enter and it should show:

```
usage: get_pcr_tt_results.py [-h]
(--segment_id SEGMENT_ID | --tt1 | --tt2 | --tt3)
        --start_date START_DATE --end_date END_DATE
        --dev_key DEV_KEY
get_pcr_tt_results.py: error: the following arguments are required: --start_date, --end_date, --dev_key
```

This means the script is working but you need to pass it the inputs. See the `Usage section`

## Usage ##

It is recommended you copy these commands to a text file (e.g., in Notepad) so they are easier to edit then paste them
from there to the command prompt / Terminal.

To run for TT1 use:

```
python get_pcr_tt_results.py --tt1 --dev_key YOUR_DEV_KEY \
                             --start_date 2017-05-27T00:00:00 \
                             --end_date 2017-05-29T23:59:59

```
Replacing `YOUR_DEV_KEY` with your Strava API code and editing the start and end date as required.

This should print something like:

```
Name, Time, Position, Gender, Date, PB, URL
First, Last, 1:00:00, 1, M, 2017-05-28T10:00:00Z, First Time, https://www.strava.com/activities/0000000
First, Last, 1:10:00, 2, F, 2017-05-28T10:00:00Z, PB, https://www.strava.com/activities/0000000
First, Last, 1:20:00, 3, M, 2017-05-28T10:00:00Z, ,https://www.strava.com/activities/0000000
```

Which can be copied into Excel.

For TT2, TT3 and the triple (3-2-1), the `--tt2`, `--tt3` and `-tt321` flags are used instead
