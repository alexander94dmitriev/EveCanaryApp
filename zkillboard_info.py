import urllib.request
import json
import datetime

# Using a passed Solar System ID and range of days get the info from ZKillBoard API about kills happened in given time
# Return json obj
def get_Zkillboard_data(solar_system_id, hours_range):
    dangerSystems = []
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(hours=hours_range)
    start_time_param = str(start_time.year) + str(start_time.month).zfill(2) + \
                       str(start_time.day).zfill(2) + str(start_time.hour).zfill(2) + '00'

    solar_systems = ",".join(solar_system_id)
    solarSystemId_url = 'https://zkillboard.com/api/kills/solarSystemID/'+ solar_systems +'/startTime/' + start_time_param + '/'

    contents = urllib.request.urlopen(solarSystemId_url).read()
    json_obj = json.loads(contents)

    if json_obj:
        for item in json_obj:
            if item['solar_system_id'] not in dangerSystems:
                dangerSystems.append(item['solar_system_id'])

    return dangerSystems
