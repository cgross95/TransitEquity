import geopandas
import pandas as pd
import contextily as cx
import matplotlib.pyplot as plt


def map_outliers(segment, speed, min_thresh, max_thresh, thresh_step):
    speed = int(speed)
    for thresh in range(min_thresh, max_thresh + thresh_step, thresh_step):
        for var in ["gravity_sum", "average_commute_time"]:
            fname = (
                f"../results/outliers/{segment}/{speed}/{thresh}/"
                f"pct_difference/{var}.csv"
            )

            path_to_data = "../shape_files/baltimore.shp"
            gdf = geopandas.read_file(path_to_data, SHAPE_RESTORE_SHX="YES")
            gdf = gdf.to_crs(epsg=3857)  # Ensure that CRS matches web map
            gdf = gdf[gdf["COUNTYFP"] == "510"]  # Restrict to baltimore
            outliers = pd.read_csv(fname)
            outliers = outliers.rename(columns={'FIPS': 'GEOID'})
            outliers = outliers.astype({'GEOID': str})
            gdf = pd.merge(gdf, outliers, on="GEOID", how="inner")
            # Set to be percentage out of 100
            gdf.loc[:, var] = 100 * gdf.loc[:, var]

            # Optionally mask out certain tracts if colors aren't informative
            if False:
                mask = gdf[var] > 10
                gdf_mask = gdf.loc[mask, :]
            else:
                gdf_mask = gdf

            if var == "gravity_sum":
                label = "% increase in job accessibility with Red Line"
            elif var == "average_commute_time":
                label = "% decrease in average commute time with Red Line"

            ax = gdf_mask.plot(var, figsize=(20, 20), alpha=0.5, edgecolor='k',
                               legend=True,
                               legend_kwds={'label': label,
                                            'orientation': "horizontal"})
            cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13)
            ax.set_xticks([])
            ax.set_yticks([])
            plt.savefig(fname[:-4])
