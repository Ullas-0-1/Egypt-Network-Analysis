import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from shapely.geometry import Point

# --- Load your dataset ---
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# --- Select spatial + speed features ---
features = df[['centroid_lat', 'centroid_lon', 'avg_d_speed_mbps', 'avg_u_speed_mbps','tests']]

# --- Normalize the features ---
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# --- Apply DBSCAN ---
dbscan = DBSCAN(eps=1.5, min_samples=5)  # You can tune these parameters
labels = dbscan.fit_predict(scaled_features)
df['cluster'] = labels

# --- Print cluster info (excluding noise) ---
num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print("Number of clusters found (excluding noise):", num_clusters)
print("Noise points:", list(labels).count(-1))

if num_clusters > 0:  # Only proceed if there are actual clusters
    # --- Group by cluster and print statistics ---
    cluster_summary = df[df['cluster'] != -1].groupby('cluster')[['avg_d_speed_mbps', 'avg_u_speed_mbps','tests']].mean()
    print("\nAverage speeds by cluster:\n", cluster_summary)

    # --- Convert to GeoDataFrame for plotting (excluding noise) ---
    geometry = [Point(xy) for xy in zip(df[df['cluster'] != -1]['centroid_lon'], df[df['cluster'] != -1]['centroid_lat'])]
    gdf = gpd.GeoDataFrame(df[df['cluster'] != -1], geometry=geometry, crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)  # For compatibility with web map tiles

    # --- Plot (excluding noise) ---
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf.plot(ax=ax, column='cluster', categorical=True, legend=True, cmap='tab20', markersize=10, alpha=0.8)

    # --- Optional: Add Egypt basemap using contextily ---
    try:
        import contextily as ctx
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    except ImportError:
        print("Contextily not installed. Map will be shown without basemap.")

    ax.set_title("DBSCAN Clustering ", fontsize=15)
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig("dbscan_clusters_all.png", dpi=300)
    plt.show()
else:
    print("No clusters found (excluding noise points).  Adjust DBSCAN parameters.")
