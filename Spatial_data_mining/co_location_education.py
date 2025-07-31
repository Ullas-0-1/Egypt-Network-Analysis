import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point

###add fake values to the test

# --------------------------
# Load hospital shapefile
# --------------------------
hospitals = gpd.read_file("/Users/ullas/Desktop/STDA-PROJECT/hotosm_egy_education_facilities_points_shp/hotosm_egy_education_facilities_points_shp.shp")
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
median_speed = gdf_network['avg_u_speed_mbps'].quantile(0.55)
high_speed = gdf_network[gdf_network['avg_u_speed_mbps'] >= median_speed]

# --------------------------
# Create buffer around hospitals (e.g., 2000 meters)
# --------------------------
hospital_buffer = hospitals.copy()
hospital_buffer['geometry'] = hospital_buffer.buffer(1500)

# --------------------------
# Spatial join: keep only high-speed points that intersect hospital buffer
# --------------------------
colocated = gpd.sjoin(high_speed, hospital_buffer, how="inner", predicate='intersects')

# --------------------------
# Plot colocated high-speed points and hospitals
# --------------------------
fig, ax = plt.subplots(figsize=(10, 10))

# Plot hospitals (red)
hospitals.plot(ax=ax, color='red', markersize=30, label='Largely Populated Places', alpha=0.5)

# Plot colocated high-speed points (green)
colocated.plot(ax=ax, color='green', markersize=20, label='High Speed Colocated Points', alpha=0.7)

# Add basemap
# ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf_network.crs.to_string())

# Styling
ax.set_title("High Upload Speed Points with largely populated places", fontsize=15)
ax.axis('off')
ax.legend()

plt.tight_layout()
plt.show()

# Optional: print how many colocated points found
print(f"Total high-speed points: {len(high_speed)}")
print(f"Colocated with largely populated places (within 2km): {len(colocated)}")



'''

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
from matplotlib.lines import Line2D

# --------------------------
# Load data
# --------------------------
# Load education facilities (hospitals)
hospitals = gpd.read_file("/Users/ullas/Desktop/STDA-PROJECT/hotosm_egy_education_facilities_points_shp/hotosm_egy_education_facilities_points_shp.shp")
hospitals['longitude'] = hospitals.geometry.x
hospitals['latitude'] = hospitals.geometry.y

# Load network performance data
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
df = df.dropna(subset=['centroid_lon', 'centroid_lat', 'avg_u_speed_mbps', 'avg_d_speed_mbps'])
gdf_network = gpd.GeoDataFrame(df, 
                             geometry=gpd.points_from_xy(df['centroid_lon'], df['centroid_lat']),
                             crs="EPSG:4326")

# --------------------------
# Project to metric CRS (Web Mercator)
# --------------------------
gdf_network = gdf_network.to_crs(epsg=3857)
hospitals = hospitals.to_crs(epsg=3857)

# --------------------------
# Define thresholds and buffers
# --------------------------
# Speed thresholds (25th percentile - adjust as needed)
upload_thresh = gdf_network['avg_u_speed_mbps'].quantile(0.25)
download_thresh = gdf_network['avg_d_speed_mbps'].quantile(0.25)

# Create hospital buffers (1.5km)
hospital_buffer = hospitals.copy()
hospital_buffer['geometry'] = hospitals.buffer(1500)

# --------------------------
# Categorize all network points
# --------------------------
def categorize_point(row):
    near_hospital = any(row.geometry.intersects(buffer) for buffer in hospital_buffer['geometry'])
    high_speed = (row['avg_u_speed_mbps'] >= upload_thresh) and (row['avg_d_speed_mbps'] >= download_thresh)
    
    if near_hospital:
        return 'Near LPP, High Speed' if high_speed else 'Near LPP, Low Speed'
    return 'Far from LPP'

gdf_network['category'] = gdf_network.apply(categorize_point, axis=1)

# --------------------------
# Generate statistics
# --------------------------
stats = gdf_network['category'].value_counts()
total_points = len(gdf_network)
near_high_speed = stats.get('Near LPP, High Speed', 0)
near_low_speed = stats.get('Near LPP, Low Speed', 0)
far_points = stats.get('Far from LPP', 0)

# --------------------------
# Enhanced Visualization
# --------------------------
fig, ax = plt.subplots(figsize=(12, 10))

# Color mapping
color_map = {
    'Near LPP, High Speed': 'limegreen',
    'Near LPP, Low Speed': 'orange',
    'Far from LPP': 'lightgray'
}

# Plot all network points by category
for category, color in color_map.items():
    subset = gdf_network[gdf_network['category'] == category]
    subset.plot(ax=ax, color=color, markersize=8, alpha=0.7, label=category)

# Plot hospitals (education facilities)
hospitals.plot(ax=ax, color='red', markersize=50, marker='*', 
              edgecolor='k', linewidth=0.5, label='Largely Populated Places')

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf_network.crs.to_string(), alpha=0.9)

# Create enhanced legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
           markersize=10, label=f"{category} ({stats.get(category, 0)})", 
           markeredgecolor='k') for category, color in color_map.items()
]
legend_elements.append(
    Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
           markersize=15, label=f'Largely Populated Places ({len(hospitals)})', 
           markeredgecolor='k')
)

ax.legend(handles=legend_elements, loc='upper right', title="Categories (Counts)")

# Add statistics annotation
stats_text = (
    f"Speed Thresholds (25th percentile):\n"
    f"Upload ≥ {upload_thresh:.2f} Mbps | Download ≥ {download_thresh:.2f} Mbps\n"
    f"Buffer Distance: 1.5km around LPPs\n\n"
    f"Near LPP, High Speed: {near_high_speed} ({near_high_speed/total_points:.1%})\n"
    f"Near LPP, Low Speed: {near_low_speed} ({near_low_speed/total_points:.1%})\n"
    f"Far from LPP: {far_points} ({far_points/total_points:.1%})"
)
ax.annotate(stats_text, xy=(0.02, 0.15), xycoords='axes fraction', 
           bbox=dict(boxstyle="round", alpha=0.8, facecolor='white'))

ax.set_title("Network Speed vs. Proximity to Largely Populated Places (LPPs)", fontsize=14)
ax.set_axis_off()
plt.tight_layout()

# Save and show
plt.savefig('network_lpp_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Print detailed statistics
print("\n=== Detailed Statistics ===")
print(f"Total network points analyzed: {total_points}")
print(f"Total Largely Populated Places: {len(hospitals)}")
print(f"\nSpeed Thresholds (25th percentile):")
print(f"Upload ≥ {upload_thresh:.2f} Mbps | Download ≥ {download_thresh:.2f} Mbps")
print("\nPoint Distribution:")
print(f"1. Near LPP with high speed: {near_high_speed} points ({near_high_speed/total_points:.1%})")
print(f"2. Near LPP with low speed: {near_low_speed} points ({near_low_speed/total_points:.1%})")
print(f"3. Far from LPP: {far_points} points ({far_points/total_points:.1%})")
print(f"\nColocation Rate: {(near_high_speed + near_low_speed)/total_points:.1%} of points near LPPs")
'''
