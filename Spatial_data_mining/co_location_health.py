import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point

###add fake values to the test

# --------------------------
# Load hospital shapefile
# --------------------------
hospitals = gpd.read_file("/Users/ullas/Desktop/STDA-PROJECT/hotosm_egy_health_facilities_points_shp/hotosm_egy_health_facilities_points_shp.shp")
hospitals['longitude'] = hospitals.geometry.x
hospitals['latitude'] = hospitals.geometry.y

# --------------------------
# Load network performance CSV
# --------------------------
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
df = df.dropna(subset=['centroid_lon', 'centroid_lat', 'avg_u_speed_mbps'])
gdf_network = gpd.GeoDataFrame(df, 
                               geometry=gpd.points_from_xy(df['centroid_lon'], df['centroid_lat']),
                               crs="EPSG:4326")

# --------------------------
# Project to metric CRS for distance calculation (meters)
# --------------------------
gdf_network = gdf_network.to_crs(epsg=3857)
hospitals = hospitals.to_crs(epsg=3857)

# --------------------------
# Filter network points with upload speed > median
# --------------------------
median_speed = gdf_network['avg_u_speed_mbps'].quantile(0.25)
high_speed = gdf_network[gdf_network['avg_u_speed_mbps'] >= median_speed]

# --------------------------
# Create buffer around hospitals (e.g., 2000 meters)
# --------------------------
hospital_buffer = hospitals.copy()
hospital_buffer['geometry'] = hospital_buffer.buffer(2000)

# --------------------------
# Spatial join: keep only high-speed points that intersect hospital buffer
# --------------------------
colocated = gpd.sjoin(high_speed, hospital_buffer, how="inner", predicate='intersects')

# --------------------------
# Plot colocated high-speed points and hospitals
# --------------------------
fig, ax = plt.subplots(figsize=(10, 10))

# Plot hospitals (red)
hospitals.plot(ax=ax, color='red', markersize=30, label='Hospitals')

# Plot colocated high-speed points (green)
colocated.plot(ax=ax, color='green', markersize=20, label='High Speed Colocated Points', alpha=0.7)

# Add basemap
# ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf_network.crs.to_string())

# Styling
ax.set_title("High Upload Speed Points with Nearby Hospitals", fontsize=15)
ax.axis('off')
ax.legend()

plt.tight_layout()
plt.show()

# Optional: print how many colocated points found
print(f"Total high-speed points: {len(high_speed)}")
print(f"Colocated with hospitals (within 2km): {len(colocated)}")
