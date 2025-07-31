# import geopandas as gpd
# import pandas as pd
# import matplotlib.pyplot as plt
# import contextily as ctx
# from shapely.geometry import Point
# from libpysal.weights import KNN
# from esda.moran import Moran
# from esda.geary import Geary

# # Load data
# df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
# geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
# gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# # Reproject to Web Mercator
# gdf_web = gdf.to_crs(epsg=3857)

# # Build spatial weights using K-Nearest Neighbors (k=8)
# w = KNN.from_dataframe(gdf_web, k=6)
# w.transform = 'R'  # row-standardized weights

# # List of variables to analyze
# variables = ['avg_u_speed_mbps', 'avg_d_speed_mbps', 'avg_lat_ms']

# # Loop through variables
# for var in variables:
#     print(f"\n=== {var} ===")
    
#     # Moran's I
#     moran = Moran(gdf_web[var], w)
#     print(f"Moran's I: {moran.I:.4f}, p-value: {moran.p_sim:.4f}")
    
#     # Geary's C
#     geary = Geary(gdf_web[var], w)
#     print(f"Geary's C: {geary.C:.4f}, p-value: {geary.p_sim:.4f}")
    
#     # Plot the variable with contextily basemap
#     fig, ax = plt.subplots(figsize=(13, 11))
#     gdf_web.plot(ax=ax, column=var, cmap='viridis', markersize=10, legend=True, alpha=0.6)
#     ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
#     ax.set_title(f"{var} (for Spatial Autocorrelation)", fontsize=14)
#     ax.set_axis_off()
#     plt.tight_layout()
#     plt.show()

    
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
from libpysal.weights import KNN
from esda.moran import Moran
from esda.geary import Geary

# 1. Load your data
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
gdf_web = gdf.to_crs(epsg=3857)

# 2. Create spatial weights
w = KNN.from_dataframe(gdf_web, k=8)
w.transform = 'R'

# 3. Compute Global Moran’s I and Geary’s C
variables = ['avg_u_speed_mbps', 'avg_d_speed_mbps', 'avg_lat_ms']
morans = []
gearys = []

for var in variables:
    moran = Moran(gdf_web[var], w)
    geary = Geary(gdf_web[var], w)
    morans.append(moran.I)
    gearys.append(geary.C)

# 4. Plot bar charts
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# Moran's I
ax[0].bar(variables, morans, color='teal')
ax[0].set_title("Global Moran's I")
ax[0].set_ylim(0, 1)
for i, v in enumerate(morans):
    ax[0].text(i, v + 0.02, f"{v:.2f}", ha='center', fontsize=12)

# Geary's C
ax[1].bar(variables, gearys, color='purple')
ax[1].set_title("Global Geary's C")
ax[1].set_ylim(0, 1.2)
for i, v in enumerate(gearys):
    ax[1].text(i, v + 0.02, f"{v:.2f}", ha='center', fontsize=12)

plt.tight_layout()
plt.savefig("global_morans_gearys.png", dpi=300)
plt.show()

# # 5. Optional: Plot the data itself with contextily map
# fig, ax = plt.subplots(figsize=(12, 10))
# gdf_web.plot(ax=ax, column='avg_u_speed_mbps', cmap='viridis', markersize=4, alpha=0.6, legend=True)
# ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
# ax.set_title("Upload Speed Distribution with Basemap")
# plt.axis('off')
# plt.show()
    


#the current code has global gearys and mornos plots ,, alsong with that it has the distributions of all thee which is just for assumption all are similar--
#should shouw that using clustering we , were able to find clusters and the plot was looking better
