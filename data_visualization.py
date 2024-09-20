import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates

# Load the dataset (adjust the file path as necessary)
csv_path = 'data/240920-1125_measurements.csv'
df = pd.read_csv(csv_path)

# Convert 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')

# Set 'timestamp' as the index for time-based operations
df.set_index('timestamp', inplace=True)

# === Visualizations === #

# Plot 1: Current, Voltage, and Power over time
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))

# Plot Current over time
ax1.plot(df.index, df['Current'], color='green')
ax1.set_title('Current Over Time')
ax1.set_xlabel('Time')
ax1.set_ylabel('Current (A)')
ax1.grid(True)

# Plot Voltage over time
ax2.plot(df.index, df['Voltage'], color='blue')
ax2.set_title('Voltage Over Time')
ax2.set_xlabel('Time')
ax2.set_ylabel('Voltage (V)')
ax2.grid(True)

# Plot Power over time
ax3.plot(df.index, df['Power'], color='red')
ax3.set_title('Power Over Time')
ax3.set_xlabel('Time')
ax3.set_ylabel('Power (W)')
ax3.grid(True)

# Format x-axes to show time as hours and minutes
for ax in [ax1, ax2, ax3]:
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Only show hours and minutes
    ax.xaxis.set_minor_locator(mdates.MinuteLocator())
    fig.autofmt_xdate()

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

# Resample data to get the average power per minute
df_resampled = df.resample('min').mean()

# Drop NaN values from the resampled data (to ensure valid values for plotting)
df_resampled = df_resampled.dropna(subset=['Power'])

# Plot 5: Average power per minute
plt.figure(figsize=(10, 6))
plt.plot(df_resampled.index, df_resampled['Power'], color='red', label='Average Power (W)')
plt.title('Average Power per Minute')
plt.xlabel('Time')
plt.ylabel('Average Power (W)')
plt.grid(True)

# Format x-axis for minute display
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Rotate date labels for better readability
plt.gcf().autofmt_xdate()

# Show all the plots
plt.show()

# === Calculations and saving .tex file === #

# Calculate time differences between consecutive measurements (in hours)
df['time_diff_hours'] = df.index.to_series().diff().dt.total_seconds() / 3600

# Fill NaN values in 'time_diff_hours' (set the first difference to 0)
df['time_diff_hours'] = df['time_diff_hours'].fillna(0)

# Calculate energy for each interval (Power * time_diff in hours) and convert to kWh
df['energy_kWh'] = (df['Power'] * df['time_diff_hours']) / 1000  # Watts to kWh conversion

# Calculate the total energy by summing the energy for all intervals
total_energy_kWh = df['energy_kWh'].sum()

# Generate a statistical summary (mean, std, min, max) for Power, Voltage, and Current
stats_summary = df[['Power', 'Voltage', 'Current']].describe()

# Create a new row for the total energy and remove fully NA columns
energy_row = pd.DataFrame({'Power': [total_energy_kWh], 'Voltage': [None], 'Current': [None]},
                          index=['Total Energy (kWh)'])
energy_row_clean = energy_row.dropna(how='all', axis=1)  # Remove columns that are fully NA

# Concatenate the energy row to the summary table
stats_summary = pd.concat([stats_summary, energy_row_clean])

# Save the statistical summary as a LaTeX file
latex_path = f'{csv_path}.tex'
stats_summary.to_latex(latex_path)
