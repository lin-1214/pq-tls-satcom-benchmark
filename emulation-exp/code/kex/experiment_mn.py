import csv
from multiprocessing import Pool
from mininet.net import Mininet
from mininet.node import Host
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
import os
import subprocess

# Experiment settings
POOL_SIZE = 4
MEASUREMENTS_PER_TIMER = 100
TIMERS = 50

def run_subprocess(command, expected_returncode=0):
    """Run a shell command and return the output."""
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    if result.stderr:
        print(result.stderr.decode('utf-8'))
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

def test_connection(client, server):
    """Test the connection between client and server using ping."""
    print("Testing connection between client and server...")
    result = client.cmd(f"ping -c 3 {server.IP()}")
    if "0% packet loss" in result:
        print("✅ Connection test passed: No packet loss.")
    else:
        print("❌ Connection test failed: Packet loss detected.")

def change_qdisc(host, intf, pkt_loss, delay):
    """Apply packet loss and delay using NetEm in Mininet."""
    command = (
        f"tc qdisc change dev {intf} root netem "
        f"limit 1000 delay {delay} rate 1000mbit"
    )
    if pkt_loss > 0:
        command += f" loss {pkt_loss}%"
    print(f"{host.name}: {command}")
    host.cmd(command)

def time_handshake(host, kex_alg, measurements):
    """Run handshake timing test from a Mininet host."""
    command = f"./s_timer.o {kex_alg} {measurements}"
    result = host.cmd(command)
    return [float(i) for i in result.strip().split(",")]

def time_handshake_task(args):
    """Helper function to unpack arguments for time_handshake."""
    net, host_name, kex_alg, measurements = args
    host = net.get(host_name)
    return time_handshake(host, kex_alg, measurements)

def run_timers(net, host_name, kex_alg, timer_pool):
    """Run multiple timer measurements for a key exchange algorithm."""
    tasks = [(net, host_name, kex_alg, MEASUREMENTS_PER_TIMER)] * TIMERS
    results_nested = timer_pool.starmap(time_handshake_task, tasks)
    return [item for sublist in results_nested for item in sublist]

def get_rtt_ms(client, server):
    """Ping the server from the client and extract RTT."""
    result = client.cmd(f"ping {server.IP()} -c 30")
    print(result)
    lines = result.splitlines()
    rtt_line = [line for line in lines if "rtt" in line][0]
    avg_rtt = rtt_line.split("/")[4]
    return avg_rtt.replace(".", "p")

class ExperimentTopo(Topo):
    """Custom Mininet topology with one client and one server."""
    def build(self):
        # Add two hosts and a direct link
        client = self.addHost("h1", ip="10.0.0.2")
        server = self.addHost("h2", ip="10.0.0.1")
        self.addLink(client, server, cls=TCLink)

if __name__ == "__main__":
    # Create the network
    topo = ExperimentTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Get client and server hosts
    client = net.get("h1")
    server = net.get("h2")

    # Configure network interfaces
    client.cmd("tc qdisc add dev h1-eth0 root netem")
    server.cmd("tc qdisc add dev h2-eth0 root netem")

    # Test connection
    test_connection(client, server)

    # Create thread pool for parallel processing
    timer_pool = Pool(processes=POOL_SIZE)

    # Create data directory
    if not os.path.exists("mn_data"):
        os.makedirs("mn_data")

    # Experiment loop
    for latency_ms in ["2.684ms", "15.458ms", "39.224ms", "97.73ms"]:
        # Configure base delay
        change_qdisc(client, "h1-eth0", 0, latency_ms)
        change_qdisc(server, "h2-eth0", 0, latency_ms)
        rtt_str = get_rtt_ms(client, server)

        for kex_alg in ["prime256v1", "p256_kyber512_90s", "p256_frodo640aes", "p256_sikep434"]:
            # Open CSV file for results
            with open(f"mn_data/{kex_alg}_{rtt_str}ms.csv", "w") as out_file:
                csv_writer = csv.writer(out_file)

                # Test different packet loss rates
                for pkt_loss in [0, 0.1, 0.5, 1, 1.5, 2, 2.5, 3] + list(range(4, 21)):
                    change_qdisc(client, "h1-eth0", pkt_loss, latency_ms)
                    change_qdisc(server, "h2-eth0", pkt_loss, latency_ms)

                    # Measure handshake times
                    results = run_timers(net, "h1", kex_alg, timer_pool)
                    results.insert(0, pkt_loss)
                    csv_writer.writerow(results)

    # Cleanup
    timer_pool.close()
    timer_pool.join()
    net.stop()