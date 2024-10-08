
# PowerTrack: Real-Time Process Energy Analysis

This project monitors and visualizes the power consumption, voltage, and current of a specified process (e.g., MATLAB) using data from the Elmor Labs PMD sensor. It provides real-time data plotting and logging, useful for performance analysis and optimization. The code works on both Windows and Linux environments.

## Features

- **Real-Time Monitoring**: Continuously monitors and displays power, voltage, and current consumption of a specified process.
- **Cross-Platform Support**: Automatically detects the operating system (Windows or Linux) and adjusts the COM port settings accordingly.
- **Configurable Settings**: Easily configurable settings for sensor connection, process name, and other parameters.
- **Data Logging**: Automatically logs power consumption data to CSV files for later analysis.
- **Integrated Plotting**: Real-time plotting of power, voltage, and current measurements.
  
## Project Structure

```plaintext
your_project/
│
├── main.py                # Unified script for both Windows and Linux
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── data/                  # Directory where CSV files are saved
```

## Setup Instructions

### 1. Clone the Repository

To start, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/your_project.git
cd your_project
```

### 2. Create a Virtual Environment

It’s recommended to use a virtual environment to manage dependencies. You can create and activate a virtual environment using:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Configure the Script

Open the `main.py` script and adjust the settings at the top to match your environment:

```python
PMD_SETTINGS = {
    'port': None,  # The script will automatically detect the correct COM port for Windows or Linux
    'baudrate': 115200,
    'bytesize': 8,
    'stopbits': 1,
    'timeout': 1,
}
```

- **port**: Leave as `None` as the script will detect the correct port automatically.
- **process_name**: Specify the name of the process you want to monitor (e.g., `MATLAB.exe` for Windows, `firefox` for Linux).
- **save_to_csv**: Enable or disable saving the power data to a CSV file.

### 5. Run the Application

Once everything is set up, you can run the application using:

```bash
python main.py
```

The script will automatically detect the operating system and configure itself accordingly.

### 6. View and Save Data

The application will plot real-time graphs of power, voltage, and current consumption. Data is saved as CSV files in the `./data/` directory if the `SAVE_TO_CSV` flag is set to `True`.

### 7. Directory Setup

Ensure that a `./data/` directory exists in your project root. This is where the CSV files will be saved. If the directory does not exist, you can create it:

```bash
mkdir data
```

## Troubleshooting

### Common Issues

- **Sensor Connection Failed**: Ensure the PMD sensor is correctly connected to the specified COM port and that the settings in the script match the sensor’s configuration.
- **Process Not Found**: Verify that the process name specified in the script matches the actual name of the process as it appears in your system’s task manager.
- **Permission Errors**: Ensure that the script has permission to save files to the specified directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Original License

The original code is licensed under the MIT License:

```plaintext
MIT License

Copyright (c) 2022 bjorntas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Main Contributions

The main contributions to the creation of this code were made by [Celestino Simon](https://github.com/CSimon369).

## Inspiration

This code was inspired by the original project available at [elmorlabs-pmd-usb-serial-interface](https://github.com/bjorntas/elmorlabs-pmd-usb-serial-interface).
