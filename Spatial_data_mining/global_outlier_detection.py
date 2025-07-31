#second plot is usefull-- and looks very good 
#but there is no point of global outliers here -- explain this there please 



import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Load your dataset
df = pd.read_csv("/Users/ullas/Desktop/STDA-PROJECT/network performance.csv")  # replace with your file path

# Set the variable to check (you can switch this to avg_u_speed_mbps, avg_lat_ms, etc.)
variable = 'avg_d_speed_mbps'

# Calculate Z-scores
df['z_score'] = stats.zscore(df[variable])

# Define outliers (e.g., beyond ±3 standard deviations)
df['is_outlier'] = df['z_score'].abs() > 3

# 📊 Boxplot
plt.figure(figsize=(8, 1.5))
sns.boxplot(x=df[variable], color='skyblue')
plt.title(f'Boxplot of {variable}')
plt.show()

# 🗺️ Scatterplot with outliers colored
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='centroid_lon', y='centroid_lat', hue='is_outlier', palette={True: 'red', False: 'blue'})
plt.title(f'Global Outliers in {variable} (Spatial View)')
plt.legend(title='Outlier')
plt.savefig('global_outliers.png', dpi=300, bbox_inches='tight')
plt.show()

# use the second figure --
