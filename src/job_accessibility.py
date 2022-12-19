import pandas as pd
import numpy as np
from functools import reduce


def impedance(time, thresh):
    return (thresh * 2) / (thresh + time)

# vars for data processing (from time data file)
time_data = "../processed_data/transit_time_data.csv"
time_metric = 'min' # col headers
#mode = 'min-transit'
mode = "transit"
# time_col = {mode: time_metric}
time_col = {'transit': 'TransitTimeOld'}

# Combine LODES Job Totals with Travel Times (GTFS or proposed times)
job_totals_tract = pd.read_csv("../processed_data/job_totals_tract.csv")
job_totals_tract["tract_id"] = job_totals_tract["tract_id"].astype(str)

travel_time = pd.read_csv(time_data)
travel_time["destination_tract_id"] =  travel_time["destination_tract_id"].apply(lambda x: str(x)[-11:]).astype(str)
travel_time["origin_tract_id"] = travel_time["origin_tract_id"].apply(lambda x: str(x)[-11:]).astype(str)

df = job_totals_tract.merge(
    travel_time, left_on="tract_id", right_on="destination_tract_id"
)[["origin_tract_id", "destination_tract_id", "job_totals", time_col[mode]]]
df["origin_tract_id"] = df["origin_tract_id"].astype(str)

min_thresh = 45
max_thresh = 90
thresh_step = 15

for thresh in range(min_thresh, max_thresh + thresh_step, thresh_step):
    below_df = df[df[time_col[mode]] <= thresh].copy()
    below_df["gravity"] = below_df[time_col[mode]].apply(lambda t: impedance(t, thresh))
    below_df["gravity"] = below_df["gravity"] * below_df["job_totals"]
    below_df.rename(columns={"origin_tract_id": "tract_id"}, inplace=True)

    final_df = below_df[['tract_id', 'job_totals', 'gravity']].groupby('tract_id').sum()

    final_df.to_csv(f"../processed_data/job_accessibility_{mode}_{int(thresh)}.csv")
