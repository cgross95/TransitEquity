import pandas as pd
from utils import *

raw_path, processed_path = set_paths()

lodes_type = 'od'
lodes_file = "md_od_main_JT00_2019.csv"

job_data = get_lodes_file(raw_path, lodes_type, lodes_file)

# extract census tract
job_data["h_geocode"] = job_data["h_geocode"].apply(lambda x: str(x)[:11])
job_data["w_geocode"] = job_data["w_geocode"].apply(lambda x: str(x)[:11])
job_data.rename(columns={"S000": "job_totals"}, inplace=True)

job_data = job_data[['h_geocode', 'w_geocode', "job_totals"]]
job_data = replace_tracts(job_data)
job_data = restrict_to_Baltimore(job_data, 'h_geocode')
job_data = restrict_to_Baltimore(job_data, 'w_geocode')

job_data = job_data.groupby(['h_geocode', 'w_geocode']).sum().reset_index()
job_data.to_csv(processed_path + "job_flows_tract.csv", index=False)