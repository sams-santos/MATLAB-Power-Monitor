import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
from datetime import datetime
from utils import list_ports, check_connection, get_new_sensor_values, save_data_to_csv

# Configuration settings
LIST_ALL_WINDOWS_PORTS = True
SAVE_TO_CSV = True
MAX_LENGTH = 1000

# Initialize global DataFrame
df = pd.DataFrame(columns=['timestamp', 'id', 'unit', 'Power', 'Voltage', 'Current'])
date_name = datetime.now().strftime('%y%m%d-%H%M')

# Define global variables for the plot axes
voltage_ax = None
current_ax = None
power_ax = None


def animation_update(i):
    """Updates the plot with new sensor data."""
    global df

    # Collect new sensor data
    df_new_data = get_new_sensor_values()
    df = pd.concat([df, df_new_data], ignore_index=True)

    # Keep only the last MAX_LENGTH data points
    if df.shape[0] > MAX_LENGTH:
        df = df.iloc[-MAX_LENGTH:]

    # Prepare data for plotting
    df_power_plot = df[df.unit == 'P'].pivot(columns=['id'], index='timestamp', values='Power')
    df_voltage_plot = df[df.unit == 'U'].pivot(columns=['id'], index='timestamp', values='Voltage')
    df_current_plot = df[df.unit == 'I'].pivot(columns=['id'], index='timestamp', values='Current')

    # Clear axes for new update
    power_ax.cla()
    voltage_ax.cla()
    current_ax.cla()

    # Plot data
    df_power_plot.plot(ax=power_ax, legend=False, color='red', linewidth=2)
    df_voltage_plot.plot(ax=voltage_ax, legend=False, color='blue', linewidth=2)
    df_current_plot.plot(ax=current_ax, legend=False, color='green', linewidth=2)

    # Set axis labels and titles
    power_ax.set_ylabel('Power Consumption [W]', fontsize=12, color='red')
    voltage_ax.set_ylabel('Voltage [V]', fontsize=12, color='blue')
    current_ax.set_ylabel('Current [A]', fontsize=12, color='green')

    # Set titles for each plot
    power_ax.set_title('Real-Time MATLAB Power Consumption', fontsize=14, color='red')
    voltage_ax.set_title('Real-Time CPU Voltage Consumption', fontsize=14, color='blue')
    current_ax.set_title('Real-Time CPU Current Consumption', fontsize=14, color='green')

    # Display gridlines
    power_ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    voltage_ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    current_ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Format x-axis to display time correctly
    power_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    voltage_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    current_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    # Rotate date labels for better readability
    plt.setp(power_ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.setp(voltage_ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.setp(current_ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Set axis limits to avoid singular transformation error
    buffer = 1e-6  # Small buffer to avoid singular transformations
    power_ax.set_ylim(df_power_plot.min().min() * 0.9 - buffer, df_power_plot.max().max() * 1.1 + buffer)
    voltage_ax.set_ylim(df_voltage_plot.min().min() * 0.9 - buffer, df_voltage_plot.max().max() * 1.1 + buffer)
    current_ax.set_ylim(df_current_plot.min().min() * 0.9 - buffer, df_current_plot.max().max() * 1.1 + buffer)

    # Apply layout adjustments
    fig.tight_layout()

    # Save data to CSV if enabled
    if SAVE_TO_CSV:
        save_data_to_csv(df, date_name)


if __name__ == "__main__":
    if LIST_ALL_WINDOWS_PORTS:
        list_ports()

    check_connection()

    plt.style.use('ggplot')

    # Define and adjust figure with gridspec for different subplot sizes
    fig = plt.figure(figsize=(10, 16), facecolor='#707576')
    gs = plt.GridSpec(3, 1, height_ratios=[1, 1, 1])
    voltage_ax = plt.subplot(gs[0])
    current_ax = plt.subplot(gs[1])
    power_ax = plt.subplot(gs[2])

    fig.suptitle('Measurement CPU and MATLAB', fontsize=14)
    anim = FuncAnimation(fig, animation_update, interval=1000, cache_frame_data=False)
    fig.tight_layout()
    fig.subplots_adjust(left=0.09)
    plt.show()
