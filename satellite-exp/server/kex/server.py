import csv
import os
import sys
import subprocess
import socket

# Network configuration constants
SERVER_IP = "192.168.50.55"
NETMASK = "24"
INTERFACE = "eth0"
BASE_LATENCY = "15.458ms"
RATE = "1000mbit"
SERVER_PORT = 8000

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
                # Ignore errors for tc qdisc del command
                try:
                    run_subprocess(cmd, expected_returncode=0)
                except AssertionError:
                    print(f"No existing qdisc to delete on {INTERFACE}")
            else:
                run_subprocess(cmd)
            print(f"Reset step completed: {' '.join(cmd)}")
        except AssertionError:
            print(f"Warning during reset: {' '.join(cmd)}")

def configure_network_interface():
    """Configure the server network interface without tc qdisc."""
    # First reset the interface
    reset_interface()
    
    commands = [
        # Basic interface configuration only
        ['ip', 'link', 'set', INTERFACE, 'up'],
        ['ip', 'addr', 'add', f'{SERVER_IP}/{NETMASK}', 'dev', INTERFACE],
        # Removed the tc qdisc configuration
    ]
    
    for cmd in commands:
        try:
            run_subprocess(cmd)
            print(f"Successfully executed: {' '.join(cmd)}")
        except AssertionError:
            print(f"Error executing command: {' '.join(cmd)}")
            sys.exit(1)

def stop_nginx():
    """Stop any running nginx processes."""
    try:
        run_subprocess(['pkill', 'nginx'], expected_returncode=None)
        print("Stopped existing nginx processes")
    except AssertionError:
        print("No existing nginx processes found")

def listen_for_client_completion():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        conn, addr = server_socket.accept()
        with conn:
            data = conn.recv(1024)
            if data == b"CLIENT_FINISHED":
                print("Client has finished!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server.py <nginx_path> <nginx_conf_dir>")
        sys.exit(1)

    nginx_path = sys.argv[1]
    nginx_conf_dir = sys.argv[2]

    # Stop any existing nginx processes
    stop_nginx()

    # Configure network before starting nginx
    configure_network_interface()

    # Start nginx
    subprocess.run([nginx_path, "-c", nginx_conf_dir])

    # Listen until client test RTT done
    listen_for_client_completion()

    # Listen until client test handshake done
    listen_for_client_completion()

    


