import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset (adjust the file path as necessary)
csv_path = 'data/240924-0923_sop_ft533.csv'
df = pd.read_csv(csv_path)

# Ensure 'elapsed_time' is in the dataset
if 'elapsed_time' not in df.columns:
    raise KeyError("'elapsed_time' column is missing from the dataset. Please ensure the file contains the duration of the experiment.")

# Convert 'elapsed_time' to TimedeltaIndex
df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'], unit='s')

# Set 'elapsed_time' as the index for time-based operations
df.set_index('elapsed_time', inplace=True)

# === Visualizations === #

# Plot 1: Current, Voltage, and Power over elapsed time
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))

# Plot Current over elapsed time
ax1.plot(df.index.total_seconds(), df['Current'], color='green')
ax1.set_title('Current Over Experiment Duration')
ax1.set_xlabel('Duration (seconds)')
ax1.set_ylabel('Current (A)')
ax1.grid(True)

# Plot Voltage over elapsed time
ax2.plot(df.index.total_seconds(), df['Voltage'], color='blue')
ax2.set_title('Voltage Over Experiment Duration')
ax2.set_xlabel('Duration (seconds)')
ax2.set_ylabel('Voltage (V)')
ax2.grid(True)

# Plot Power over elapsed time
ax3.plot(df.index.total_seconds(), df['Power'], color='red')
ax3.set_title('Power Over Experiment Duration')
ax3.set_xlabel('Duration (seconds)')
ax3.set_ylabel('Power (W)')
ax3.grid(True)

# Adjust layout to prevent overlap
plt.tight_layout()

# Plot 2: Boxplot of Power
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['Power']], palette="Blues")
plt.title('Boxplot of Power', fontsize=14)
plt.ylabel('Values', fontsize=12)
plt.xlabel('Power', fontsize=12)

# Plot 3: Boxplot of Current
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['Current']], palette="Oranges")
plt.title('Boxplot of Current', fontsize=14)
plt.ylabel('Values', fontsize=12)
plt.xlabel('Current', fontsize=12)

# Plot 4: Histogram of Power
plt.figure(figsize=(10, 6))
sns.histplot(df['Power'].dropna(), bins=30, color='red')
plt.title('Histogram of Power')
plt.xlabel('Power (W)')
plt.ylabel('Frequency')

# Resample data to get the average power per minute (elapsed time in seconds)
df_resampled = df.resample('60s').mean()

# Drop NaN values from the resampled data (to ensure valid values for plotting)
df_resampled = df_resampled.dropna(subset=['Power'])

# Plot 5: Average power per minute
plt.figure(figsize=(10, 6))
plt.plot(df_resampled.index.total_seconds() / 60, df_resampled['Power'], color='red', label='Average Power (W)')
plt.title('Average Power per Minute')
plt.xlabel('Elapsed Time (minutes)')
plt.ylabel('Average Power (W)')
plt.grid(True)

# Show all the plots
plt.show()

# === Calculations and saving .tex file === #

# Calculate time differences between consecutive measurements (in hours)
df['time_diff_hours'] = df.index.to_series().diff().dt.total_seconds() / 3600  # elapsed_time is in seconds, convert to hours

# Fill NaN values in 'time_diff_hours' (set the first difference to 0)
df['time_diff_hours'] = df['time_diff_hours'].fillna(0)

# Calculate energy for each interval (Power * time_diff in hours) and convert to kWh
df['energy_kWh'] = (df['Power'] * df['time_diff_hours']) / 1000  # Watts to kWh conversion

# Calculate the total energy by summing the energy for all intervals
total_energy_kWh = df['energy_kWh'].sum()

# Calculate total elapsed time in minutes
total_elapsed_time_minutes = (df.index.max() - df.index.min()).total_seconds() / 60

# Generate a statistical summary (mean, std, min, max) for Power, Voltage, and Current
stats_summary = df[['Power', 'Voltage', 'Current']].describe()

# Create new rows for the total energy and total elapsed time in minutes
energy_row = pd.DataFrame({'Power': [total_energy_kWh], 'Voltage': [None], 'Current': [None]},
                          index=['Total Energy (kWh)'])

elapsed_time_row = pd.DataFrame({'Power': [None], 'Voltage': [None], 'Current': [total_elapsed_time_minutes]},
                                index=['Total Elapsed Time (min)'])

# Remove fully NA columns
energy_row_clean = energy_row.dropna(how='all', axis=1)
elapsed_time_row_clean = elapsed_time_row.dropna(how='all', axis=1)

# Concatenate the energy row and elapsed time row to the summary table
stats_summary = pd.concat([stats_summary, energy_row_clean, elapsed_time_row_clean])

# Save the statistical summary as a LaTeX file
latex_path = f'{csv_path}.tex'
stats_summary.to_latex(latex_path)
