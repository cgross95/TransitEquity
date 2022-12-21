import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from utils import *
import pickle

_, processed_path = set_paths()


def preprocessing():
    processed_file = processed_path + "preprocessed_transit_time.pkl"
    if os.path.isfile(processed_file):
        walks, segments, transit, gtfs, stop_num = pickle.load(open(processed_file,'rb'))
    else:
        # walking time to red line stops
        walks = pd.read_csv("../raw_data/walk_to_red_line.csv", index_col=False)
        # red line stops
        stops = pd.read_csv("../raw_data/red_line_stops_lookup.csv", index_col='id')
        # red line segments
        segments = gpd.read_file("../shape_files/red_line_segments.shp")
        # commute time matrix
        gtfs = pd.read_csv("../raw_data/GTFS_ODMatrix_TravelTime.csv")


        # walks = data for walking to the nearest red line stop  
        walks['origin'] = (
            walks['centroids_15min: STATEFP'].astype(str)
            + walks['centroids_15min: COUNTYFP'].astype(str).str.pad(3, "left", "0")
            + walks['centroids_15min: TRACTCE'].astype(str).str.pad(6, "left", "0")
        )
        walks.rename(
            columns={
                "Near Layer: Name": "dest",
                "Minimum Travel Time (Minutes)": "minutes",
            },
            inplace=True,
        )
        walks = walks[['origin', 'dest', 'minutes']]

        segments[['origin', 'dest']] = segments['OriginDest'].str.split(':', expand=True).astype(int)
        segments = segments.loc[(segments['origin'] != 0) & (segments['dest'] != 0)]

        # stops = name and stop number for each stop of proposed route
        stop_num = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 18, 4, 15]
        stops['stop_num'] = stop_num
        stops = stops.set_index('Name').to_dict()['stop_num']

        walks.replace(stops, inplace=True)

        gtfs["dest"] = extract_tract_FIPS(gtfs, "GeoID_Destination")

        gtfs["origin"] = extract_tract_FIPS(gtfs, "GoeID_Origin")

        gtfs = gtfs[["origin", "dest", "TransitTime (minutes)"]]

        transit = gtfs.copy()
        transit['minutes'] = transit["TransitTime (minutes)"]
        transit = transit[["origin", "dest", "minutes"]]
        pickle.dump((walks, segments, transit, gtfs, stop_num), open(processed_file, 'wb'))
    return walks, segments, transit, gtfs, stop_num



def compute_transit_time(assumed_train_speed = 20):
    transit_time_file = processed_path + f"transit_time_data_speed_{assumed_train_speed}.csv"
    if os.path.isfile(transit_time_file):
        final = pd.read_csv(transit_time_file)
    else:
        walks, segments, transit, gtfs, stop_num = preprocessing()
        segments['minutes'] = (segments['mileage'] / assumed_train_speed) * 60
        segments = segments[['origin', 'dest', 'minutes']]

        # Compute all pairs shortest path
        G=nx.from_pandas_edgelist(pd.concat([walks, segments, transit]), 'origin', 'dest', ['minutes'])

        path = dict(nx.all_pairs_bellman_ford_path_length(G, weight = 'minutes'))

        distance = pd.DataFrame.from_dict(path)
        distance = distance.drop(stop_num, axis=1).drop(stop_num, axis=0)

        # Convert all pair shortest path matrix into data frame
        long_form = distance.unstack()
        long_form.index.rename(['origin', 'dest'], inplace=True)
        long_form = long_form.to_frame('minutes').reset_index()

        final = pd.merge(gtfs, long_form, on=['origin','dest'])
        final = replace_tracts(final)
        final = final[~((final['origin'] == "24510280600") & (final['dest'] == "24510280600") & (final['minutes'] > 0))]
        final = final.groupby(['origin','dest']).mean()
        final.rename(columns={"TransitTime (minutes)": "transit_time_current", 'minutes': 'transit_time_with_red_line'}, inplace=True)
        final.to_csv(transit_time_file)
    return final