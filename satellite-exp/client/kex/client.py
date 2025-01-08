import csv
import os
import sys
from tqdm import tqdm
import subprocess
import socket
import json
# Network configuration constants
SERVER_IP = None
CLIENT_IP = None
SERVER_PORT = None

# Read network configuration from config file
with open('../config.json') as f:
    config = json.load(f)
    SERVER_IP = config['server_ip']
    CLIENT_IP = config['client_ip']
    SERVER_PORT = int(config['socket_port'])


NETMASK = "24"
INTERFACE = "eth0"
MEASUREMENTS_PER_TIMER = 100
TIMERS = 50

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

def send_completion_message():
    """Send a completion message to the server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.sendall(b"CLIENT_FINISHED")
            print("✅ Completion message sent to server")
    except ConnectionRefusedError:
        print("❌ Could not connect to server - is it running?")
    except Exception as e:
        print(f"❌ Error sending completion message: {e}")

def time_handshake(kex_alg, measurements):
    """Run handshake timing test from a Mininet host."""
    result = run_subprocess(["./s_timer.o", kex_alg, str(measurements)])
    result = result.replace("\r", "")
    result = result.replace("\n", "")

    return [float(i) for i in result.split(",") if i != ""]


def run_timers(kex_alg):
    """Run multiple timer measurements for a key exchange algorithm in parallel."""
    results = []
    for _ in tqdm(range(TIMERS), desc="Running timers"):
        results.extend(time_handshake(kex_alg, MEASUREMENTS_PER_TIMER))
    return results

if __name__ == "__main__":
    # Configure network interface first
    configure_network_interface()
    
    # Measure RTT
    rtt_str = get_rtt_ms()
    print(f"✅ RTT measurement success! RTT: {rtt_str}")
    
    # Send completion message
    send_completion_message()

    # Create data directory
    if not os.path.exists("../../sat_data/kex"):
        os.makedirs("../../sat_data/kex")

    for kex_alg in ["prime256v1", "p256_kyber512_90s"]:
        results = run_timers(kex_alg)
        with open(f"../../sat_data/kex/{kex_alg}_{rtt_str}ms.csv", "w") as out_file:
            csv_writer = csv.writer(out_file)
            csv_writer.writerow(results)

    # Send completion message
    send_completion_message()