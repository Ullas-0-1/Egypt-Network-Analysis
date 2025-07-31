import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
from scipy.stats import chi2_contingency

# Load hospital shapefile
hospitals = gpd.read_file("/Users/ullas/Desktop/STDA-PROJECT/hotosm_egy_populated_places_points_shp/hotosm_egy_populated_places_points_shp.shp")
hospitals = hospitals.to_crs(epsg=3857)

# Load network data
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
df = df.dropna(subset=['centroid_lon', 'centroid_lat', 'avg_u_speed_mbps'])
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['centroid_lon'], df['centroid_lat']), crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)

# Create buffer (1.5 km) around hospitals
hospital_buffer = hospitals.copy()
hospital_buffer['geometry'] = hospital_buffer.buffer(2000)

# Determine which points fall within any hospital buffer (near hospital)
gdf['near_hospital'] = gdf.geometry.apply(lambda x: hospital_buffer.contains(x).any())

# Categorize upload speed into bins
bins = [0, 5, 15, 30, 1000]
labels = ['Very Low', 'Low', 'Medium', 'High']
gdf['speed_category'] = pd.cut(gdf['avg_u_speed_mbps'], bins=bins, labels=labels, include_lowest=True)

# Plot
fig, ax = plt.subplots(figsize=(12, 10))

# Plot hospital points with different symbol
hospitals.plot(ax=ax, color='black', marker='X', markersize=50, label='Largely Populated Places (Hospitals)')

# Plot all network points with color for speed, shape for proximity
for speed in labels:
    for near in [True, False]:
        subset = gdf[(gdf['speed_category'] == speed) & (gdf['near_hospital'] == near)]
        marker = '^' if near else 'o'
        label = f"{speed} - {'Near' if near else 'Far'}"
        subset.plot(ax=ax, label=label, markersize=30, marker=marker, alpha=0.7)

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf.crs.to_string())

# Styling
ax.set_title("Upload Speed & Proximity to Hospitals", fontsize=15)
ax.axis('off')
ax.legend()
plt.tight_layout()
plt.show()

# ------------------------
# Count stats
# ------------------------
count_table = pd.crosstab(gdf['speed_category'], gdf['near_hospital'])
print("Counts of Points by Speed Category and Proximity:")
print(count_table)

# ------------------------
# Chi-square test
# ------------------------
chi2, p, dof, expected = chi2_contingency(count_table)
print("\nChi-square Test of Independence:")
print(f"Chi2 Statistic = {chi2:.2f}")
print(f"Degrees of Freedom = {dof}")
print(f"P-Value = {p:.4f}")

if p < 0.05:
    print("✅ Significant association between speed and hospital proximity.")
else:
    print("❌ No significant association between speed and hospital proximity.")
