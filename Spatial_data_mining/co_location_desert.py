import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.stats import ttest_ind

# --- File Paths ---
csv_file_path = '/Users/ullas/Desktop/STDA-PROJECT/network performance.csv'
governorate_shapefile_path = '/Users/ullas/Desktop/STDA-PROJECT/eg_shp/eg.shp'

try:
    # --- Read the CSV file into a DataFrame ---
    df = pd.read_csv(csv_file_path)

    # --- Get unique city names ---
    unique_cities = df['city'].unique().tolist()

    # --- Get coordinates for each city ---
    city_coordinates = {}
    for city in unique_cities:
        city_row = df[df['city'] == city].iloc[0]
        city_coordinates[city] = (city_row['centroid_lon'], city_row['centroid_lat'])

    # --- Load governorate shapefile ---
    governorates = gpd.read_file(governorate_shapefile_path)

    # --- Find governorate of a city using coordinates ---
    def find_governorate(city_name, governorates_gdf, city_lat_lon_dict):
        if city_name in city_lat_lon_dict:
            lon, lat = city_lat_lon_dict[city_name]
            point = Point(lon, lat)
            for index, row in governorates_gdf.iterrows():
                if row['geometry'].contains(point):
                    return row['name']  # Adjust column name as needed
            return None
        else:
            return None

    # --- Map cities to governorates ---
    city_governorate_mapping = {}
    for city in unique_cities:
        governorate = find_governorate(city, governorates, city_coordinates)
        city_governorate_mapping[city] = governorate

    # --- Add governorate column to original DataFrame ---
    df['governorate'] = df['city'].map(city_governorate_mapping)

    # --- Filter Western Desert Governorates ---
    western_desert_governorates = ['Al Wadi al Jadid', 'Matruh','Asyut','Minya','Beni Suef','Faiyum','Qena','Sohag']
    df_western_desert = df[df['governorate'].isin(western_desert_governorates)]
    df_other = df[~df['governorate'].isin(western_desert_governorates)]

    # --- Display average values ---
    print("\n--- AVERAGE VALUES ---")
    print("Western Desert Governorates:")
    print(df_western_desert[['avg_d_speed_mbps', 'avg_u_speed_mbps']].mean())
    print(f"Number of test records: {len(df_western_desert)}\n")

    print("Other Governorates:")
    print(df_other[['avg_d_speed_mbps', 'avg_u_speed_mbps']].mean())
    print(f"Number of test records: {len(df_other)}\n")

    # --- T-tests ---
    print("--- STATISTICAL TEST RESULTS ---")
    download_ttest = ttest_ind(df_western_desert['avg_d_speed_mbps'], df_other['avg_d_speed_mbps'], equal_var=False)
    upload_ttest = ttest_ind(df_western_desert['avg_u_speed_mbps'], df_other['avg_u_speed_mbps'], equal_var=False)

    print(f"Download Speed - t-statistic: {download_ttest.statistic:.2f}, p-value: {download_ttest.pvalue:.4f}")
    print(f"Upload Speed   - t-statistic: {upload_ttest.statistic:.2f}, p-value: {upload_ttest.pvalue:.4f}")

    # --- Interpretation ---
    significance_level = 0.05
    print("\n--- INTERPRETATION ---")
    if download_ttest.pvalue < significance_level:
        print("✅ The average **download speed** is statistically significantly lower in the Western Desert governorates.")
    else:
        print("❌ No significant difference in download speed.")

    if upload_ttest.pvalue < significance_level:
        print("✅ The average **upload speed** is statistically significantly lower in the Western Desert governorates.")
    else:
        print("❌ No significant difference in upload speed.")

    if len(df_western_desert) < len(df_other) * 0.25:
        print("✅ Western Desert governorates have **fewer test records**, suggesting lower coverage.")
    else:
        print("❌ Number of tests is not significantly lower.")

except FileNotFoundError as e:
    print(f"Error: File not found at '{e.filename}'. Please check the file path.")
except KeyError as e:
    print(f"Error: Column '{e}' not found in the CSV file.")
except Exception as e:
    print(f"An error occurred: {e}")
