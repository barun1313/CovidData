import requests
import json
import sys # For progress bar
import datetime

# Source: https://stackoverflow.com/a/15860757
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:.2f}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def headers():
    return {'authority': 'cdn-api.co-vin.in',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not\\A\"Brand";v="99"',
            'accept': 'application/json, text/plain, */*',
            # 'authorization': auth,
            'sec-ch-ua-mobile': '?1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Mobile Safari/537.36',
            'origin': 'https://selfregistration.cowin.gov.in',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://selfregistration.cowin.gov.in/',
            'accept-language': 'en-US,en;q=0.9',
        }

# authorization = ''
# r = None

def g(district_id, min_age_limit = 18, available_capacity = 1):
    global r
    available = []
    r = requests.get(f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={district_id}&date={datetime.datetime.now().strftime("%d-%m-%Y")}', headers=headers())
    centers_count = len(r.json()['centers'])
    start = datetime.datetime.now()
    print (f"Query for {centers_count} centers started at {start}")
    update_progress(0)
    for i, center in enumerate(r.json()['centers']):
        if 'sessions' in center:
            sessions = []
            for sess in center['sessions']:
                if (sess['available_capacity'] >= available_capacity) and (sess['min_age_limit'] == min_age_limit):
                    sessions.append(sess.copy())
            if len(sessions):
                details = set(center.keys()) - set(['sessions'])
                mini_center = {k: center[k] for k in details}
                mini_center['sessions'] = sessions.copy()
                available.append(mini_center)
        update_progress((i+1)/centers_count)

    end = datetime.datetime.now()
    print ("Query ended at", end)
    print(f'Total time taken: {end-start}')
    print(f'Time taken for each center: {(end-start)/centers_count}')
    print(f'Slots available at {len(available)} centers')
    return available

def f(available_capacity = 1):
    # global authorization
    # x = input('authorization (blank if unchanged): ').strip()
    # if x != '':
    #     authorization = x
    state = input('state: ').lower().strip()
    district = input('district (blank if all): ').lower().strip()
    r = requests.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/states', headers=headers())
    for s in r.json()['states']:
        if s['state_name'].lower().strip() == state:
            sid = s['state_id']
    r = requests.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{sid}', headers=headers())
    slots = []
    if district == '':
        for d in r.json()['districts']:
            slots += g(d['district_id'], available_capacity = available_capacity)
    else:
        for d in r.json()['districts']:
            if d['district_name'].lower().strip() == district:
                slots += g(d['district_id'], available_capacity = available_capacity)
    print(json.dumps(slots, sort_keys=True, indent=2))
    return slots


x = f()
