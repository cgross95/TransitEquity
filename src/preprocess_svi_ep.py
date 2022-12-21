"""
Outputs normalized percentage estimates of SVI indices for census tracts 
(without missing data) in Baltimore city.
"""
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, PowerTransformer
import seaborn as sns
import matplotlib.pyplot as plt
from sys import argv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-svi2020', nargs=1, type=bool, 
	help='Use 2020 census data (otherwise 2018)')

if __name__ == 'main':
	args = parser.parse_args(argv[1:])
	svi2020 = args.svi2020[0] if args.svi2020 != None else True
	raw = "svi_md_2020" if svi2020 else "svi_md"

	# Filter SVI data by Baltimore City county
	df = pd.read_csv(f"../raw_data/{raw}.csv")
	df = df.loc[df['STCNTY'] == 24510] 
	df = df.replace(-999, np.nan)

	# Extract the percentage estimate columns
	ep_df = df.loc[:, df.columns.str.contains('FIPS|EP_.*')]

	# Remove data for 2 census tracts with missing data
	drop_fips = [
	             24510250600,  # South harbor
	             24510100300   # Prison
	             ]
	drop_indices = ep_df.index[ep_df["FIPS"].isin(drop_fips)]
	ep_df = ep_df.drop(index=drop_indices)

	# Standardize data to mean zero, variance 1
	scaler = StandardScaler()
	df_temp = ep_df.drop(columns='FIPS')
	scaled_df = pd.DataFrame(scaler.fit_transform(df_temp), columns = df_temp.columns)

	# Add back the FIPS columns in final processing
	scaled_df['FIPS'] = list(ep_df['FIPS'])
	
	output = "SVI_EP_2020_Standard_Scaled" if svi2020 else "SVI_EP_Standard_Scaled"
	scaled_df.to_csv(f"../processed_data/{output}.csv", index=False)