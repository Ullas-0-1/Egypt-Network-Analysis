
import pandas as pd
import numpy as np

# Load your dataset
df = pd.read_csv('/Users/ullas/Desktop/STDA-PROJECT/network performance.csv')

# Extract coordinates
coords = df[['centroid_lon', 'centroid_lat']].dropna().values

from astropy.stats import RipleysKEstimator
import matplotlib.pyplot as plt

# Define the area of the study region (e.g., bounding box area)
area = (df['centroid_lon'].max() - df['centroid_lon'].min()) * (df['centroid_lat'].max() - df['centroid_lat'].min())

# Initialize the estimator
rk = RipleysKEstimator(area=area, x_max=df['centroid_lon'].max(), y_max=df['centroid_lat'].max())

# Define radii at which to evaluate K
radii = np.linspace(0, 0.5, 50)  # Adjust the max radius as needed

# Evaluate K-function
k_values = rk(data=coords, radii=radii, mode='none')  # 'none' means no edge correction

# Theoretical CSR K-function
k_theoretical = np.pi * radii**2

# Plot
plt.figure(figsize=(8, 6))
plt.plot(radii, k_values, label='Observed K(r)')
plt.plot(radii, k_theoretical, '--', label='CSR K(r)')
plt.xlabel('Radius r')
plt.ylabel('K(r)')
plt.title("Ripley's K-function")
plt.legend()
plt.grid(True)
plt.show()
plt.savefig('ripley_k_function.png')
