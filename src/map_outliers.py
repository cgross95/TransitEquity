import geopandas
import pandas as pd
import contextily as cx
import matplotlib.pyplot as plt


def map_outliers(segment, speed, min_thresh, max_thresh, thresh_step):
    # outliers are always computed and mapped using pct_difference
    mode = "difference"  # can be pct_difference, only changes cloropleth coloring
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
            if mode == "pct_difference":
                gdf.loc[:, f"{var}_{mode}"] = 100 * gdf.loc[:, f"{var}_{mode}"]

            # Optionally mask out certain tracts if colors aren't informative
            if False:
                mask = gdf[f"{var}_{mode}"] > 10
                gdf_mask = gdf.loc[mask, :]
            else:
                gdf_mask = gdf

            mode_dict = {"difference": "change",
                         "pct_difference": "percent change"}
            var_dict = {"gravity_sum": "job accessibility",
                        "average_commute_time": "average commute time"}
            unit_dict = {"difference": {"gravity_sum": " (number of jobs)",
                                        "average_commute_time": " (minutes)"},
                         "pct_difference": {"gravity_sum": "",
                                            "average_commute_time": ""}
                        }
            label = f"{mode_dict[mode]} in {var_dict[var]} with Red Line{unit_dict[mode][var]}"

            ax = gdf_mask.plot(f"{var}_{mode}", figsize=(20, 20), alpha=0.5, edgecolor='k',
                               legend=True,
                               legend_kwds={'label': label,
                                            'orientation': "horizontal"})
            
            cent = gdf_mask.centroid
            for (x, y, svi) in zip(cent.x, cent.y, gdf["svi_pct_rank"]):
                ax.text(x, y, f"{svi:.0%}", fontsize=15, ha='center')
            cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom=13)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title("Tracts are colored by their change in the specified metric and labeled by their social vulnerability percentile (higher is more vulnerable)")
            plt.savefig(fname[:-4])
