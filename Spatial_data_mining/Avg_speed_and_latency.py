import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# --- 1. Get Ranges ---
print(f"Download Speed Range: {df['avg_d_speed_mbps'].min():.3f} to {df['avg_d_speed_mbps'].max():.3f} Mbps")
print(f"Upload Speed Range: {df['avg_u_speed_mbps'].min():.3f} to {df['avg_u_speed_mbps'].max():.3f} Mbps")
print(f"Latency Range: {df['avg_lat_ms'].min():.0f} to {df['avg_lat_ms'].max():.0f} ms")

# --- 2. Binning Speeds and Latency with readable string labels ---

# Define bins and corresponding labels
download_bins = [0, 5, 20, 50, 300, 800]
download_labels = ['0-5', '5-20', '20-50', '50-300', '300-800']
df['download_category'] = pd.cut(df['avg_d_speed_mbps'], bins=download_bins, labels=download_labels, include_lowest=True)

upload_bins = [0, 3, 15, 50, 200, 500]
upload_labels = ['0-3', '3-15', '15-50', '50-200', '200-500']
df['upload_category'] = pd.cut(df['avg_u_speed_mbps'], bins=upload_bins, labels=upload_labels, include_lowest=True)

latency_bins = [0, 20, 50, 500, 1000]
latency_labels = ['0-20', '20-50', '50-500', '500-1000']
df['latency_category'] = pd.cut(df['avg_lat_ms'], bins=latency_bins, labels=latency_labels, include_lowest=True)

# --- 3. Value Counts ---
print("\nDownload Speed Ranges:")
print(df['download_category'].value_counts().reindex(download_labels))

print("\nUpload Speed Ranges:")
print(df['upload_category'].value_counts().reindex(upload_labels))

print("\nLatency Ranges:")
print(df['latency_category'].value_counts().reindex(latency_labels))

# --- 4. Count Plots ---
plt.figure(figsize=(18, 4))

sns.set_palette("cool")  # Set cool color palette

plt.subplot(1, 3, 1)
sns.countplot(data=df, x='download_category', order=download_labels)
plt.title("Download Speed (Mbps)")
plt.xlabel("Speed Range (Mbps)")
plt.ylabel("Count")

plt.subplot(1, 3, 2)
sns.countplot(data=df, x='upload_category', order=upload_labels)
plt.title("Upload Speed (Mbps)")
plt.xlabel("Speed Range (Mbps)")
plt.ylabel("Count")

plt.subplot(1, 3, 3)
sns.countplot(data=df, x='latency_category', order=latency_labels)
plt.title("Latency (ms)")
plt.xlabel("Latency Range (ms)")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig('speed_latency_count_plots.png', dpi=300)
plt.show()


