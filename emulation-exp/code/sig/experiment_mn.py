import csv
from multiprocessing import Pool
from mininet.net import Mininet
from mininet.node import Host
from mininet.link import TCLink
from mininet.topo import Topo
from tqdm import tqdm
import os
import sys

MEASUREMENTS_PER_TIMER = 100     # 10
TIMERS = 10                    # 4
# POOL_SIZE = 4
server, client = None, None

def change_qdisc(host, intf, pkt_loss, delay, bandwidth):
    """Apply packet loss and delay using NetEm in Mininet."""
    command = (
        f"tc qdisc change dev {intf} root netem "
        f"limit 1000 delay {delay} rate {bandwidth}mbit"
    )
    if pkt_loss > 0:
        command += f" loss {pkt_loss}%"
    print(f"{host.name}: {command}")
    host.cmd(command)

def time_handshake(sig_alg, measurements):
    """Run handshake timing test from a Mininet host."""
    command = f"./s_timer.o {sig_alg} {measurements}"
    result = client.cmd(command)
    result = result.replace("\r", "")
    result = result.replace("\n", "")
    
    return [float(i) for i in result.split(",") if i != ""]

def run_timers(sig_alg):
    """Run multiple timer measurements for a key exchange algorithm sequentially."""
    results = []
    for _ in tqdm(range(TIMERS), desc="Running timers"):
        results.extend(time_handshake(sig_alg, MEASUREMENTS_PER_TIMER))
    return results

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
    if len(sys.argv) != 4:
        print("Usage: python3 experiment_mn.py <sig_alg> <nginx_path> <nginx_conf_dir>")
        sys.exit(1)

    sig_alg = sys.argv[1]
    nginx_path = sys.argv[2]
    nginx_conf_dir = sys.argv[3]

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

    # Create data directory
    if not os.path.exists("../../mn_data/sig"):
        os.makedirs("../../mn_data/sig")

    # Experiment loop
    for latency_ms in ["2.684ms", "15.458ms", "39.224ms", "97.73ms", "297.73ms"]:
        client_bandwidth = 100  # 100 Mbps DL
        server_bandwidth = 20  # 20 Mbps UL
        # Configure base delay
        change_qdisc(client, "h2-eth0", 0, latency_ms, client_bandwidth)
        change_qdisc(server, "h1-eth0", 0, latency_ms, server_bandwidth)
        rtt_str = get_rtt_ms(client, server)
        print(f"✅ RTT measurement success! RTT: {rtt_str}")
        
        # Open CSV file for results
        with open(f"../../mn_data/sig/{sig_alg}_{rtt_str}ms.csv", "w") as out_file:
            csv_writer = csv.writer(out_file)

            # Test different packet loss rates
            for pkt_loss in [0, 0.1, 0.5, 1, 1.5, 2, 2.5, 3] + list(range(4, 21)):
                change_qdisc(client, "h2-eth0", pkt_loss, latency_ms, client_bandwidth)
                change_qdisc(server, "h1-eth0", pkt_loss, latency_ms, server_bandwidth)

                # Measure handshake times
                results = run_timers(sig_alg)
                results.insert(0, pkt_loss)
                csv_writer.writerow(results)

    # Cleanup
    net.stop()