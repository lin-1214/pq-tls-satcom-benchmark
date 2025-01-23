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

    # Calculate percentage differences
    median_diff_percent = ((median_pq - median_trad) / median_trad) * 100
    percentile_95_diff_percent = ((percentile_95_pq - percentile_95_trad) / percentile_95_trad) * 100

    # Print results
    print(f"\n=== Results for {type.upper()} - RTT: {label} ===")
    print("Packet Loss % | Median Diff % | 95th Percentile Diff %")
    print("-" * 50)
    for i, loss in enumerate(pkt_loss):
        print(f"{loss:11.1f} | {median_diff_percent[i]:11.1f} | {percentile_95_diff_percent[i]:20.1f}")

    # Create two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    if type == 'kex':
        # Plot scatter points with lower alpha
        for col in handshake_time_trad.columns:
            ax1.scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color='red', s=10)
        for col in handshake_time_pq.columns:
            ax1.scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color='blue', s=10)
            
        # Plot medians with dashed line for traditional
        ax1.plot(pkt_loss, median_trad, label=KEX_ALG[1], color='red', linewidth=2, linestyle='--', marker='o', markersize=8, fillstyle='none')
        ax1.plot(pkt_loss, median_trad, color='red', marker='o', markersize=5)
        ax1.plot(pkt_loss, median_pq, label=KEX_ALG[0], color='blue', linewidth=2, marker='o', markersize=8, fillstyle='none')
        ax1.plot(pkt_loss, median_pq, color='blue', marker='o', markersize=5)
        
        ax1.set_xlabel('Packet Loss (%)')
        ax1.set_ylabel('Handshake Time (ms)')
        ax1.set_title(f'Median Handshake Time vs Packet Loss - RTT: {label}')
        ax1.grid(True)
        ax1.legend(prop={'size': 12})
        ax1.set_ylim(0, 14000)
        
        # Do the same for 95th percentile plot
        for col in handshake_time_trad.columns:
            ax2.scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color='red', s=10)
        for col in handshake_time_pq.columns:
            ax2.scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color='blue', s=10)
            
        ax2.plot(pkt_loss, percentile_95_trad, label=KEX_ALG[1], color='red', linewidth=2, linestyle='--', marker='o', markersize=8)
        ax2.plot(pkt_loss, percentile_95_trad, color='red', marker='o', markersize=5)
        ax2.plot(pkt_loss, percentile_95_pq, label=KEX_ALG[0], color='blue', linewidth=2, marker='o', markersize=8)
        ax2.plot(pkt_loss, percentile_95_pq, color='blue', marker='o', markersize=5)

        ax2.set_xlabel('Packet Loss (%)')
        ax2.set_ylabel('Handshake Time (ms)')
        ax2.set_title(f'95th Percentile Handshake Time vs Packet Loss - RTT: {label}')
        ax2.grid(True)
        ax2.legend(prop={'size': 12})
        ax2.set_ylim(0, 14000)
        
    elif type == 'sig':
        # Similar updates for signature plots
        for col in handshake_time_pq.columns:
            ax1.scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color='blue', s=10)
        for col in handshake_time_trad.columns:
            ax1.scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color='red', s=10)
            
        ax1.plot(pkt_loss, median_trad, label=SIG_ALG[1], color='red', linewidth=2, linestyle='--', marker='o', markersize=8, fillstyle='none')
        ax1.plot(pkt_loss, median_trad, color='red', marker='o', markersize=5)
        ax1.plot(pkt_loss, median_pq, label=SIG_ALG[0], color='blue', linewidth=2, marker='o', markersize=8, fillstyle='none')
        ax1.plot(pkt_loss, median_pq, color='blue', marker='o', markersize=5)

        ax1.set_xlabel('Packet Loss (%)')
        ax1.set_ylabel('Handshake Time (ms)')
        ax1.set_title(f'Median Handshake Time vs Packet Loss - RTT: {label}')
        ax1.grid(True)
        ax1.legend(prop={'size': 12})
        ax1.set_ylim(0, 14000)
        
        for col in handshake_time_pq.columns:
            ax2.scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color='blue', s=10)
        for col in handshake_time_trad.columns:
            ax2.scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color='red', s=10)
            
        ax2.plot(pkt_loss, percentile_95_trad, label=SIG_ALG[1], color='red', linewidth=2, linestyle='--', marker='o', markersize=8)
        ax2.plot(pkt_loss, percentile_95_trad, color='red', marker='o', markersize=5)
        ax2.plot(pkt_loss, percentile_95_pq, label=SIG_ALG[0], color='blue', linewidth=2, marker='o', markersize=8)
        ax2.plot(pkt_loss, percentile_95_pq, color='blue', marker='o', markersize=5)

        ax2.set_xlabel('Packet Loss (%)')
        ax2.set_ylabel('Handshake Time (ms)')
        ax2.set_title(f'95th Percentile Handshake Time vs Packet Loss - RTT: {label}')
        ax2.grid(True)
        ax2.legend(prop={'size': 12})
        ax2.set_ylim(0, 14000)

    plt.tight_layout()
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


KEX_RTT = ['6p029ms', '31p654ms', '79p322ms', '196p246ms', '596p401ms'] # ms
SIG_RTT_D = ['6p464ms', '31p677ms', '79p294ms', '196p273ms', '600p335ms'] # ms
SIG_RTT_E = ['6p228ms', '31p904ms', '79p345ms', '196p503ms', '600p393ms']

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
        # packet_loss = df_prime.iloc[:, 0] if len(df_kyber.iloc[:, 0]) >= len(df_prime.iloc[:, 0]) else df_kyber.iloc[:, 0]
        handshake_time_dilithium = df_dilithium.iloc[: len(packet_loss), 1:]  # All other columns are data
        handshake_time_ecdsa = df_ecdsa.iloc[: len(packet_loss), 1:]  # All other columns are data
        
        # Create plot
        plt.figure(figsize=(10, 10))  # Made taller to accommodate two subplots
        
        plot_data(packet_loss, handshake_time_dilithium, handshake_time_ecdsa, type='sig', label=f'{rtt}')
        
        # Save plot
        rtt = SIG_RTT_D[i]
        output_filename = f'sig_{rtt}_plot.png'
        save_plot(plt, output_filename)


