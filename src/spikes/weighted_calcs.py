import numpy as np
import pandas as pd

def calculate_thompson(z, center):
    f_center = center
    i_charge = z
    thompson = f_center * i_charge - ((z - 1) * 1.0078)
    return thompson

# Define the original weighted_mean_std function
def weighted_mean_std(data, weight_col, value_col):
    mean = (data[value_col] * data[weight_col]).sum() / data[weight_col].sum()
    variance = (data[weight_col] * (data[value_col] - mean) ** 2).sum() / data[weight_col].sum()
    std = np.sqrt(variance)
    return mean, std

# Define the new weighted_mean_std function using numpy.average with weights
def weighted_mean_std_v2(data, weight_col, value_col):
    mean = np.average(data[value_col], weights=data[weight_col])
    variance = np.average((data[value_col] - mean)**2, weights=data[weight_col])
    std = np.sqrt(variance)
    return mean, std


# Load your dataframe (replace with the actual path to your CSV file)
df = pd.read_csv('resources/csv/spike_cluster.csv')

df["Center_Th"] = calculate_thompson(df["z"], df["Center"])

# Select a sample group for testing
sample_group = df.groupby(['Sequence', 'Exposure', 'State', 'Start', 'End', 'Protein']).get_group(('GSSHHHHHHSSGLVPRGSHMGSV', 0.0, 'AT21950', 1, 23, 'astex'))

# Calculate using both methods
mean1, std1 = weighted_mean_std(sample_group, 'Inten', 'Center_Th')
mean2, std2 = weighted_mean_std_v2(sample_group, 'Inten', 'Center_Th')

# Print results for comparison
print("Original method:", (mean1, std1))
print("Numpy.average method:", (mean2, std2))
