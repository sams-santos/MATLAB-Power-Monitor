import psutil
import pandas as pd
import serial
import platform
from datetime import datetime
import serial.tools.list_ports

# Detect operating system
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

# Sensor configuration
PMD_SETTINGS = {
    'port': None,  # Port will be assigned dynamically based on OS
    'baudrate': 115200,
    'bytesize': 8,
    'stopbits': 1,
    'timeout': 1,
}

NUM_CORES = psutil.cpu_count()


def detect_serial_port():
    """Detects the serial port based on the operating system and device description."""
    ports = list(serial.tools.list_ports.comports())

    # Define the target device description (e.g., USB-SERIAL CH340)
    target_device_description = 'USB-SERIAL CH340'

    if IS_WINDOWS:
        # For Windows, look for a device matching the target description
        for port in ports:
            if target_device_description in port.description:
                return port.device  # Return COMx port for Windows

    elif IS_LINUX:
        # For Linux, look for devices like /dev/ttyUSBx or /dev/ttySx
        for port in ports:
            # Check description and device name (typically /dev/ttyUSBx or /dev/ttySx)
            if target_device_description in port.description:
                return port.device  # Return /dev/ttyUSBx or /dev/ttySx for Linux

    print("No appropriate port found. Listing available ports:")
    list_ports()  # List all ports for debugging
    return None  # If no suitable port is found


def list_ports():
    """Lists all available COM ports."""
    ports = list(serial.tools.list_ports.comports())
    print('Available ports:')
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
    """Normalizes CPU usage to the range of 0-100%, considering the number of cores."""
    return min(max(cpu_usage / num_cores, 0.0), 100.0)


def check_connection() -> None:
    """Checks the connection with the Elmor Labs PMD sensor."""
    # Detect the appropriate port based on the operating system
    PMD_SETTINGS['port'] = detect_serial_port()
    
    if PMD_SETTINGS['port'] is None:
        print("No serial port detected.")
        return

    with serial.Serial(**PMD_SETTINGS) as ser:
        ser.write(b'\x00')  # Send a command to the sensor
        ser.flush()  # Ensure all data is sent
        read_bytes = ser.read(18)  # Read the welcome message
        assert read_bytes == b'ElmorLabs PMD-USB', "Incorrect welcome message"
        ser.write(b'\x02')  # Send another command to the sensor
        ser.flush()
        ser.read(100)  # Read additional data


def get_new_sensor_values() -> pd.DataFrame:
    """Gets new sensor values from the Elmor Labs PMD and stores them in a DataFrame."""
    # Detect the appropriate port based on the operating system
    PMD_SETTINGS['port'] = detect_serial_port()

    if PMD_SETTINGS['port'] is None:
        print("No serial port detected.")
        return pd.DataFrame()

    with serial.Serial(**PMD_SETTINGS) as ser:
        command = b'\x03'  # Command to request sensor data
        ser.write(command)
        ser.flush()
        read_bytes = ser.read(16)  # Read sensor data

    # Capture the current timestamp
    timestamp = pd.Timestamp(datetime.now())

    # Process the received sensor data
    i = 2  # Index for reading values
    name = 'EPS1'  # Sensor name
    voltage_value = int.from_bytes(read_bytes[i * 4:i * 4 + 2], byteorder='little') * 0.01
    current_value = int.from_bytes(read_bytes[i * 4 + 2:i * 4 + 4], byteorder='little') * 0.1
    pro1 = get_cpu_usage('rstudio.exe')
    pro2 = get_cpu_usage('rsession-utf8.exe')
    cpu_usage = pro1 + pro2
    cpu_usage_normalized = normalize_cpu_usage(cpu_usage, NUM_CORES)
    power_value = max((voltage_value * current_value * cpu_usage_normalized) / 100, 0)

    power_value = round(power_value, 4)

    # Create a DataFrame with the new sensor data
    data = {
        'timestamp': timestamp,
        'id': name,
        'unit': ['P', 'U', 'I'],
        'Power': [power_value, None, None],
        'Voltage': [None, voltage_value, None],
        'Current': [None, None, current_value],
    }

    return pd.DataFrame(data)


def save_data_to_csv(df: pd.DataFrame, date_name: str) -> None:
    """Saves the power data to a CSV file."""
    try:
        df_power = df[['timestamp', 'id', 'unit', 'Power']].dropna(subset=['Power'])
        file_path = f'./data/{date_name}_measurements.csv'
        df_power.to_csv(file_path, mode='w', header=True, index=False)
    except Exception as e:
        print(f"Error saving power data to CSV: {e}")
