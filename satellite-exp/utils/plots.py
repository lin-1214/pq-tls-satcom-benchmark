import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def compare_handshake_times(kyber_file, traditional_file):
    # Read the CSV files with no header
    kyber_data = pd.read_csv(kyber_file, header=None)
    traditional_data = pd.read_csv(traditional_file, header=None)

    # Prepare data for plotting - use the first row as data
    kyber_times = kyber_data.iloc[0].values.astype(float)
    traditional_times = traditional_data.iloc[0].values.astype(float)
    
    # Remove outliers using IQR method
    def remove_outliers(data):
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data >= lower_bound) & (data <= upper_bound)]
    
    kyber_times_clean = remove_outliers(kyber_times)
    traditional_times_clean = remove_outliers(traditional_times)
    
    print(f"Number of samples after outlier removal - Kyber: {len(kyber_times_clean)}, P-256: {len(traditional_times_clean)}")
    
    # Validate data
    if len(kyber_times_clean) == 0 or len(traditional_times_clean) == 0:
        raise ValueError("One or both input files contain no data")
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Use closer x-positions (0.8 and 1.2 instead of 1 and 2)
    x_positions = [0.8, 1.2]
    
    # Create scatter plot with smaller dots
    plt.scatter([x_positions[1]] * len(kyber_times_clean), kyber_times_clean, alpha=0.5, s=10, label='Kyber-512')
    plt.scatter([x_positions[0]] * len(traditional_times_clean), traditional_times_clean, alpha=0.5, s=10, label='P-256')
    
    # Add median and 95th percentile markers
    kyber_median = np.median(kyber_times_clean)
    kyber_p95 = np.percentile(kyber_times_clean, 95)
    trad_median = np.median(traditional_times_clean)
    trad_p95 = np.percentile(traditional_times_clean, 95)
    
    # Plot median lines and points
    plt.hlines([kyber_median], x_positions[1]-0.05, x_positions[1]+0.05, colors='red', label='Median')
    plt.hlines([trad_median], x_positions[0]-0.05, x_positions[0]+0.05, colors='red')
    
    # Plot 95th percentile lines and points
    plt.hlines([kyber_p95], x_positions[1]-0.05, x_positions[1]+0.05, colors='green', label='95th Percentile')
    plt.hlines([trad_p95], x_positions[0]-0.05, x_positions[0]+0.05, colors='green')
    
    # Customize plot
    plt.xticks(x_positions, ['P-256', 'Kyber-512'])
    plt.ylabel('Time (ms)')
    plt.title('Handshake Times: Kyber-512 vs P-256')
    plt.legend()
    
    # Adjust x-axis limits to zoom in on the data
    plt.xlim(0.5, 1.5)
    
    # Calculate and print statistics
    stats = {
        'Kyber-512': {
            'mean': kyber_times_clean.mean(),
            'median': np.median(kyber_times_clean),
            'std': kyber_times_clean.std(),
            'p95': np.percentile(kyber_times_clean, 95)
        },
        'P-256': {
            'mean': traditional_times_clean.mean(),
            'median': np.median(traditional_times_clean),
            'std': traditional_times_clean.std(),
            'p95': np.percentile(traditional_times_clean, 95)
        }
    }
    
    print("\nStatistics:")
    for algo, metrics in stats.items():
        print(f"\n{algo}:")
        print(f"Mean: {metrics['mean']:.3f} ms")
        print(f"Median: {metrics['median']:.3f} ms")
        print(f"Std Dev: {metrics['std']:.3f} ms")
        print(f"95th Percentile: {metrics['p95']:.3f} ms")
    
    return plt.gcf()

# Example usage:
if __name__ == "__main__":
    kyber_file = "../sat_data/kex/p256_kyber512_90s_696p944ms.csv"
    traditional_file = "../sat_data/kex/prime256v1_696p944ms.csv"
    fig = compare_handshake_times(kyber_file, traditional_file)

    if not os.path.exists("../sat_data/plots"):
        os.makedirs("../sat_data/plots")

    plt.savefig("../sat_data/plots/handshake_times_kex.png")
