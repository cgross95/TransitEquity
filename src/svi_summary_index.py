"""
Computes summary SVI indices for census tracts 
(without missing data) in Baltimore city.
"""
import pandas as pd
import numpy as np
import geopandas
from sklearn.preprocessing import StandardScaler
from sys import argv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-svi2020', nargs=1, type=bool, 
	help='Use 2020 census data (otherwise 2018)')

if __name__ == '__main__':
	args = parser.parse_args(argv[1:])
	svi2020 = args.svi2020[0] if args.svi2020 != None else True
	if svi2020:
	    filename = "SVI_EP_2020_Standard_Scaled"
	    indicators = ["EP_POV150", "EP_UNEMP", "EP_HBURD", "EP_NOHSDP"]
	else:
	    filename = "SVI_EP_Standard_Scaled"
	    indicators = ["EP_POV", "EP_UNEMP", "EP_PCI", "EP_NOHSDP"]
	df_standard_scaled = pd.read_csv(f"../processed_data/{filename}.csv")
	
	socioecon_indicators = df_standard_scaled.loc[:, indicators]
	if not svi2020:
	    # Negate PCI so low numbers correspond to less vulnerable
	    socioecon_indicators['EP_PCI'] = -socioecon_indicators['EP_PCI']
	summary_index = socioecon_indicators.sum(axis=1)
	df_standard_scaled['svi_socioecon_summary'] = StandardScaler().fit_transform(summary_index.to_numpy().reshape(-1, 1))

	df_standard_scaled.to_csv(f"../processed_data/{filename}_Summary_Index.csv", index=False)

	path_to_data = "../shape_files/baltimore.shp"
	gdf = geopandas.read_file(path_to_data, SHAPE_RESTORE_SHX="YES")
	gdf = gdf[gdf["COUNTYFP"] == "510"] # Restrict to baltimore
	df_standard_scaled = df_standard_scaled.rename(columns={'FIPS': 'GEOID'})
	df_standard_scaled = df_standard_scaled.astype({'GEOID': str})
	gdf = pd.merge(gdf, df_standard_scaled, on="GEOID")
	gdf.explore("svi_socioecon_summary") 