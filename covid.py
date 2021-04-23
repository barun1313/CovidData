import requests
import json
from datetime import datetime, timedelta

all_json = json.loads(requests.get("https://github.com/covid19india/api/blob/gh-pages/v4/min/data-all.min.json?raw=true", allow_redirects=True).content)
# https://api.covid19india.org/v4/data-all.json
# https://github.com/covid19india/api/blob/gh-pages/v4/min/data-all.min.json?raw=true

# x = {}
# for d in all_json:
#     if (state in all_json[d]) and ('districts' in all_json[d][state]) and (city in all_json[d][state]['districts']):
#         x[d] = all_json[d][state]['districts'][city]['total']

def clean_info(date, total_json):
    c = total_json['confirmed']
    d = total_json['deceased'] if 'deceased' in total_json else 0
    r = total_json['recovered'] if 'recovered' in total_json else 0
    a = c - d - r
    t = total_json['tested'] if 'tested' in total_json else 0
    return {"date": datetime.strptime(date,'%Y-%m-%d'), "confirmed": c, "active": a, "deceased": d, "recovered": r, "tested": t, "ratio_test_by_case": t/c}

def add_last_n_weeks_info (city_info, n):
    for day, day_info in enumerate(city_info):
        if day < 7*n:
            day_info[f"last_{n}_week"] = day_info["confirmed"]
            day_info[f"last_{n}_week_test"] = day_info["tested"]
            day_info[f"last_{n}_week_deceased"] = day_info["deceased"]
        else:
            day_info[f"last_{n}_week"] = day_info["confirmed"] - city_info[day - 7*n]["confirmed"]
            day_info[f"last_{n}_week_test"] = day_info["tested"] - city_info[day - 7*n]["tested"]
            day_info[f"last_{n}_week_deceased"] = day_info["deceased"] - city_info[day - 7*n]["deceased"]
        day_info[f"ratio_last_{n}_week_test_by_case"] = day_info[f"last_{n}_week_test"]/day_info[f"last_{n}_week"] if day_info[f"last_{n}_week"] else -1
        for i in range(day+1):
            if "active_equivalent_date" not in day_info:
                if day_info["active"] <= city_info[i]["active"]:
                    day_info["active_equivalent_date"] = city_info[i]["date"]
            if f"last_{n}_week_equivalent_date" not in day_info:
                if day_info[f"last_{n}_week"] <= city_info[i][f"last_{n}_week"]:
                    day_info[f"last_{n}_week_equivalent_date"] = city_info[i]["date"]
            if f"last_{n}_week_deceased_equivalent_date" not in day_info:
                if day_info[f"last_{n}_week_deceased"] <= city_info[i][f"last_{n}_week_deceased"]:
                    day_info[f"last_{n}_week_deceased_equivalent_date"] = city_info[i]["date"]

def print_city_info (state, city = None):
    factor = 1
    if "panch" in state.lower():
        state = 'MH'
        city = 'Satara'
        factor = 14894/3003741
    city_info = []
    for d in all_json:
        if city is None:
            if (state in all_json[d]):
                city_info.append(clean_info(d, all_json[d][state]['total']))
        else:
            if (state in all_json[d]) and ('districts' in all_json[d][state]) and (city in all_json[d][state]['districts']):
                city_info.append(clean_info(d, all_json[d][state]['districts'][city]['total']))

    city_info.sort(key = lambda x: x["date"])

    # fill details for missing days
    i = 1
    while i < len(city_info):
        gap = (city_info[i]["date"]-city_info[i-1]["date"]).days
        if gap != 1:
            print("MISSING DAY at {i}")
            input()
        i += 1

    add_last_n_weeks_info(city_info, 1)

    print("date,active,last 1 week,confirmed,active equivalent,last week equivalent,recovered,deceased,last week deceased,deceased equivalent,tested,last week tested,ratio test by case,ratio last week test by case")
    for day_info in city_info:
        print(f"{day_info['date'].strftime('%Y-%m-%d')},{factor*day_info['active']},{factor*day_info['last_1_week']},{factor*day_info['confirmed']},{day_info['active_equivalent_date'].strftime('%Y-%m-%d')},{day_info['last_1_week_equivalent_date'].strftime('%Y-%m-%d')},{factor*day_info['recovered']},{factor*day_info['deceased']},{factor*day_info['last_1_week_deceased']},{day_info['last_1_week_deceased_equivalent_date'].strftime('%Y-%m-%d')},{factor*day_info['tested']},{factor*day_info['last_1_week_test']},{day_info['ratio_test_by_case']},{day_info['ratio_last_1_week_test_by_case']}")

print_city_info('HR', 'Faridabad')
# print_city_info('UP', 'Kanpur Nagar')
