import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np

# --- 1. Load your network performance CSV data ---
csv_file_path = '/Users/ullas/Desktop/STDA-PROJECT/network performance.csv'  # Replace with your actual path
try:
    df = pd.read_csv(csv_file_path)
except FileNotFoundError:
    print(f"Error: CSV file not found at {csv_file_path}")
    exit()

# --- 2. Create GeoDataFrame from the CSV data ---
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)  # Project to a suitable CRS for distance calculations (e.g., meters)

# --- 3. Sample the data ---
if len(gdf) > 10000:
    gdf_sample = gdf.sample(n=10000, random_state=42)  # Sample 10000 points
    print("\nData sampled to 10000 points for efficiency.")
else:
    gdf_sample = gdf
    print("\nData has 10000 or fewer points. No sampling performed.")

# --- 4.  Variogram Cloud Calculation ---
def variogram_cloud(gdf, variable):
    """
    Calculates and returns the variogram cloud data.

    Parameters:
    gdf (GeoDataFrame):  GeoDataFrame containing the data.
    variable (str): Name of the variable to analyze.

    Returns:
    pandas.DataFrame: DataFrame with columns 'distance' and 'semivariance'.
    """
    coords = np.array([(p.x, p.y) for p in gdf.geometry])
    values = gdf[variable].values
    n_points = len(coords)

    distances = []
    semivariances = []

    for i in range(n_points):
        for j in range(i + 1, n_points):
            dist = np.sqrt(np.sum((coords[i] - coords[j]) ** 2))
            semivariance = 0.5 * (values[i] - values[j]) ** 2
            distances.append(dist)
            semivariances.append(semivariance)
    return pd.DataFrame({'distance': distances, 'semivariance': semivariances})

# Calculate variogram cloud for 'avg_d_speed_mbps'
variogram_df = variogram_cloud(gdf_sample, 'avg_u_speed_mbps')

# --- 5. Plot the Variogram Cloud ---
plt.figure(figsize=(10, 6))
plt.scatter(variogram_df['distance'], variogram_df['semivariance'], alpha=0.5)
plt.title('Variogram Cloud for avg_u_speed_mbps (Sample of 10000)')
plt.xlabel('Distance (meters)')
plt.ylabel('Semivariance')
plt.grid(True)
plt.show()

# --- 6. Interpretation of Variogram Cloud for Outliers ---
print("\nInterpretation of Variogram Cloud for Outliers:")
print("The variogram cloud displays the relationship between the difference in data values and the distance between locations.")
print("Points that are far from the main cloud, especially those with high semivariance values, may indicate potential spatial outliers.")
print("  - Points with large semivariance and large distance:  These points represent pairs of locations that are far apart and have very different values. They could be influential outliers.")
print("  - Points with large semivariance and small distance: These points represent locations that are close together but have very different values.  They are strong candidates for spatial outliers.")
print("In this plot, look for points that stand out from the general pattern.  These points warrant further investigation to determine if they are true outliers or simply areas of high variability.")
