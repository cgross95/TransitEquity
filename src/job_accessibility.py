import pandas as pd
import numpy as np
from utils import *

def impedance(time, thresh):
    return (thresh * 2) / (thresh + time)

# vars for data processing (from time data file)
time_data = "../processed_data/transit_time_data.csv"
modes = ['transit_current', 'red_line']
cols = {'transit_time_current', 'transit_time_with_red_line'}
time_col = dict(zip(modes, cols))

# Combine LODES Job Totals with Travel Times (GTFS or proposed times)
job_totals_tract = pd.read_csv("../processed_data/job_totals_tract.csv")
job_totals_tract["tract_id"] = job_totals_tract["tract_id"].astype(str)
job_totals_tract = replace_tracts(job_totals_tract)

travel_time = pd.read_csv(time_data)
travel_time["dest"] =  travel_time["dest"].astype(str)
travel_time["origin"] = travel_time["origin"].astype(str)

df = job_totals_tract.merge(travel_time, left_on="tract_id", right_on="dest")

df.drop("tract_id", axis=1, inplace=True)
df["tract_id"] = df["origin"].astype(str)

min_thresh = 45
max_thresh = 90
thresh_step = 15

for mode in modes:
    for thresh in range(min_thresh, max_thresh + thresh_step, thresh_step):
        below_df = df[df[time_col[mode]] <= thresh].copy()
        below_df["gravity"] = below_df[time_col[mode]].apply(lambda t: impedance(t, thresh))
        below_df["gravity"] = below_df["gravity"] * below_df["job_totals"]

        final_df = below_df[['tract_id', 'job_totals', 'gravity']].groupby('tract_id').sum()

        os.makedirs(
                f"../processed_data/job_accessibility/{mode}", exist_ok=True)

        final_df.to_csv(
                f"../processed_data/job_accessibility/{mode}/{int(thresh)}.csv")
