import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('/Users/ullas/Desktop/STDA-PROJECT/network performance.csv')  




# --- 2. Average Speed by City ---
city_group = df.groupby('city').agg({
    'avg_d_speed_mbps': 'mean',
    'avg_u_speed_mbps': 'mean',
    'avg_lat_ms': 'mean'
}).reset_index()

# Sort by avg download speed for clarity
city_group_sorted = city_group.sort_values(by='avg_d_speed_mbps', ascending=False)

# Plot
plt.figure(figsize=(14, 6))
sns.barplot(data=city_group_sorted.head(20), x='city', y='avg_d_speed_mbps', palette='mako')
plt.title("Top 20 Cities by Average Download Speed")
plt.xticks(rotation=45)
plt.ylabel("Download Speed (Mbps)")
plt.xlabel("City")
plt.tight_layout()
plt.savefig('top_20_cities_download_speed.png', dpi=300)
plt.show()


# --- Upload Speed by City ---
city_group_sorted_u = city_group.sort_values(by='avg_u_speed_mbps', ascending=False)

plt.figure(figsize=(14, 6))
sns.barplot(data=city_group_sorted_u.head(20), x='city', y='avg_u_speed_mbps', palette='mako')
plt.title("Top 20 Cities by Average Upload Speed")
plt.xticks(rotation=45)
plt.ylabel("Upload Speed (Mbps)")
plt.xlabel("City")
plt.tight_layout()
plt.savefig('top_20_cities_upload_speed.png', dpi=300)
plt.show()

# Optional: print the top 5
print("\nTop 5 Cities by Average Upload Speed:")
print(city_group_sorted_u.head())


# --- Correlation Matrix ---
corr_cols = ['tests', 'devices', 'avg_d_speed_mbps', 'avg_u_speed_mbps', 'avg_lat_ms']
corr_matrix = df[corr_cols].corr()

# Print correlation values
print("\nCorrelation Matrix:")
print(corr_matrix)

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='inferno', fmt=".2f")
plt.title("Correlation Matrix: Tests, Devices, Speeds, and Latency")
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=300)
plt.show()


