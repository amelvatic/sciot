#!/bin/bash

# Array to hold the PIDs of the background processes
pids=()
sudo systemctl stop serial-getty@USB0.service 

# Function to start a Python script in the background
start_script() {
    local script_name=$1
    python3 $script_name &
    local pid=$!
    pids+=($pid)
    echo "Started $script_name with PID $pid"
}

# Function to kill all background processes
kill_scripts() {
    echo "Killing all background processes..."
    for pid in "${pids[@]}"; do
        kill $pid
        echo "Killed process with PID $pid"
    done
}

# Function to handle script termination
terminate() {
    echo "Termination signal received. Cleaning up..."
    kill_scripts
    exit 0
}

# Trap termination signals to ensure cleanup
trap terminate SIGINT SIGTERM

# List of Python scripts to run
scripts=('sensors/air_t&h.py --id 1' 'sensors/water_level.py --id 2' "sensors/light.py --id 3" "actuators/led_indicator.py" "actuators/water_pump.py" "actuators/fan.py"  "actuators/arduino_acc.py" "main.py")

# Start all Python scripts
for script in "${scripts[@]}"; do
    start_script $script
done

# Wait for all background processes to finish
wait