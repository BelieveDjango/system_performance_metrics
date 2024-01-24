import paramiko
import psutil
import csv
import time
import platform

# Global variable to track if the header has been written
header_written = False

def get_system_info(ip_address, username, password):
    system_platform = platform.system()

    if system_platform == 'Linux':
        return get_linux_system_info(ip_address, username, password)
    else:
        raise ValueError(f"Unsupported operating system: {system_platform}")

def get_linux_system_info(ip_address, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip_address, username=username, password=password)

        # Get CPU, memory, network, and disk utilization
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        network_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        # Get the current timestamp in traditional and Unix formats
        timestamp_traditional = time.strftime("%Y-%m-%d %H:%M:%S")
        timestamp_unix = int(time.time())

        # Return a dictionary with the collected metrics
        return {
            'Timestamp': timestamp_traditional,
            'Timestamp Unix': timestamp_unix,
            'IP Address': ip_address,
            'CPU Percent': cpu_percent,
            'Memory Percent': memory_percent,
            'Network Sent': network_io.bytes_sent,
            'Network Received': network_io.bytes_recv,
            'Disk Read': disk_io.read_bytes,
            'Disk Write': disk_io.write_bytes,
        }
    finally:
        ssh_client.close()

def save_to_csv(data, filename='system_metrics.csv'):
    global header_written  # Use the global variable

    # Save the metrics to the CSV file
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the header hasn't been written, write the header
        if not header_written:
            writer.writeheader()
            header_written = True

        # Write the row of data
        row_data = {key: value for key, value in data.items()}
        writer.writerow(row_data)

def main():
    # Define the target system's details
    target_ip = '192.168.10.133'
    username = 'username'
    password = 'Passw0rd'

    # Define the interval (in seconds) for data collection
    collection_interval = 5  # 5 seconds

    while True:
        try:
            # Get system information from the target system
            system_info = get_system_info(target_ip, username, password)

            # Save the metrics to a CSV file
            save_to_csv(system_info)

            # Print a message indicating successful data collection
            print(f"Metrics collected successfully at {system_info['Timestamp']}")
        except Exception as e:
            # Print an error message if an exception occurs
            print(f"Error: {e}")

        # Wait for the specified interval before collecting data again
        time.sleep(collection_interval)

if __name__ == "__main__":
    main()
