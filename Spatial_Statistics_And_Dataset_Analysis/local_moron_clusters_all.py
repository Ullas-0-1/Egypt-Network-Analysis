import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from libpysal.weights import KNN
from esda import Moran_Local
import matplotlib.pyplot as plt
import contextily as ctx

# Load and convert to GeoDataFrame
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

# Add Local Moran's I results to GeoDataFrame
gdf['local_I'] = moran_local.Is
gdf['p_sim'] = moran_local.p_sim
gdf['q'] = moran_local.q

# Only keep statistically significant clusters (p < 0.05)
gdf['cluster'] = 'Not Significant'
gdf.loc[(gdf['p_sim'] < 0.05) & (gdf['q'] == 1), 'cluster'] = 'High-High'
gdf.loc[(gdf['p_sim'] < 0.05) & (gdf['q'] == 2), 'cluster'] = 'Low-High'
gdf.loc[(gdf['p_sim'] < 0.05) & (gdf['q'] == 3), 'cluster'] = 'Low-Low'
gdf.loc[(gdf['p_sim'] < 0.05) & (gdf['q'] == 4), 'cluster'] = 'High-Low'

# Define colors for clusters
cluster_colors = {
    'High-High': 'red',
    'Low-Low': 'blue',
    'Low-High': 'lightblue',
    'High-Low': 'orange',
    'Not Significant': 'lightgrey'
}
gdf['color'] = gdf['cluster'].map(cluster_colors)

# Plot the cluster map
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color=gdf['color'], markersize=20, alpha=0.8, edgecolor='black')

# Add basemap (EPSG:3857)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gdf.crs.to_string())

# Customize legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', label=key,
                          markerfacecolor=val, markersize=10) for key, val in cluster_colors.items()]
ax.legend(handles=legend_elements, title='Local Moran Clusters', loc='lower right')

ax.set_title("Local Moran's I Cluster Map (avg_u_speed_mbps)")
ax.set_axis_off()
plt.tight_layout()
plt.savefig("local_moran_clusters_all.png", dpi=300, bbox_inches='tight')
plt.show()
