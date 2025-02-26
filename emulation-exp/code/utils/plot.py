import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

KEX_ALG = ['p256_kyber512_90s', 'p256_kyber768_90s', 'p256_kyber1024_90s', 'prime256v1']
SIG_ALG = ['dilithium2', 'dilithium3', 'ecdsap256']

def plot_data(pkt_loss, handshake_times_pq, handshake_time_trad, type, label=None):
    """Load CSV data and create visualization with separate plots for each algorithm"""
    
    # Calculate medians and percentiles for traditional
    median_trad = handshake_time_trad.apply(lambda x: x.median(), axis=1)
    percentile_95_trad = handshake_time_trad.apply(lambda x: x.quantile(0.95), axis=1)

    # Create figure with subplots for each PQ algorithm
    num_pq_algs = len(handshake_times_pq)
    fig, axes = plt.subplots(num_pq_algs, 2, figsize=(15, 5 * num_pq_algs))
    
    # Colors for PQ and traditional algorithms
    pq_color = 'blue'
    trad_color = 'red'

    if type == 'kex':
        # Plot each PQ algorithm in its own subplot
        for idx, handshake_time_pq in enumerate(handshake_times_pq):
            median_pq = handshake_time_pq.apply(lambda x: x.median(), axis=1)
            percentile_95_pq = handshake_time_pq.apply(lambda x: x.quantile(0.95), axis=1)
            
            # Print comparison results
            print(f"\n=== Results for {KEX_ALG[idx]} vs {KEX_ALG[-1]} - RTT: {label} ===")
            print("Packet Loss % | Median Diff % | 95th Percentile Diff %")
            print("-" * 50)
            median_diff_percent = ((median_pq - median_trad) / median_trad) * 100
            percentile_95_diff_percent = ((percentile_95_pq - percentile_95_trad) / percentile_95_trad) * 100
            for i, loss in enumerate(pkt_loss):
                print(f"{loss:11.1f} | {median_diff_percent[i]:11.1f} | {percentile_95_diff_percent[i]:20.1f}")

            # Plot median comparison
            for col in handshake_time_pq.columns:
                axes[idx, 0].scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color=pq_color, s=10)
            for col in handshake_time_trad.columns:
                axes[idx, 0].scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color=trad_color, s=10)
            
            axes[idx, 0].plot(pkt_loss, median_pq, label=KEX_ALG[idx], color=pq_color, 
                            linewidth=2, marker='o', markersize=8)
            axes[idx, 0].plot(pkt_loss, median_trad, label=KEX_ALG[-1], color=trad_color, 
                            linewidth=2, linestyle='--', marker='o', markersize=8)
            
            # Plot 95th percentile comparison
            for col in handshake_time_pq.columns:
                axes[idx, 1].scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color=pq_color, s=10)
            for col in handshake_time_trad.columns:
                axes[idx, 1].scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color=trad_color, s=10)
            
            axes[idx, 1].plot(pkt_loss, percentile_95_pq, label=KEX_ALG[idx], color=pq_color, 
                            linewidth=2, marker='o', markersize=8)
            axes[idx, 1].plot(pkt_loss, percentile_95_trad, label=KEX_ALG[-1], color=trad_color, 
                            linewidth=2, linestyle='--', marker='o', markersize=8)
            
            # Add labels and legends
            axes[idx, 0].set_title(f'Median Comparison: {KEX_ALG[idx]} vs {KEX_ALG[-1]}')
            axes[idx, 1].set_title(f'95th Percentile: {KEX_ALG[idx]} vs {KEX_ALG[-1]}')
            axes[idx, 0].legend()
            axes[idx, 1].legend()
            axes[idx, 0].set_xlabel('Packet Loss (%)')
            axes[idx, 1].set_xlabel('Packet Loss (%)')
            axes[idx, 0].set_ylabel('Handshake Time (ms)')
            axes[idx, 1].set_ylabel('Handshake Time (ms)')
            axes[idx, 0].grid(True)
            axes[idx, 1].grid(True)

            # Add y-axis limits after creating the plots
            max_median = max(max(median_pq), max(median_trad))
            max_95th = max(max(percentile_95_pq), max(percentile_95_trad))
            
            # Set y-axis limits with 10% padding
            axes[idx, 0].set_ylim(0, max_median * 1.1)
            axes[idx, 1].set_ylim(0, max_95th * 1.1)

    elif type == 'sig':
        # Similar structure for signature plots
        for idx, handshake_time_pq in enumerate(handshake_times_pq):
            median_pq = handshake_time_pq.apply(lambda x: x.median(), axis=1)
            percentile_95_pq = handshake_time_pq.apply(lambda x: x.quantile(0.95), axis=1)
            
            print(f"\n=== Results for {SIG_ALG[idx]} vs {SIG_ALG[-1]} - RTT: {label} ===")
            print("Packet Loss % | Median Diff % | 95th Percentile Diff %")
            print("-" * 50)
            median_diff_percent = ((median_pq - median_trad) / median_trad) * 100
            percentile_95_diff_percent = ((percentile_95_pq - percentile_95_trad) / percentile_95_trad) * 100
            for i, loss in enumerate(pkt_loss):
                print(f"{loss:11.1f} | {median_diff_percent[i]:11.1f} | {percentile_95_diff_percent[i]:20.1f}")

            # Plot median comparison
            for col in handshake_time_pq.columns:
                axes[idx, 0].scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color=pq_color, s=10)
            for col in handshake_time_trad.columns:
                axes[idx, 0].scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color=trad_color, s=10)
            
            axes[idx, 0].plot(pkt_loss, median_pq, label=SIG_ALG[idx], color=pq_color, 
                            linewidth=2, marker='o', markersize=8)
            axes[idx, 0].plot(pkt_loss, median_trad, label=SIG_ALG[-1], color=trad_color, 
                            linewidth=2, linestyle='--', marker='o', markersize=8)
            
            # Plot 95th percentile comparison
            for col in handshake_time_pq.columns:
                axes[idx, 1].scatter(pkt_loss, handshake_time_pq[col], alpha=0.05, color=pq_color, s=10)
            for col in handshake_time_trad.columns:
                axes[idx, 1].scatter(pkt_loss, handshake_time_trad[col], alpha=0.05, color=trad_color, s=10)
            
            axes[idx, 1].plot(pkt_loss, percentile_95_pq, label=SIG_ALG[idx], color=pq_color, 
                            linewidth=2, marker='o', markersize=8)
            axes[idx, 1].plot(pkt_loss, percentile_95_trad, label=SIG_ALG[-1], color=trad_color, 
                            linewidth=2, linestyle='--', marker='o', markersize=8)
            
            # Add labels and legends
            axes[idx, 0].set_title(f'Median Comparison: {SIG_ALG[idx]} vs {SIG_ALG[-1]}')
            axes[idx, 1].set_title(f'95th Percentile: {SIG_ALG[idx]} vs {SIG_ALG[-1]}')
            axes[idx, 0].legend()
            axes[idx, 1].legend()
            axes[idx, 0].set_xlabel('Packet Loss (%)')
            axes[idx, 1].set_xlabel('Packet Loss (%)')
            axes[idx, 0].set_ylabel('Handshake Time (ms)')
            axes[idx, 1].set_ylabel('Handshake Time (ms)')
            axes[idx, 0].grid(True)
            axes[idx, 1].grid(True)

            # Add y-axis limits after creating the plots
            max_median = max(max(median_pq), max(median_trad))
            max_95th = max(max(percentile_95_pq), max(percentile_95_trad))
            
            # Set y-axis limits with 10% padding
            axes[idx, 0].set_ylim(0, max_median * 1.1)
            axes[idx, 1].set_ylim(0, max_95th * 1.1)

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


KEX_RTT = ['6p158ms', '31p730ms', '79p220ms', '196p246ms', '596p386ms'] # ms
SIG_RTT_D2 = ['6p325ms', '31p723ms', '79p253ms', '196p327ms', '596p335ms'] # ms
SIG_RTT_D3 = ['6p331ms', '31p745ms', '79p240ms', '196p386ms', '596p309ms'] # ms
SIG_RTT_E = ['6p253ms', '31p733ms', '79p207ms', '196p264ms', '596p328ms']

DATA_FILE = '../../mn_data'

if __name__ == '__main__':
    # KEX Plot
    for rtt in KEX_RTT:
        df_kyber_list = []
        df_prime = None
        
        for kex in KEX_ALG:
            if kex != 'prime256v1':
                df_kyber_list.append(pd.read_csv(f'{DATA_FILE}/kex/{kex}_{rtt}.csv'))
            else:
                df_prime = pd.read_csv(f'{DATA_FILE}/kex/{kex}_{rtt}.csv')
        
        # Use the longest packet loss array
        packet_loss = df_prime.iloc[:, 0]
        for df in df_kyber_list:
            if len(df.iloc[:, 0]) > len(packet_loss):
                packet_loss = df.iloc[:, 0]
        
        # Prepare data frames
        handshake_times_kyber = [df.iloc[: len(packet_loss), 1:] for df in df_kyber_list]
        handshake_time_prime = df_prime.iloc[: len(packet_loss), 1:]
        
        plt.figure(figsize=(10, 10))
        plot_data(packet_loss, handshake_times_kyber, handshake_time_prime, type='kex', label=f'{rtt}')
        output_filename = f'kex_{rtt}_plot.png'
        save_plot(plt, output_filename)

    # SIG Plot
    for i in range(len(SIG_RTT_D2)):
        df_dilithium_list = []
        df_ecdsa = None
        rtt = SIG_RTT_D2[i]  # Use D2's RTT for the plot name

        for sig in SIG_ALG:
            if sig == 'dilithium2':
                df_dilithium_list.append(pd.read_csv(f'{DATA_FILE}/sig/{sig}_{SIG_RTT_D2[i]}.csv'))
            elif sig == 'dilithium3':
                df_dilithium_list.append(pd.read_csv(f'{DATA_FILE}/sig/{sig}_{SIG_RTT_D3[i]}.csv'))
            else:  # ecdsap256
                df_ecdsa = pd.read_csv(f'{DATA_FILE}/sig/{sig}_{SIG_RTT_E[i]}.csv')
        
        packet_loss = df_ecdsa.iloc[:, 0]
        for df in df_dilithium_list:
            if len(df.iloc[:, 0]) > len(packet_loss):
                packet_loss = df.iloc[:, 0]
        
        handshake_times_dilithium = [df.iloc[: len(packet_loss), 1:] for df in df_dilithium_list]
        handshake_time_ecdsa = df_ecdsa.iloc[: len(packet_loss), 1:]
        
        plt.figure(figsize=(10, 10))
        plot_data(packet_loss, handshake_times_dilithium, handshake_time_ecdsa, type='sig', label=f'{rtt}')
        output_filename = f'sig_{rtt}_plot.png'
        save_plot(plt, output_filename)


