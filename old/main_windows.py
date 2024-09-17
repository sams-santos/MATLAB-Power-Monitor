import time
import serial
import psutil
import serial.tools.list_ports
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec

# Settings for the Elmor Labs PMD sensor connection
PMD_SETTINGS = {
    'port': 'COM4',  # Replace 'COM3' with the correct port for your setup
    'baudrate': 115200,
    'bytesize': 8,
    'stopbits': 1,
    'timeout': 1,
}

# Configuration flags
LIST_ALL_WINDOWS_PORTS = True  # Set to True to list all available COM ports
SAVE_TO_CSV = True  # Set to True to save the power data to a CSV file
MAX_LENGTH = 1000  # Maximum number of data points to retain in memory
PROCESS_NAME = 'MATLAB.exe'  # Name of the process to monitor
NUM_CORES = psutil.cpu_count()  # Get the number of CPU cores

# Initialize a global DataFrame for storing sensor data
df = pd.DataFrame(columns=['timestamp', 'id', 'unit', 'Power', 'Voltage', 'Current'])

# Define global variables for plot axes
voltage_ax = None
current_ax = None
power_ax = None


def list_ports():
    """Lists all available COM ports."""
    ports = list(serial.tools.list_ports.comports())
    print('USB PORTS:')
    for p in ports:
        print(p)
    print()


def get_cpu_usage(process_name: str) -> float:
    """Gets the CPU usage of a specific process."""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            cpu_usage = psutil.Process(process.info['pid']).cpu_percent(interval=1)
            return cpu_usage
    print(f"Process {process_name} not found.")
    return 0.0


def normalize_cpu_usage(cpu_usage: float, num_cores: int) -> float:
    """Normalizes CPU usage to a range of 0-100% considering the number of cores."""
    return min(max(cpu_usage / num_cores, 0.0), 100.0)


def check_connection() -> None:
    """Checks the connection with the Elmor Labs PMD sensor."""
    with serial.Serial(**PMD_SETTINGS) as ser:
        ser.write(b'\x00')  # Send a command to the sensor
        ser.flush()  # Ensure all data is sent
        read_bytes = ser.read(18)  # Read the welcome message
        assert read_bytes == b'ElmorLabs PMD-USB', "Incorrect welcome message received"

        ser.write(b'\x02')  # Send another command to the sensor
        ser.flush()  # Ensure all data is sent
        read_bytes = ser.read(100)  # Read additional data
        print('Struct:', read_bytes)  # Print the received data


def get_new_sensor_values() -> pd.DataFrame:
    """Gets new sensor values from the Elmor Labs PMD and stores them in a DataFrame."""
    with serial.Serial(**PMD_SETTINGS) as ser:
        command = b'\x03'  # Command to request sensor data
        ser.write(command)  # Send the command
        ser.flush()  # Ensure all data is sent
        read_bytes = ser.read(16)  # Read sensor data

    # Capture the current timestamp
    timestamp = pd.Timestamp(datetime.now())

    # Process the received sensor data
    i = 2  # Index for reading values
    name = 'EPS1'  # Sensor name
    voltage_value = int.from_bytes(read_bytes[i * 4:i * 4 + 2], byteorder='little') * 0.01
    current_value = int.from_bytes(read_bytes[i * 4 + 2:i * 4 + 4], byteorder='little') * 0.1
    cpu_usage = get_cpu_usage(PROCESS_NAME)
    cpu_usage_normalized = normalize_cpu_usage(cpu_usage, NUM_CORES)
    power_value = max((voltage_value * current_value * cpu_usage_normalized) / 100, 0)

    power_value = round(power_value, 4)

    print(f"MATLAB Power Consumption: {power_value}")

    # Create DataFrame with new sensor data
    data = {
        'timestamp': timestamp,
        'id': name,
        'unit': ['P', 'U', 'I'],
        'Power': [power_value, None, None],
        'Voltage': [None, voltage_value, None],
        'Current': [None, None, current_value],
    }

    return pd.DataFrame(data)


def animation_update(i):
    """Updates the plot with new sensor data."""
    global df

    # Get new sensor data
    df_new_data = get_new_sensor_values()
    df = pd.concat([df, df_new_data], ignore_index=True)  # Append new data to global DataFrame

    # Trim DataFrame to the last max_length rows if necessary
    if df.shape[0] > MAX_LENGTH:
        df = df.iloc[-MAX_LENGTH:]

    # Prepare data for plotting
    df_power_plot = df[df.unit == 'P'].pivot(columns=['id'], index='timestamp', values='Power')
    df_voltage_plot = df[df.unit == 'U'].pivot(columns=['id'], index='timestamp', values='Voltage')
    df_current_plot = df[df.unit == 'I'].pivot(columns=['id'], index='timestamp', values='Current')

    # Clear the axes for redrawing
    power_ax.cla()
    voltage_ax.cla()
    current_ax.cla()

    # Plot the data
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

    # Auto adjust plot limits
    power_ax.set_ylim(df_power_plot.min().min() * 0.9, df_power_plot.max().max() * 1.1)
    voltage_ax.set_ylim(df_voltage_plot.min().min() * 0.9, df_voltage_plot.max().max() * 1.1)
    current_ax.set_ylim(df_current_plot.min().min() * 0.9, df_current_plot.max().max() * 1.1)

    # Tighten layout to avoid overlapping
    fig.tight_layout()

    # Save data to CSV if enabled
    if SAVE_TO_CSV:
        save_data_to_csv(df)


def save_data_to_csv(df: pd.DataFrame) -> None:
    """Saves the power data to a CSV file."""
    try:
        df_power = df[['timestamp', 'id', 'unit', 'Power']].dropna(subset=['Power'])
        date_name = datetime.now().strftime('%Y-%m-%d-%H-%M')
        file_path = f'./data/{date_name}_power_measurements.csv'  # Use a generic path
        df_power.to_csv(file_path, mode='w', header=True, index=False)
        print(f"Power data saved to {file_path}")
    except Exception as e:
        print(f"Error saving power data to CSV: {e}")


if __name__ == "__main__":
    if LIST_ALL_WINDOWS_PORTS:
        list_ports()

    check_connection()

    plt.style.use('ggplot')

    # Define and adjust figure with gridspec for different subplot sizes
    fig = plt.figure(figsize=(10, 16), facecolor='#707576')
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
    voltage_ax = plt.subplot(gs[0])
    current_ax = plt.subplot(gs[1])
    power_ax = plt.subplot(gs[2])

    fig.suptitle('Measurement CPU and MATLAB', fontsize=14)

    anim = FuncAnimation(fig, animation_update, interval=1000, cache_frame_data=False)
    fig.tight_layout()
    fig.subplots_adjust(left=0.09)
    plt.show()
