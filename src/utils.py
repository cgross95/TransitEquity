import pandas as pd
import os
import urllib.request
import gzip
import shutil
from itertools import accumulate
import zipfile


def download_files(url, raw_path):
    zip_path, _ = urllib.request.urlretrieve(url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(raw_path)

def get_lodes_file(raw_path, lodes_type, file_name):
    lodes_file = raw_path + file_name
    if not os.path.isfile(lodes_file):
        print("Downloading LODES data into " + lodes_file)
        url = f"https://lehd.ces.census.gov/data/lodes/LODES7/md/{lodes_type}/{file_name}.gz"
        urllib.request.urlretrieve(url, raw_path + "tmp.gz")
        with gzip.open(raw_path + "tmp.gz", "rb") as f_in:
            with open(lodes_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(raw_path + "tmp.gz")
    lodes_data = pd.read_csv(lodes_file)
    return lodes_data

def set_paths(prefix = "../"):
    processed_relpath = f"{prefix}processed_data/"
    raw_relpath = f"{prefix}raw_data/"

    processed_path = os.path.join(processed_relpath)
    raw_path = os.path.join(raw_relpath)
    return raw_path, processed_path

def replace_tracts(df):
    return df.replace(["24510180100", "24510180200"], "24510280600")

def restrict_to_Baltimore(df, col):
    tracts = pd.read_csv("../raw_data/Baltimore_tracts.csv")['tracts'].astype(str).tolist()
    return df[df[col].isin(tracts)]

def extract_tract_FIPS(df, col):
    return df[col].apply(lambda x: str(x)[-11:])

def FIPS_to_str(df, col):
    return df[col].apply(lambda x: str(x)[:11])


def cumulativeSum(lst):
    return list(accumulate(lst))