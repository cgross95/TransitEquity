import pandas as pd
from utils import *

raw_path, processed_path = set_paths()

lodes_type = 'wac'
lodes_file = "md_wac_S000_JT00_2019.csv"

job_data = get_lodes_file(raw_path, lodes_type, lodes_file)

job_data["tract_id"] = job_data["w_geocode"].apply(lambda x: str(x)[:11])
job_data = replace_tracts(job_data)
job_data = restrict_to_Baltimore(job_data, 'tract_id')

job_data.rename(columns={"C000": "job_totals", "CD01": "Less than high school", 
    "CD02": "High school or equivalent, no college", "w_geocode": "block_id"}, inplace=True)

job_data_tract = job_data[["tract_id", "job_totals"]]
job_data_tract = job_data_tract.groupby("tract_id").sum().reset_index()
job_data_tract.to_csv(processed_path + "job_totals_tract.csv", index=False)