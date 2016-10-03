# hub\_where
Hack-A-Week 11: Python script to gather data on Hubway's bike-sharing stations. 

Reason: I am a Hubway customer, and would like to know when the stations I
frequent are usually low on bikes.

I'll be leaving this script running on my laptop for as much time as possible
over the next week or so, so I'll have interesting data set to do fun things
with..

### Usage:
- Use `python hub_where.py` to run the hub\_where.py file

### Features:
- Uses python to gather and save data via Hubway's station\_status URL
- Only saves data when `last_reported` field has changed
- Shortens dict keys in order to save space

### What it does:
- If `last_updated.txt` file does not exist, creates last\_updated.txt as well
    as log files for each station
- Checks every 60 seconds if the data has been updated
- If the data has been updated, log any new data in the station log files
- Only add to the station log files if necessary in order to save space

### What it doesn't do:
- N/A

### Included Files:
```
- README.md..................This readme file
- hub_where.py...............Python script to gather data from Hubway
- data/......................Data gathered from Hubway
- last_updated.txt...........Text file to hold epoch time stamps
```
### Example Output:

