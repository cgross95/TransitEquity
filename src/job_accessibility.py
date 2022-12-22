import pandas as pd
import numpy as np
from utils import *

raw_path, processed_path = set_paths()

def impedance(time, thresh):
    return (thresh * 2) / (thresh + time) - 1

modes = ['transit_current', 'red_line']
cols = {'transit_time_current', 'transit_time_with_red_line'}
time_col = {'transit_current': 'transit_time_current', 'red_line': 'transit_time_with_red_line'}

def compute_job_accessibility(travel_time, job_totals, seg, assumed_train_speed):

    df = job_totals.merge(travel_time, left_on="tract_id", right_on="dest")

    df.drop("tract_id", axis=1, inplace=True)
    df.rename(columns={"origin": "tract_id",}, inplace=True)

    min_thresh = 15
    max_thresh = 90
    thresh_step = 15

    for mode in modes:
        for thresh in range(min_thresh, max_thresh + thresh_step, thresh_step):
            below_df = df[df[time_col[mode]] <= thresh].copy()
            below_df["gravity"] = below_df[time_col[mode]].apply(lambda t: impedance(t, thresh))
            below_df["gravity"] = below_df["gravity"] * below_df["job_totals"]

            final_df = below_df[['tract_id', 'job_totals', 'gravity']].groupby('tract_id').sum()

            dir_path = processed_path + f"job_accessibility/{seg}/{int(assumed_train_speed)}/{mode}"

            os.makedirs(dir_path, exist_ok=True)

            final_df.to_csv(f"{dir_path}/{int(thresh)}.csv")
