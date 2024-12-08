import csv
import os
import sys
from tqdm import tqdm
import subprocess

# Network configuration constants
SERVER_IP = "192.168.50.55"
CLIENT_IP = "192.168.50.54"  # Corrected client IP
NETMASK = "24"
INTERFACE = "eth0"
RATE = "1000mbit"
BASE_LATENCY = "15.458ms"

def run_subprocess(command, working_dir='.', expected_returncode=0):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir
    )
    if(result.stderr):
        print(result.stderr)
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

def reset_interface():
    """Reset the network interface to a clean state."""
    reset_commands = [
        ['ip', 'link', 'set', INTERFACE, 'down'],
        ['ip', 'addr', 'flush', 'dev', INTERFACE],
        ['tc', 'qdisc', 'del', 'dev', INTERFACE, 'root'],  # Just delete root qdisc
    ]
    
    for cmd in reset_commands:
        try:
            if 'qdisc' in cmd:
                try:
                    run_subprocess(cmd, expected_returncode=2)  # Allow error code 2 for non-existent qdisc
                except AssertionError:
                    print(f"No existing qdisc to delete on {INTERFACE}")
            else:
                run_subprocess(cmd)
            print(f"Reset step completed: {' '.join(cmd)}")
        except AssertionError:
            print(f"Warning during reset: {' '.join(cmd)}")

def configure_network_interface():
    """Configure the client network interface with tc qdisc."""
    # First reset the interface
    reset_interface()
    
    commands = [
        # Basic interface configuration
        ['ip', 'link', 'set', INTERFACE, 'up'],
        ['ip', 'addr', 'add', f'{CLIENT_IP}/{NETMASK}', 'dev', INTERFACE],
        # Add traffic control qdisc
        ['tc', 'qdisc', 'add', 'dev', INTERFACE, 'root', 'netem'],  # Simplified command
    ]
    
    for cmd in commands:
        try:
            run_subprocess(cmd)
            print(f"Successfully executed: {' '.join(cmd)}")
        except AssertionError:
            print(f"Error executing command: {' '.join(cmd)}")
            sys.exit(1)

def get_rtt_ms():
    """Ping the server and extract RTT."""
    result = run_subprocess(['ping', SERVER_IP, '-c', '30'])
    lines = result.splitlines()
    rtt_line = [line for line in lines if "rtt" in line][0]
    avg_rtt = rtt_line.split("/")[4]
    return avg_rtt.replace(".", "p")

def change_qdisc(pkt_loss=0, latency=BASE_LATENCY):
    """Update qdisc parameters (matching experiment_mn.py function)."""
    command = [
        'tc', 'qdisc', 'change', 'dev', INTERFACE, 'root', 'netem',
        'limit', '1000', 'delay', latency, 'rate', RATE
    ]
    if pkt_loss > 0:
        command.extend(['loss', f'{pkt_loss}%'])
    
    try:
        run_subprocess(command)
        print(f"Successfully updated qdisc: {' '.join(command)}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating qdisc: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Configure network interface first
    configure_network_interface()
    
    # Change qdisc to initial state
    change_qdisc()
    
    # Measure RTT
    rtt_str = get_rtt_ms()
    print(f"✅ RTT measurement success! RTT: {rtt_str}")
    
