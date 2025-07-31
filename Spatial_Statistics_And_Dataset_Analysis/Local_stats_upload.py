import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from libpysal.weights import KNN
from esda import Moran_Local, Geary_Local, G_Local
import matplotlib.pyplot as plt

# Load and prepare GeoDataFrame
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)

# Compute spatial weights
w = KNN.from_dataframe(gdf, k=8)
w.transform = 'R'

# For all variables, store local values for each row
for var in ['avg_u_speed_mbps', 'avg_d_speed_mbps', 'avg_lat_ms']:
    x = gdf[var].astype(float).values
    gdf[f'{var}_local_moran'] = Moran_Local(x, w).Is
    gdf[f'{var}_local_geary'] = Geary_Local(connectivity=w).fit(x).localG
    gdf[f'{var}_local_getis'] = G_Local(x, w).Gs

# Now group by city and calculate mean of each local stat per city
city_stats = gdf.groupby('city').agg({
    'avg_u_speed_mbps_local_moran': 'mean',
    'avg_d_speed_mbps_local_moran': 'mean',
    'avg_lat_ms_local_moran': 'mean',
    'avg_u_speed_mbps_local_geary': 'mean',
    'avg_d_speed_mbps_local_geary': 'mean',
    'avg_lat_ms_local_geary': 'mean',
    'avg_u_speed_mbps_local_getis': 'mean',
    'avg_d_speed_mbps_local_getis': 'mean',
    'avg_lat_ms_local_getis': 'mean',
}).reset_index()

# -------------------------------
# Get Top 10 Cities for Each Metric

def top10(df, column, ascending=False):
    return df[['city', column]].sort_values(by=column, ascending=ascending).head(10)

top10_moran = top10(city_stats, 'avg_u_speed_mbps_local_moran', ascending=False)
top10_geary = top10(city_stats, 'avg_u_speed_mbps_local_geary', ascending=True)  # Low is good
top10_getis = top10(city_stats, 'avg_u_speed_mbps_local_getis', ascending=False)

# -------------------------------
# Plotting the top 10 cities for each

fig, axs = plt.subplots(1, 3, figsize=(18, 5))

axs[0].barh(top10_moran['city'], top10_moran['avg_u_speed_mbps_local_moran'], color='seagreen')
axs[0].set_title("Top 10 Cities - Local Moran's I ")
axs[0].invert_yaxis()

axs[1].barh(top10_geary['city'], top10_geary['avg_u_speed_mbps_local_geary'], color='tomato')
axs[1].set_title("Top 10 Cities - Local Geary's C ")
axs[1].invert_yaxis()

axs[2].barh(top10_getis['city'], top10_getis['avg_u_speed_mbps_local_getis'], color='steelblue')
axs[2].set_title("Top 10 Cities - Local Getis-Ord G* ")
axs[2].invert_yaxis()

plt.tight_layout()
plt.savefig("top_10_cities_local_stats_upload.png", dpi=300)
plt.show()

for i, row in top10_moran.iterrows():
    print(f"City: {row['city']}, Local Moran's I: {row['avg_u_speed_mbps_local_moran']}")

print("-" * 50)
for i, row in top10_geary.iterrows():
    print(f"City: {row['city']}, Local Geary's C: {row['avg_u_speed_mbps_local_geary']}")
print("-" * 50)
for i, row in top10_getis.iterrows():
    print(f"City: {row['city']}, Local Getis-Ord G*: {row['avg_u_speed_mbps_local_getis']}")
print("-" * 50)
