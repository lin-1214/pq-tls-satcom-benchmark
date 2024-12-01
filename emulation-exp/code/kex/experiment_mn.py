import csv
from multiprocessing import Pool
from mininet.net import Mininet
from mininet.node import Host
from mininet.link import TCLink
from mininet.topo import Topo
import os
import sys

MEASUREMENTS_PER_TIMER = 100
TIMERS = 50
POOL_SIZE = 4

client = None
server = None

def test_connection(client, server):
    """Test the connection between client and server using ping."""
    print("Testing connection between client and server...")
    result = client.cmd(f"ping -c 3 {server.IP()}")
    if "0% packet loss" in result:
        print("✅ Connection test passed: No packet loss.")
    else:
        print("❌ Connection test failed: Packet loss detected.")

    print("Testing nginx connection...")
    print(f"Curling {server.IP()}:4433")
    curl_result = client.cmd(f"curl -k https://{server.IP()}:4433")
    if curl_result:
        print("✅ Nginx test passed: Received response from server")
        # print(f"Response: {curl_result[:200]}...")  # Show first 200 chars of response
    else:
        print("❌ Nginx test failed: No response from server")
        print("Debugging info:")
        print(client.cmd(f"curl -v http://{server.IP()}:4433"))
        net.stop()
        sys.exit(1)

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

def time_handshake(kex_alg, measurements):
    """Run handshake timing test from a Mininet host."""
    command = f"./s_timer.o {kex_alg} {measurements}"
    result = client.cmd(command)
    result = result.replace("\r", "")
    result = result.replace("\n", "")

    return [float(i) for i in result.split(",") if i != ""]


def run_timers(kex_alg):
    """Run multiple timer measurements for a key exchange algorithm in parallel."""
    with Pool(processes=POOL_SIZE) as timer_pool:
        results_nested = timer_pool.starmap(time_handshake, [(kex_alg, MEASUREMENTS_PER_TIMER)] * TIMERS)
        return [item for sublist in results_nested for item in sublist if sublist != []]

def get_rtt_ms(client, server):
    """Ping the server from the client and extract RTT."""
    result = client.cmd(f"ping {server.IP()} -c 30")
    # print(f"[DEBUG] Ping result: {result}")
    lines = result.splitlines()
    rtt_line = [line for line in lines if "rtt" in line][0]
    avg_rtt = rtt_line.split("/")[4]
    return avg_rtt.replace(".", "p")

class ExperimentTopo(Topo):
    """Custom Mininet topology with one client and one server."""
    def build(self):
        # Add two hosts and a direct link
        client = self.addHost("h2", ip="10.0.0.2")
        server = self.addHost("h1", ip="10.0.0.1")
        self.addLink(client, server, cls=TCLink)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python experiment_mn.py <nginx_path> <nginx_conf_dir>")
        sys.exit(1)

    nginx_path = sys.argv[1]
    nginx_conf_dir = sys.argv[2]

    # Create the network
    topo = ExperimentTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Get client and server hosts
    client = net.get("h2")
    server = net.get("h1")

    # Configure network interfaces
    client.cmd("tc qdisc add dev h2-eth0 root netem")
    server.cmd("tc qdisc add dev h1-eth0 root netem")

    # Start nginx on server
    server.cmd(f"{nginx_path} -c {nginx_conf_dir}")

    # Test connection
    test_connection(client, server)

    # Create data directory
    if not os.path.exists("../../mn_data/kex"):
        os.makedirs("../../mn_data/kex")

    # Experiment loop
    for latency_ms in ["2.684ms", "15.458ms", "39.224ms", "97.73ms"]:
        # Configure base delay
        change_qdisc(client, "h2-eth0", 0, latency_ms)
        change_qdisc(server, "h1-eth0", 0, latency_ms)
        rtt_str = get_rtt_ms(client, server)
        print(f"✅ RTT measurement success! RTT: {rtt_str}")

        for kex_alg in ["prime256v1", "p256_kyber512_90s"]:
            # Open CSV file for results
            with open(f"../../mn_data/kex/{kex_alg}_{rtt_str}ms.csv", "w") as out_file:
                csv_writer = csv.writer(out_file)

                # Test different packet loss rates
                for pkt_loss in [0, 0.1, 0.5, 1, 1.5, 2, 2.5, 3] + list(range(4, 13)):
                    change_qdisc(client, "h2-eth0", pkt_loss, latency_ms)
                    change_qdisc(server, "h1-eth0", pkt_loss, latency_ms)

                    # Measure handshake times
                    results = run_timers(kex_alg)
                    results.insert(0, pkt_loss)
                    csv_writer.writerow(results)

    # Cleanup
    net.stop()
