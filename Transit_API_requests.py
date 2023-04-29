import os, urllib, json, csv
import requests
import numpy as np

# Add the Authorization header
'''
headers = {'apiKey': '0887dadd7934d9f08c73689aba903e2df4181b80799114188a1bc82cfc533e82'}


# This is the base URL for all Nautobot API calls
base_url = 'https://external.transitapp.com/v3/public/available_networks'

# Get the list of devices from Nautobot using the requests module and passing in the authorization header defined above
req = urllib.request.Request(base_url, headers=headers)
req.add_header('Accept', 'application/json')

response = urllib.request.urlopen(req)

content = response.read()
objs = json.loads(content)['networks']
for i in range(len(objs)):
    if objs[i]['network_location'] == 'Baltimore':
        print(objs[i]['network_id'])



base_url = 'https://external.transitapp.com/v3/public/routes_for_network?'

headers = {'apiKey': '0887dadd7934d9f08c73689aba903e2df4181b80799114188a1bc82cfc533e82'}

params =  {'network_id': 'Charm City Circulator|Baltimore'}
req = urllib.request.Request(base_url + urllib.parse.urlencode(params), headers=headers)

req.add_header('Accept', 'application/json')

response = urllib.request.urlopen(req)

content = response.read()
objs = json.loads(content)
print(objs)
'''



base_url = 'https://external.transitapp.com/v3/otp/plan?'

headers = {'apiKey': '0887dadd7934d9f08c73689aba903e2df4181b80799114188a1bc82cfc533e82'}

params =  {'date'         : '11/01/2022',
                    'time'            : '8:00AM',
                    'fromPlace'       : '%s,%s' % (39.2736267,-76.60028),
                    'toPlace'         : '%s,%s' % (39.2887712,-76.5887716),
                    'numItineraries'  : 10}
req = urllib.request.Request(base_url + urllib.parse.urlencode(params), headers=headers)

req.add_header('Accept', 'application/json')

response = urllib.request.urlopen(req)

content = response.read()
objs = json.loads(content)
durations = [i['duration'] for i in objs['plan']['itineraries']]
duration = np.min(durations)/60

print(duration)