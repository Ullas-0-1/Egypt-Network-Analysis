import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from libpysal.weights import KNN
from esda import Moran_Local
import matplotlib.pyplot as plt
import contextily as ctx

# Load CSV and create GeoDataFrame
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)

# Compute spatial weights
w = KNN.from_dataframe(gdf, k=8)
w.transform = 'R'

# Compute Local Moran's I for avg download speed
x = gdf['avg_u_speed_mbps'].values
moran_local = Moran_Local(x, w)

# Add results to GeoDataFrame
gdf['local_I'] = moran_local.Is
gdf['p_sim'] = moran_local.p_sim
gdf['q'] = moran_local.q

# Keep only statistically significant points (p < 0.05)
sig_gdf = gdf[gdf['p_sim'] < 0.05].copy()

# Assign cluster types based on quadrant
cluster_map = {
    1: 'High-High',
    2: 'Low-High',
    3: 'Low-Low',
    4: 'High-Low'
}
sig_gdf['cluster'] = sig_gdf['q'].map(cluster_map)

# Assign colors to cluster types
cluster_colors = {
    'High-High': 'red',
    'Low-Low': 'blue',
    'Low-High': 'lightblue',
    'High-Low': 'orange',
}
sig_gdf['color'] = sig_gdf['cluster'].map(cluster_colors)

# Plot only significant clusters
fig, ax = plt.subplots(figsize=(10, 10))
sig_gdf.plot(ax=ax, color=sig_gdf['color'], markersize=20, alpha=0.8, edgecolor='black')

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=sig_gdf.crs.to_string())

# Add legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', label=key,
                          markerfacecolor=val, markersize=10) for key, val in cluster_colors.items()]
ax.legend(handles=legend_elements, title='Significant Local Moran Clusters', loc='lower right')

ax.set_title("Significant Local Moran's I Clusters (avg_u_speed_mbps)")
ax.set_axis_off()
plt.tight_layout()
plt.savefig("local_moran_clusters_significant.png", dpi=300, bbox_inches='tight')
plt.show()
