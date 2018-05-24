import urllib.request
import json
import datetime

# Using a passed Solar System ID and range of days get the info from ZKillBoard API about kills happened in given time
# Return json obj
def get_Zkillboard_data(solar_system_id, minutes_range):
    danger_systems = []
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(minutes=minutes_range)
    start_time_param = str(start_time.year) + str(start_time.month).zfill(2) + \
                       str(start_time.day).zfill(2) + str(start_time.hour).zfill(2) + '00'

    solar_systems = ",".join(solar_system_id)
    solarSystemId_url = 'https://zkillboard.com/api/kills/solarSystemID/'+ solar_systems +'/startTime/' + start_time_param + '/'

    contents = urllib.request.urlopen(solarSystemId_url).read()
    json_obj = json.loads(contents)

    start_time = datetime.datetime(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
    current_time = datetime.datetime(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
    if json_obj:
        for item in json_obj:
            new_killmail_time = datetime.datetime.strptime(item['killmail_time'], '%Y-%m-%dT%H:%M:%SZ')
            if current_time >= new_killmail_time >= start_time:
                if item['solar_system_id'] not in danger_systems:
                    danger_systems.append(item['solar_system_id'])

    return danger_systems