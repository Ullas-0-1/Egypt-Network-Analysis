# import pandas as pd
# import geopandas as gpd
# from shapely.geometry import Point
# from sklearn.preprocessing import StandardScaler
# import numpy as np
# from mgwr.gwr import GWR
# from mgwr.sel_bw import Sel_BW
# import matplotlib.pyplot as plt

# # ------------------------------
# # Load and preprocess your data
# # ------------------------------
# df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# # Drop rows with missing values
# df = df.dropna(subset=['centroid_lat', 'centroid_lon', 'avg_u_speed_mbps', 
#                        'avg_d_kbps', 'avg_u_kbps', 'avg_lat_ms', 'tests', 'devices'])

# # Create geometry column
# geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
# gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# # Project to metric CRS (meters)
# gdf = gdf.to_crs(epsg=3857)

# # ------------------------------
# # Prepare Variables for GWR
# # ------------------------------

# # Target: upload speed (Mbps)
# y = gdf['avg_u_speed_mbps'].values.reshape(-1, 1)

# # Predictors
# X = gdf[[ 'avg_d_speed_mbps', 'avg_lat_ms','tests', 'devices']].values

# # Standardize predictors and target
# scaler_X = StandardScaler()
# scaler_y = StandardScaler()
# X_std = scaler_X.fit_transform(X)
# y_std = scaler_y.fit_transform(y)

# # Coordinates for spatial modeling
# coords = np.column_stack((gdf.geometry.x, gdf.geometry.y))

# # ------------------------------
# # Select optimal bandwidth
# # ------------------------------
# selector = Sel_BW(coords, y_std, X_std, fixed=False, spherical=False)
# bw = selector.search()
# print("Selected Bandwidth:", bw)

# # ------------------------------
# # Apply observation weights PROPERLY
# # ------------------------------
# # The correct way to incorporate weights is to pre-multiply them into the variables
# weights = np.sqrt(gdf['tests'].values)  # Using sqrt for more balanced weighting
# y_weighted = y_std * weights.reshape(-1, 1)
# X_weighted = X_std * weights.reshape(-1, 1)

# # ------------------------------
# # Fit the GWR model
# # ------------------------------
# gwr_model = GWR(coords, y_weighted, X_weighted, bw, fixed=False, spherical=False)
# gwr_results = gwr_model.fit()

# # ------------------------------
# # Store and visualize results
# # ------------------------------
# for i, var in enumerate([ 'avg_u_speed_mbps', 'avg_lat_ms','tests', 'devices']):
#     gdf[f'gwr_coef_{var}'] = gwr_results.params[:, i]

# # Plot coefficients
# fig, ax = plt.subplots(1, 3, figsize=(20, 6))
# for i, var in enumerate([ 'avg_u_speed_mbps', 'avg_lat_ms','tests', 'devices']):
#     gdf.plot(column=f'gwr_coef_{var}', ax=ax[i], legend=True, cmap='coolwarm',
#             vmin=gdf[f'gwr_coef_{var}'].quantile(0.05),
#             vmax=gdf[f'gwr_coef_{var}'].quantile(0.95))
#     ax[i].set_title(f'Local Coefficient: {var}')
#     ax[i].axis('off')

# plt.tight_layout()
# plt.show()

# # ------------------------------
# # Model diagnostics
# # ------------------------------
# print("\nModel Summary:")
# print(gwr_results.summary())

# print("\nGoodness of Fit:")
# print(f"AICc: {gwr_results.aicc:.2f}")
# print(f"R²: {gwr_results.R2:.3f}")
# print(f"Adjusted R²: {gwr_results.adj_R2:.3f}")

# # Calculate weighted residuals
# gdf['residuals'] = (y_std.flatten() - gwr_results.predictions.flatten()) / weights


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler
import numpy as np
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
import matplotlib.pyplot as plt
import contextily as ctx

# ------------------------------
# Load and preprocess your data
# ------------------------------
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# Drop rows with missing values
df = df.dropna(subset=['centroid_lat', 'centroid_lon', 'avg_u_speed_mbps', 
                       'avg_d_kbps', 'avg_u_kbps', 'avg_lat_ms', 'tests', 'devices'])

# Create geometry column
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Project to metric CRS (Web Mercator for basemap compatibility)
gdf = gdf.to_crs(epsg=3857)

# ------------------------------
# Prepare Variables for GWR
# ------------------------------

# Target: upload speed (Mbps)
y = gdf['avg_u_speed_mbps'].values.reshape(-1, 1)

# Predictors
X = gdf[['avg_d_speed_mbps', 'avg_lat_ms', 'tests', 'devices']].values

# Standardize predictors and target
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_std = scaler_X.fit_transform(X)
y_std = scaler_y.fit_transform(y)

# Coordinates for spatial modeling
coords = np.column_stack((gdf.geometry.x, gdf.geometry.y))

# ------------------------------
# Select optimal bandwidth
# ------------------------------
selector = Sel_BW(coords, y_std, X_std, fixed=False, spherical=False)
bw = selector.search()
print("Selected Bandwidth:", bw)

# ------------------------------
# Apply observation weights
# ------------------------------
weights = np.sqrt(gdf['tests'].values)  # Square root for balanced weighting
y_weighted = y_std * weights.reshape(-1, 1)
X_weighted = X_std * weights.reshape(-1, 1)

# ------------------------------
# Fit the GWR model
# ------------------------------
gwr_model = GWR(coords, y_weighted, X_weighted, bw, fixed=False, spherical=False)
gwr_results = gwr_model.fit()

# ------------------------------
# Store results
# ------------------------------
predictors = ['avg_d_speed_mbps', 'avg_lat_ms', 'tests', 'devices']
for i, var in enumerate(predictors):
    gdf[f'gwr_coef_{var}'] = gwr_results.params[:, i]

# ------------------------------
# Plot coefficients with Egypt basemap
# ------------------------------
fig, axs = plt.subplots(2, 2, figsize=(20, 16))
axs = axs.flatten()

for i, var in enumerate(predictors):
    # Plot coefficients
    gdf.plot(column=f'gwr_coef_{var}', 
             ax=axs[i], 
             cmap='coolwarm',
             legend=True,
             alpha=0.7,
             markersize=10,
             vmin=gdf[f'gwr_coef_{var}'].quantile(0.05),
             vmax=gdf[f'gwr_coef_{var}'].quantile(0.95))
    
    # Add Egypt basemap
    ctx.add_basemap(axs[i], 
                   source=ctx.providers.CartoDB.Positron,
                   attribution_size=6)
    
    # Styling
    axs[i].set_title(f'Local Coefficient: {var}', fontsize=14)
    axs[i].axis('off')

plt.tight_layout()
plt.savefig('gwr_coefficients_egypt.png', dpi=300, bbox_inches='tight')
plt.show()

# ------------------------------
# Model diagnostics
# ------------------------------
print("\nModel Summary:")
print(gwr_results.summary())

print("\nGoodness of Fit:")
print(f"AICc: {gwr_results.aicc:.2f} (Lower = Better)")
print(f"R²: {gwr_results.R2:.3f}")
print(f"Adjusted R²: {gwr_results.adj_R2:.3f}")

# Residual analysis
gdf['residuals'] = (y_std.flatten() - gwr_results.predictions.flatten()) / weights

# Plot residuals with basemap
fig, ax = plt.subplots(figsize=(12, 10))
gdf.plot(column='residuals', 
         ax=ax, 
         cmap='RdYlBu', 
         legend=True,
         alpha=0.7,
         markersize=10,
         vmin=-3, 
         vmax=3)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
ax.set_title("Standardized Residuals", fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig('gwr_residuals_egypt.png', dpi=300)
plt.show()


##just talk about the ols model -- adn tell as spatial heterogenity exists clearly this one worked bettr and is better