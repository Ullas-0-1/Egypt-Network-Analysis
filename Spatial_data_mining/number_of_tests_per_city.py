import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")

# Group by city and sort
city_tests = df.groupby('city')['tests'].sum().sort_values(ascending=False).head(20)

# Plot
plt.figure(figsize=(10, 8))
sns.barplot(x=city_tests.values, y=city_tests.index, palette="plasma")
plt.xlabel("Number of Tests")
plt.ylabel("City")
plt.title("Top 20 Cities by Number of Tests")
plt.tight_layout()
plt.savefig("top_20_cities_by_tests.png", dpi=300)
plt.show()



import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point

# Load CSV
csv_path = '/Users/ullas/Desktop/STDA-PROJECT/network performance.csv'
df = pd.read_csv(csv_path)

# Load shapefile
shapefile_path = '/Users/ullas/Desktop/STDA-PROJECT/eg_shp/eg.shp'
governorates_gdf = gpd.read_file(shapefile_path)

# Extract city coordinates
city_coords = df.groupby('city')[['centroid_lon', 'centroid_lat']].first().to_dict('index')

# Function to get governorate from point
def get_governorate(city_name):
    coords = city_coords.get(city_name)
    if coords:
        point = Point(coords['centroid_lon'], coords['centroid_lat'])
        for _, row in governorates_gdf.iterrows():
            if row.geometry.contains(point):
                return row['name']  # Adjust if column name differs
    return None

# Map each row to its governorate
df['governorate'] = df['city'].apply(get_governorate)

# Drop rows where mapping failed
df = df.dropna(subset=['governorate'])

# Aggregate total tests by governorate
gov_tests = df.groupby('governorate')['tests'].sum().sort_values(ascending=False).head(15)

# Plot horizontal bar
plt.figure(figsize=(10, 8))
sns.barplot(x=gov_tests.values, y=gov_tests.index, palette="viridis")
plt.xlabel("Number of Tests")
plt.ylabel("Governorate")
plt.title("Top 15 Governorates by Number of Tests")
plt.tight_layout()
plt.savefig("top_15_governorates_by_tests.png", dpi=300)
plt.show()


# Full aggregation (for all governorates)
gov_test_counts = df.groupby('governorate')['tests'].sum().reset_index()

# Merge with shapefile
choropleth_gdf = governorates_gdf.merge(gov_test_counts, left_on='name', right_on='governorate', how='left')

# Fill NaN with 0 (some may have no test data)
choropleth_gdf['tests'] = choropleth_gdf['tests'].fillna(0)

# Plot choropleth
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
choropleth_gdf.plot(column='tests', ax=ax, legend=True, cmap='OrRd', edgecolor='black', linewidth=0.6)
ax.set_title('Number of Tests per Governorate in Egypt', fontsize=14)
ax.axis('off')
plt.savefig("choropleth_tests_per_governorate.png", dpi=300)
plt.show()


