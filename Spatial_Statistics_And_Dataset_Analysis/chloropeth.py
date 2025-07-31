import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from libpysal.weights import KNN
from esda import Geary_Local
import matplotlib.pyplot as plt
import numpy as np  # Import numpy

# --- Specify the path to your CSV file ---
csv_file_path = '/Users/ullas/Desktop/STDA-PROJECT/network performance.csv'  # Replace with the actual path to your CSV file

# --- Specify the path to your governorate shapefile ---
governorate_shapefile_path = '/Users/ullas/Desktop/STDA-PROJECT/eg_shp/eg.shp'  # Replace with the actual path

try:
    # --- Read the CSV file into a pandas DataFrame ---
    df = pd.read_csv(csv_file_path)

    # --- Get the unique city names ---
    unique_cities = df['city'].unique().tolist()

    # --- Create a dictionary to store city coordinates (using the first occurrence) ---
    city_coordinates = {}
    for city in unique_cities:
        city_row = df[df['city'] == city].iloc[0]
        city_coordinates[city] = (city_row['centroid_lon'], city_row['centroid_lat'])

    # --- Load the governorate shapefile ---
    governorates_gdf = gpd.read_file(governorate_shapefile_path)

    # --- Function to find the governorate of a city (using coordinates) ---
    def find_governorate(city_name, governorates_gdf, city_lat_lon_dict):
        if city_name in city_lat_lon_dict:
            lon, lat = city_lat_lon_dict[city_name]
            point = Point(lon, lat)
            for index, row in governorates_gdf.iterrows():
                if row['geometry'].contains(point):
                    return row['name']  # Assuming 'name' column holds governorate names
            return None  # If the city point doesn't fall within any governorate
        else:
            return "Coordinates not available for this city"

    # --- Map each unique city to its governorate ---
    city_governorate_mapping = {}
    for city in unique_cities:
        governorate = find_governorate(city, governorates_gdf, city_coordinates)
        city_governorate_mapping[city] = governorate

    # --- Add governorate information to the original DataFrame based on the mapping ---
    df['governorate'] = df['city'].map(city_governorate_mapping)

    # --- Compute spatial weights ---
    geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)
    w = KNN.from_dataframe(gdf, k=8)
    w.transform = 'R'

    # --- Calculate Local Geary's C for 'avg_d_speed_mbps' ---
    x = gdf['avg_d_speed_mbps'].values
    geary_local = Geary_Local(connectivity=w).fit(x)
    gdf['avg_d_speed_mbps_local_geary'] = geary_local.localG
    gdf['avg_d_speed_mbps_local_geary_p_value'] = geary_local.p_sim  # Get p-values

    # --- Calculate average Geary's C for each governorate ---
    governorate_geary_c = gdf.groupby('governorate').agg(
        avg_geary_c=('avg_d_speed_mbps_local_geary', 'mean'),
        avg_p_value=('avg_d_speed_mbps_local_geary_p_value', 'mean')  # Average p-values
    ).reset_index()

    # --- Merge the Geary's C values with the governorates GeoDataFrame ---
    governorates_gdf = governorates_gdf.merge(governorate_geary_c, left_on='name', right_on='governorate', how='left')

    # --- Plot the choropleth map ---
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Color the governorates based on average Geary's C
    governorates_gdf.plot(
        column='avg_geary_c',
        cmap='viridis_r',
        linewidth=0.8,
        ax=ax,
        edgecolor='0.8',
        legend=True,
        legend_kwds={'label': "Avg. Local Geary's C (Download Speed)", 'orientation': "horizontal"}
    )

    # --- Add governorate names to the plot ---
    for idx, row in governorates_gdf.iterrows():
        centroid = row['geometry'].centroid
        governorate_name = row['name']
        ax.text(centroid.x, centroid.y, governorate_name,
                horizontalalignment='center', verticalalignment='center',
                fontsize=8, color='black',
                )



    ax.set_title(
        "Governorate Avg. Geary's C for Download Speed with Governorate Names and Significant City Clusters (p < 0.05)")
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig('geary_chloropeth.png', dpi=300)
    plt.show()

except FileNotFoundError as e:
        print(f"Error: File not found at '{e.filename}'. Please check the file path.")
except KeyError as e:
        print(
            f"Error: Column '{e}' not found in the CSV/Shapefile. Please ensure the required columns are present.")
except Exception as e:
        print(f"An error occurred: {e}")
