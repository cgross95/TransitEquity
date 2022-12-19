import pandas as pd
import os


processed_relpath = "../processed_data/"
raw_relpath = "../raw_data/"

processed_path = os.path.join(processed_relpath)
raw_path = os.path.join(raw_relpath)


job_data = pd.read_csv(raw_path + "md_od_main_JT00_2019.csv")

# extract census tract
job_data["h_geocode"] = job_data["h_geocode"].apply(lambda x: str(x)[:11])
job_data["w_geocode"] = job_data["w_geocode"].apply(lambda x: str(x)[:11])
job_data.rename(columns={"S000": "job_totals"}, inplace=True)

job_data_tract = job_data[['h_geocode', 'w_geocode', "job_totals"]].copy()

job_data_tract = job_data_tract.groupby(['h_geocode', 'w_geocode']).sum().reset_index()
job_data_tract.to_csv(processed_path + "job_flows_tract.csv", index=False)