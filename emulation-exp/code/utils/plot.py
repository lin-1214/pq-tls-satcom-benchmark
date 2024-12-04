import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

KEX_ALG = ['p256_kyber512_90s', 'prime256v1']
SIG_ALG = ['dilithium2', 'ecdsap256']

def plot_data(pkt_loss, handshake_time_pq, handshake_time_trad, type, label=None):
    """Load CSV data and create visualization with two subfigures"""
    
    median_pq = handshake_time_pq.apply(lambda x: x.median(), axis=1)
    median_trad = handshake_time_trad.apply(lambda x: x.median(), axis=1)

    percentile_95_pq = handshake_time_pq.apply(lambda x: x.quantile(0.95), axis=1)
    percentile_95_trad = handshake_time_trad.apply(lambda x: x.quantile(0.95), axis=1)

    # Create two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    if type == 'kex':
        # Plot medians in first subplot
        ax1.plot(pkt_loss, median_pq, label=KEX_ALG[0], color='blue')
        ax1.plot(pkt_loss, median_trad, label=KEX_ALG[1], color='red')
        ax1.set_xlabel('Packet Loss (%)')
        ax1.set_ylabel('Handshake Time (ms)')
        ax1.set_title(f'Median Handshake Time vs Packet Loss - RTT: {label}')
        ax1.grid(True)
        ax1.legend(prop={'size': 12})
        
        # Plot 95th percentiles in second subplot
        ax2.plot(pkt_loss, percentile_95_pq, label=KEX_ALG[0], color='blue')
        ax2.plot(pkt_loss, percentile_95_trad, label=KEX_ALG[1], color='red')
        ax2.set_xlabel('Packet Loss (%)')
        ax2.set_ylabel('Handshake Time (ms)')
        ax2.set_title(f'95th Percentile Handshake Time vs Packet Loss - RTT: {label}')
        ax2.grid(True)
        ax2.legend(prop={'size': 12})
        
        plt.tight_layout()
    
    elif type == 'sig':
        # Plot medians in first subplot
        ax1.plot(pkt_loss, median_pq, label=SIG_ALG[0], color='blue')
        ax1.plot(pkt_loss, median_trad, label=SIG_ALG[1], color='red')
        ax1.set_xlabel('Packet Loss (%)')
        ax1.set_ylabel('Handshake Time (ms)')
        ax1.set_title(f'Median Handshake Time vs Packet Loss - RTT: {label}')
        ax1.grid(True)
        ax1.legend(prop={'size': 12})
        
        # Plot 95th percentiles in second subplot
        ax2.plot(pkt_loss, percentile_95_pq, label=SIG_ALG[0], color='blue')
        ax2.plot(pkt_loss, percentile_95_trad, label=SIG_ALG[1], color='red')
        ax2.set_xlabel('Packet Loss (%)')
        ax2.set_ylabel('Handshake Time (ms)')
        ax2.set_title(f'95th Percentile Handshake Time vs Packet Loss - RTT: {label}')
        ax2.grid(True)
        ax2.legend(prop={'size': 12})

    return plt

def save_plot(plt, output_filename):
    """
    Save the plot to a file
    
    Args:
        plt: matplotlib plot object
        output_filename (str): Name of the output file
    """


    output_path = Path(__file__).parent.parent.parent / 'mn_data' / 'plots' / output_filename
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path)
    plt.close()


KEX_RTT = ['6p164ms', '31p749ms', '79p188ms', '196p425ms', '596p551ms'] # ms
SIG_RTT_D = ['6p306ms', '31p844ms', '79p216ms', '196p489ms'] # ms
SIG_RTT_E = ['6p282ms', '31p702ms', '79p217ms', '196p182ms']

DATA_FILE = '../../mn_data'

if __name__ == '__main__':
    # KEX Plot
    for rtt in KEX_RTT:
        df_kyber = None
        df_prime = None
        for kex in KEX_ALG:
            if kex == 'p256_kyber512_90s':
                df_kyber = pd.read_csv(f'{DATA_FILE}/kex/{kex}_{rtt}.csv')
            else:
                df_prime = pd.read_csv(f'{DATA_FILE}/kex/{kex}_{rtt}.csv')
    
    
        # Separate packet loss and data columns
        packet_loss = df_prime.iloc[:, 0] if len(df_kyber.iloc[:, 0]) >= len(df_prime.iloc[:, 0]) else df_kyber.iloc[:, 0]
        handshake_time_kyber = df_kyber.iloc[: len(packet_loss), 1:]  # All other columns are data
        handshake_time_prime = df_prime.iloc[: len(packet_loss), 1:]  # All other columns are data
        
        # Create plot
        plt.figure(figsize=(10, 10))  # Made taller to accommodate two subplots
        
        plot_data(packet_loss, handshake_time_kyber, handshake_time_prime, type='kex', label=f'{rtt}')
        
        # Save plot
        output_filename = f'kex_{rtt}_plot.png'
        save_plot(plt, output_filename)

    # SIG Plot
    for i in range(len(SIG_RTT_D)):

        df_dilithium = None
        df_ecdsa = None

        for sig in SIG_ALG:
            if sig == 'dilithium2':
                rtt = SIG_RTT_D[i]
                df_dilithium = pd.read_csv(f'{DATA_FILE}/sig/{sig}_{rtt}.csv')
            else:
                rtt = SIG_RTT_E[i]
                df_ecdsa = pd.read_csv(f'{DATA_FILE}/sig/{sig}_{rtt}.csv')
        
        # Separate packet loss and data columns
        packet_loss = df_ecdsa.iloc[:, 0] if len(df_dilithium.iloc[:, 0]) >= len(df_ecdsa.iloc[:, 0]) else df_dilithium.iloc[:, 0]
        handshake_time_dilithium = df_dilithium.iloc[: len(packet_loss), 1:]  # All other columns are data
        handshake_time_ecdsa = df_ecdsa.iloc[: len(packet_loss), 1:]  # All other columns are data
        
        # Create plot
        plt.figure(figsize=(10, 10))  # Made taller to accommodate two subplots
        
        plot_data(packet_loss, handshake_time_dilithium, handshake_time_ecdsa, type='sig', label=f'{rtt}')
        
        # Save plot
        rtt = SIG_RTT_D[i]
        output_filename = f'sig_{rtt}_plot.png'
        save_plot(plt, output_filename)


