import pandas as pd
from utils import *

import pandas as pd
import geopandas as gpd
import os, urllib, json, csv
from tqdm import tqdm
import numpy as np

raw_path, processed_path = set_paths()

def get_all_pair_transit_time(output_file, job_flow, tract_file = "2020_Gaz_tracts_24.txt", date = '11/01/2022', time = '08:00AM'):
    output_path = processed_path + output_file
    if not os.path.isfile(output_path):
        year = tract_file[:4]
        if not os.path.isfile(raw_path + tract_file):
            url = f'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{year}_Gazetteer/{tract_file}'
            urllib.request.urlretrieve(url, raw_path + tract_file)
        with open(raw_path + tract_file) as f:
            tracts = pd.read_csv(f, delimiter='\s+')
        f.close()

        tracts = tracts[['GEOID', 'INTPTLAT', 'INTPTLONG']]
        # This is specific to maryland tracts
        tracts.loc[1456,['INTPTLAT', 'INTPTLONG']] = [39.34673721019194, -76.68057889700162]

        df = job_flow.merge(tracts, left_on="h_geocode", right_on="GEOID").merge(tracts, left_on="w_geocode", right_on="GEOID")
        df.rename(
            columns={
                "INTPTLAT_x": "start_lat",
                "INTPTLONG_x": "start_lon",
                "INTPTLAT_y": "end_lat",
                "INTPTLONG_y": "end_lon",
            },
            inplace=True,
        )
        df = df[['h_geocode', 'w_geocode', 'job_totals', 'start_lat', 'start_lon', 'end_lat', 'end_lon']]

        df['Date'] = date
        df['Time'] = time
        df = df.drop_duplicates()

        # Find all travel times via API calls
        URL = 'http://localhost:8080/otp/routers/default/plan?'

        outputFile = open(output_path, 'w')
        writer = csv.writer(outputFile)
        writer.writerow(['origin','dest','job_totals','start_lat','start_lon','end_lat', 'end_lon', 'Date', 'Time', 'minutes'])

        # Takes CSV input, creates URLs, stores data locally in row array
        for _, d in tqdm(df.iterrows(), total=df.shape[0]):
            params =  {'date'         : d['Date'],
                    'time'            : d['Time'],
                    'fromPlace'       : '%s,%s' % (d['start_lat'], d['start_lon']),
                    'toPlace'         : '%s,%s' % (d['end_lat'], d['end_lon']),
                    'numItineraries'  : 10}
            req = urllib.request.Request(URL + urllib.parse.urlencode(params))
            req.add_header('Accept', 'application/json')

            if(d['h_geocode'] == d['w_geocode']):
                outrow = d.tolist() + [0]
                writer.writerow(outrow)
            else:
                response = urllib.request.urlopen(req)
                try :
                    content = response.read()
                    objs = json.loads(content)
                    durations = [i['duration'] for i in objs['plan']['itineraries']]
                    duration = np.min(durations)
                    outrow = d.tolist() + [duration/60]
                    writer.writerow(outrow)
                except :
                    print(d)
                    print ('no itineraries')
        outputFile.close()


def compute_transit_time(gtfs_current, gtfs_red_line, speed = 20, period = 8):
    transit_time_file = processed_path + f"transit_time_data_speed_{int(speed)}_period_{period}.csv"
    if not os.path.isfile(transit_time_file):
        current = pd.read_csv(f"{processed_path}{gtfs_current}")[['origin','dest','minutes']].rename(columns={"minutes": "transit_time_current"})
        red_line = pd.read_csv(f"{processed_path}{gtfs_red_line}")[['origin','dest','minutes']].rename(columns={"minutes": "transit_time_with_red_line"})

        final = pd.merge(current, red_line, on=['origin','dest'])

        final.to_csv(transit_time_file, index = False)
        
    final = pd.read_csv(transit_time_file)
    return final