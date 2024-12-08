import csv
import os
import sys
import subprocess

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

# Network configuration constants
SERVER_IP = "192.168.50.55"
NETMASK = "24"
INTERFACE = "eth0"
BASE_DELAY = "15.458ms"  # Can be adjusted based on experiment needs
RATE = "1000mbit"

def configure_network_interface():
    """Configure the server network interface with tc qdisc."""
    commands = [
        # Basic interface configuration
        ['ip', 'link', 'set', INTERFACE, 'up'],
        ['ip', 'addr', 'flush', 'dev', INTERFACE],
        ['ip', 'addr', 'add', f'{SERVER_IP}/{NETMASK}', 'dev', INTERFACE],
        
        # Remove existing qdisc if any
        ['tc', 'qdisc', 'del', 'dev', INTERFACE, 'root'],
        
        # Add traffic control qdisc (matching experiment_mn.py approach)
        ['tc', 'qdisc', 'add', 'dev', INTERFACE, 'root', 'netem'],
    ]
    
    for cmd in commands:
        try:
            # Allow the qdisc delete command to fail if no qdisc exists
            expected_returncode = 0
            if cmd[2] == 'del':
                expected_returncode = None  # Accept any return code for delete
            run_subprocess(cmd, expected_returncode=expected_returncode)
            print(f"Successfully executed: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            if cmd[2] != 'del':  # Only exit if non-delete command fails
                print(f"Error configuring network: {e}")
                sys.exit(1)

def change_qdisc(pkt_loss=0, delay=BASE_DELAY):
    """Update qdisc parameters (matching experiment_mn.py function)."""
    command = [
        'tc', 'qdisc', 'change', 'dev', INTERFACE, 'root', 'netem',
        'limit', '1000', 'delay', delay, 'rate', RATE
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
    if len(sys.argv) != 3:
        print("Usage: python server.py <nginx_path> <nginx_conf_dir>")
        sys.exit(1)

    nginx_path = sys.argv[1]
    nginx_conf_dir = sys.argv[2]

    # Configure network before starting nginx
    configure_network_interface()

    # Start nginx
    subprocess.run([nginx_path, "-c", nginx_conf_dir])
    print("[+]Nginx started")
