import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import great_circle
from tqdm import tqdm

# Load dataset and sample 5000 rows
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")
df_sampled = df.sample(n=5000, random_state=42).reset_index(drop=True)

# Extract required columns
coords = list(zip(df_sampled['centroid_lat'], df_sampled['centroid_lon']))
download = df_sampled['avg_d_speed_mbps'].values
upload = df_sampled['avg_u_speed_mbps'].values

# Function to compute Moran's I
def morans_i(values, weights):
    n = len(values)
    mean_val = np.mean(values)
    num = 0
    for i in range(n):
        for j in range(n):
            num += weights[i, j] * (values[i] - mean_val) * (values[j] - mean_val)
    denom = np.sum((values - mean_val) ** 2)
    W = np.sum(weights)
    if W == 0 or denom == 0:
        return np.nan
    return (n / W) * (num / denom)

# Compute pairwise distances in kilometers using Haversine
print("Calculating distances...")
n = len(coords)
dist_matrix = np.zeros((n, n))
for i in tqdm(range(n)):
    for j in range(i+1, n):
        dist = great_circle(coords[i], coords[j]).km
        dist_matrix[i, j] = dist
        dist_matrix[j, i] = dist  # symmetric

# Define distance bins
bin_edges = np.linspace(0, np.max(dist_matrix), 20)
bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
morans_d = []
morans_u = []
counts_per_bin = []

# For each bin, create a weight matrix and compute Moran’s I
for k in range(len(bin_edges) - 1):
    lower = bin_edges[k]
    upper = bin_edges[k+1]
    W_bin = np.where((dist_matrix >= lower) & (dist_matrix < upper), 1, 0)
    count = np.sum(W_bin)
    if count == 0:
        morans_d.append(np.nan)
        morans_u.append(np.nan)
        counts_per_bin.append(0)
        continue
    morans_d.append(morans_i(download, W_bin))
    morans_u.append(morans_i(upload, W_bin))
    counts_per_bin.append(count)

# --- PLOTTING ---
fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                       gridspec_kw={'height_ratios': [3, 1]})

# Correlogram
ax[0].plot(bin_centers, morans_d, label='Download Speed Moran\'s I', color='blue', marker='o')
ax[0].plot(bin_centers, morans_u, label='Upload Speed Moran\'s I', color='green', marker='s')
ax[0].axhline(0, linestyle='--', color='red')
ax[0].set_ylabel("Moran's I")
ax[0].set_title("Spatial Correlogram of Upload & Download Speeds")
ax[0].legend()
ax[0].grid(True)

# Histogram of counts
ax[1].bar(bin_centers, counts_per_bin, width=np.diff(bin_edges), align='center', color='gray', edgecolor='black')
ax[1].set_xlabel("Distance between point pairs (km)")
ax[1].set_ylabel("Pair Count per Bin")
ax[1].set_title("Number of Point Pairs in Each Distance Bin")
ax[1].grid(True)

plt.tight_layout()
plt.savefig("correlogram.png", dpi=300)
plt.show()
