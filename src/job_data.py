import pandas as pd
from utils import *

raw_path, processed_path = set_paths()

# See documentation at https://lehd.ces.census.gov/data/#lodes
# or https://lehd.ces.census.gov/data/lodes/LODES7/LODESTechDoc7.5.pdf

def compute_job_flow(seg = "S000", year = '2019'):
    job_flow_file = processed_path + f"job_flow_tract_{seg}.csv"
    if not os.path.isfile(job_flow_file):
        lodes_type = 'od'
        lodes_file = f"md_od_main_JT00_{year}.csv"
        job_data = get_lodes_file(raw_path, lodes_type, lodes_file)

        job_data["h_geocode"] = FIPS_to_str(job_data, "h_geocode")
        job_data["w_geocode"] = FIPS_to_str(job_data, "w_geocode")
        job_data.rename(columns={seg: "job_totals"}, inplace=True)

        job_data = job_data[['h_geocode', 'w_geocode', "job_totals"]]
        job_data = replace_tracts(job_data)
        job_data = restrict_to_Baltimore(job_data, 'h_geocode')
        job_data = restrict_to_Baltimore(job_data, 'w_geocode')

        job_data = job_data.groupby(['h_geocode', 'w_geocode']).sum().reset_index()
        job_data = job_data.loc[job_data["job_totals"] != 0]
        job_data.to_csv(job_flow_file, index=False)
    
    job_data = pd.read_csv(job_flow_file)
    return job_data

def compute_job_totals(seg = "S000", year = '2019'):
    job_totals_file = processed_path + f"job_totals_tract_{seg}.csv"
    if not os.path.isfile(job_totals_file):
        lodes_type = 'wac'
        lodes_file = f"md_wac_{seg}_JT00_{year}.csv"

        job_data = get_lodes_file(raw_path, lodes_type, lodes_file)

        job_data["tract_id"] = FIPS_to_str(job_data, "w_geocode")
        job_data = replace_tracts(job_data)
        job_data = restrict_to_Baltimore(job_data, 'tract_id')

        job_data.rename(columns={'C000': "job_totals"}, inplace=True)

        job_data = job_data[["tract_id", "job_totals"]]
        job_data = job_data.groupby("tract_id").sum().reset_index()
        job_data = job_data.loc[job_data["job_totals"] != 0]
        job_data.to_csv(job_totals_file, index=False)
        job_data = replace_tracts(job_data)
    
    job_data = pd.read_csv(job_totals_file)
    print(job_data["job_totals"].sum())
    return job_data

compute_job_totals()
compute_job_totals(seg = "SE01")
compute_job_totals(seg = "SE02")
compute_job_totals(seg = "SE03")