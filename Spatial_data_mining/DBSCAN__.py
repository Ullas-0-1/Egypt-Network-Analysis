import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx

# Load dataset
df = pd.read_csv('/Users/ullas/Desktop/STDA-PROJECT/network performance.csv')

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['centroid_lon'], df['centroid_lat']), crs='EPSG:4326')
gdf = gdf.to_crs(epsg=3857)

# Extract projected coordinates for DBSCAN
xy = np.array([[geom.x, geom.y] for geom in gdf.geometry])

# DBSCAN clustering
dbscan = DBSCAN(eps=10000, min_samples=3)
gdf['cluster'] = dbscan.fit_predict(xy)

# Filter out noise points (label = -1)
gdf_filtered = gdf[gdf['cluster'] != -1].copy()

# Summarize cluster properties
cluster_summary = gdf_filtered.groupby('cluster').agg({
    'avg_d_speed_mbps': ['mean', 'min', 'max'],
    'avg_u_speed_mbps': ['mean', 'min', 'max'],
    'geometry': 'count'
}).rename(columns={'geometry': 'points_in_cluster'})

print("\n🔍 Cluster Summary:\n")
print(cluster_summary)

# Plotting

ax = gdf_filtered.plot(column='cluster', cmap='tab20', legend=True, alpha=0.8, markersize=60)

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf_filtered.crs.to_string())

# Label each cluster with its number
for cluster_id, cluster_data in gdf_filtered.groupby('cluster'):
    centroid = cluster_data.geometry.unary_union.centroid
    plt.text(centroid.x, centroid.y, str(cluster_id), fontsize=12, fontweight='bold', color='black')

plt.title("DBSCAN Clusters on Egypt Map", fontsize=15)
plt.axis('off')
plt.tight_layout()
plt.savefig("dbscan_clusters_egypt.png", dpi=300)
plt.show()
