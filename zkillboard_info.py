import urllib.request
import json
import datetime

# Using a passed Solar System ID and range of days get the info from ZKillBoard API about kills happened in given time
# Return json obj
def get_Zkillboard_data(solar_system_id, hours_range, system_list):
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(hours=hours_range)
    start_time_param = str(current_time.year) + str(current_time.month).zfill(2) + \
                       str(current_time.day).zfill(2) + str(start_time.hour).zfill(2) + '00'
    solarSystemId_url = 'https://zkillboard.com/api/kills/solarSystemID/'+ solar_system_id +'/startTime/' + start_time_param + '/'

    contents = urllib.request.urlopen(solarSystemId_url).read()
    json_obj = json.loads(contents)

    if json_obj[0]['solar_system_id'] not in system_list:
        system_list.append(json_obj[0]['solar_system_id'])

    #for item in json_obj:
        #print(item['solar_system_id'])
        #system_list.append(json_obj[item]['solar_system_id'])
    #print(json_obj[1]['solar_system_id'])

    print('whatever')

    return