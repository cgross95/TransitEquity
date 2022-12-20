import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import pickle

walks = pd.read_csv("../raw_data/walk_to_red_line.csv", index_col=False)
stops = pd.read_csv("../raw_data/red_line_stops_lookup.csv", index_col='id')
segments = gpd.read_file("../shape_files/red_line_segments.shp")
gtfs = pd.read_csv("../raw_data/GTFS_ODMatrix_TravelTime.csv")


assumed_train_speed = 20 # assume train travels at 20 mph


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

# stops = name and stop number for each stop of proposed route
stop_num = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 18, 4, 15]
stops['stop_num'] = stop_num
stops = stops.set_index('Name').to_dict()['stop_num']

walks.replace(stops, inplace=True)

segments[['origin', 'dest']] = segments['OriginDest'].str.split(':', expand=True).astype(int)
segments = segments.loc[(segments['origin'] != 0) & (segments['dest'] != 0)]
segments['minutes'] = (segments['mileage'] / assumed_train_speed) * 60
segments = segments[['origin', 'dest', 'minutes']]

gtfs["dest"] = (
    gtfs["GeoID_Destination"].apply(lambda x: str(x)[-11:]).astype(str)
)
gtfs["origin"] = (
    gtfs["GoeID_Origin"].apply(lambda x: str(x)[-11:]).astype(str)
)
gtfs = gtfs[["origin", "dest", "TransitTime (minutes)"]]

# Compute all pairs shortest path
transit = gtfs.copy()
transit['minutes'] = transit["TransitTime (minutes)"]
transit = transit[["origin", "dest", "minutes"]]

G=nx.from_pandas_edgelist(pd.concat([walks, segments, transit]), 'origin', 'dest', ['minutes'])

path = dict(nx.all_pairs_bellman_ford_path_length(G, weight = 'minutes'))

distance = pd.DataFrame.from_dict(path)
distance = distance.drop(stop_num, axis=1).drop(stop_num, axis=0)

# Convert all pair shortest path matrix into data frame
long_form = distance.unstack()
long_form.index.rename(['origin', 'dest'], inplace=True)
long_form = long_form.to_frame('minutes').reset_index()

final = pd.merge(gtfs, long_form, on=['origin','dest'])
final = final.replace(["24510180100", "24510180200"], "24510280600")
final = final[~((final['origin'] == "24510280600") & (final['dest'] == "24510280600") & (final['minutes'] > 0))]
final = final.groupby(['origin','dest']).mean()
final.rename(columns={"TransitTime (minutes)": "transit_time_current", 'minutes': 'transit_time_with_red_line'}, inplace=True)
final.to_csv(f"../processed_data/transit_time_data.csv")

