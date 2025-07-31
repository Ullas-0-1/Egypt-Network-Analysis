import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
import geopandas as gpd
from shapely.geometry import Point

# -------------------------------
# 1. Load and Prepare Data
# -------------------------------
# Load your data
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# Convert to GeoDataFrame (using first 1000 points for testing - remove this limit for full analysis)
df = df.iloc[:5000]  # Remove this line after testing
geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=3857)

# Extract coordinates and values
coords = np.array([(pt.x, pt.y) for pt in gdf.geometry])
values = gdf['avg_u_speed_mbps'].values

# -------------------------------
# 2. Optimized Variogram Calculation
# -------------------------------
def calculate_variogram(coords, values, max_dist=None, n_bins=20):
    """Calculate empirical variogram using upper triangle only"""
    # Calculate pairwise distances (condensed form)
    dist_condensed = pdist(coords)
    
    # Calculate squared differences
    diff_condensed = pdist(values.reshape(-1,1), lambda u, v: ((u-v)**2)/2)
    
    # Filter out zero distances
    mask = dist_condensed > 0
    dist_condensed = dist_condensed[mask]
    diff_condensed = diff_condensed[mask]
    
    # Determine max distance if not provided
    if max_dist is None:
        max_dist = np.percentile(dist_condensed, 95)
    
    # Bin the distances
    bins = np.linspace(0, max_dist, n_bins+1)
    bin_indices = np.digitize(dist_condensed, bins)
    
    # Calculate mean semivariance per bin
    variogram = []
    semivariances = []
    counts = []
    
    for i in range(1, len(bins)):
        in_bin = bin_indices == i
        if np.any(in_bin):
            variogram.append(bins[i])
            semivariances.append(np.mean(diff_condensed[in_bin]))
            counts.append(np.sum(in_bin))
    
    return np.array(variogram), np.array(semivariances), np.array(counts)

# Compute variogram (using max_dist=200km in meters)
max_dist = 200000
variogram_x, semivariance, counts = calculate_variogram(coords, values, max_dist=max_dist)

# -------------------------------
# 3. Plot Variogram
# -------------------------------
plt.figure(figsize=(12, 6))

# Empirical variogram
plt.scatter(variogram_x/1000, semivariance, s=50, c='darkred', 
           label=f'Empirical (n={len(coords)} points)')

# Add trend line
if len(variogram_x) > 3:
    plt.plot(variogram_x/1000, semivariance, '--', color='black', alpha=0.5)

# Formatting
plt.title('Variogram of Average Upload Speed (Mbps)', fontsize=14)
plt.xlabel('Distance (km)', fontsize=12)
plt.ylabel('Semivariance', fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('variogram_upload_speed.png', dpi=300, bbox_inches='tight')

# Distance markers every 50 km
for d in np.arange(0, max_dist/1000+50, 50):
    plt.axvline(d, color='gray', linestyle=':', alpha=0.2)

plt.tight_layout()
plt.show()

# -------------------------------
# 4. Interpretation
# -------------------------------
print("\nVariogram Statistics:")
print(f"- Maximum distance analyzed: {max_dist/1000:.1f} km")
print(f"- Number of distance bins: {len(variogram_x)}")
print(f"- Maximum semivariance: {semivariance.max():.2f}")
print("\nStationarity indicators:")
print("- Variogram reaches sill:", "Yes" if semivariance[-1] < semivariance.max()*1.1 else "Possibly not")
print("- Initial nugget effect:", f"{semivariance[0]:.2f}")



# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial.distance import pdist
# import geopandas as gpd
# from shapely.geometry import Point

# # Load data
# df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
# df_sampled = df.sample(n=500, random_state=42).reset_index(drop=True)
# geometry = [Point(xy) for xy in zip(df['centroid_lon'], df['centroid_lat'])]
# gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=3857)
# coords = np.array([(pt.x, pt.y) for pt in gdf.geometry])

# # Optimized variogram function
# def calculate_variogram(coords, values, max_dist=None, n_bins=20):
#     dist_condensed = pdist(coords)
#     diff_condensed = pdist(values.reshape(-1,1), lambda u, v: ((u-v)**2)/2)
#     mask = dist_condensed > 0
#     dist_condensed, diff_condensed = dist_condensed[mask], diff_condensed[mask]
#     max_dist = max_dist or np.percentile(dist_condensed, 95)
#     bins = np.linspace(0, max_dist, n_bins+1)
#     bin_indices = np.digitize(dist_condensed, bins)
#     return (
#         bins[1:],
#         [np.mean(diff_condensed[bin_indices==i]) for i in range(1,len(bins))],
#         [np.sum(bin_indices==i) for i in range(1,len(bins))]
#     )

# # Plot dual variograms
# plt.figure(figsize=(14,6))
# for i, (var, color) in enumerate(zip(
#     ['avg_d_speed_mbps', 'avg_u_speed_mbps'],
#     ['darkred', 'navy']
# )):
#     v_x, semivar, _ = calculate_variogram(coords, gdf[var].values, max_dist=200000)
#     plt.scatter(v_x/1000, semivar, s=50, color=color, label=f'{var} (n={len(coords)})')
#     plt.plot(v_x/1000, semivar, '--', color=color, alpha=0.3)

# plt.title('Dual Variograms: Download vs Upload Speeds', fontsize=14)
# plt.xlabel('Distance (km)')
# plt.ylabel('Semivariance')
# plt.legend()
# plt.grid(alpha=0.3)
# plt.show()
# plt.savefig('dual_variograms.png', dpi=300, bbox_inches='tight')