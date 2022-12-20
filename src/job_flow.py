import pandas as pd
import os


processed_relpath = "../processed_data/"
raw_relpath = "../raw_data/"

processed_path = os.path.join(processed_relpath)
raw_path = os.path.join(raw_relpath)

# LODES data is too big to store on Github
lodes_file = raw_path + "md_od_main_JT00_2019.csv"
if not os.path.isfile(lodes_file):
    import urllib.request
    import gzip
    import shutil
    print("Downloading LODES data into " + lodes_file)
    url = "https://lehd.ces.census.gov/data/lodes/LODES7/md/od/md_od_main_JT00_2019.csv.gz"
    urllib.request.urlretrieve(url, raw_path + "tmp.gz")
    with gzip.open(raw_path + "tmp.gz", "rb") as f_in:
        with open(lodes_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(raw_path + "tmp.gz")
    

job_data = pd.read_csv(lodes_file)

# extract census tract
job_data["h_geocode"] = job_data["h_geocode"].apply(lambda x: str(x)[:11])
job_data["w_geocode"] = job_data["w_geocode"].apply(lambda x: str(x)[:11])
job_data.rename(columns={"S000": "job_totals"}, inplace=True)

job_data_tract = job_data[['h_geocode', 'w_geocode', "job_totals"]].copy()

job_data_tract = job_data_tract.groupby(['h_geocode', 'w_geocode']).sum().reset_index()
job_data_tract.to_csv(processed_path + "job_flows_tract.csv", index=False)