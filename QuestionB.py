"""
Network Performance EEN1058
Author: Kyle Sheehy
Date: October 2025

This script processes multiple OMNeT++ scalar results (.sca) files to calculate key network performance metrics 
for varying distances and provides comprehensive analysis and visualisation.

Metrics calculated:
- Average throughput (Kbps)
- Average delay (ms)
- Packet loss ratio (PLR)

The script also generates individual plot visualisations for each metric vs distance.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Configuration - Dictionary of files to process
original_files_dictionary = { # original bit rate of 160kbps
    "0m": "QuestionB-Original-Sim/DataOfUser1-1759412866-0m-.sca",
    "10m": "QuestionB-Original-Sim/DataOfUser1-1759413106-10m-.sca",
    "20m": "QuestionB-Original-Sim/DataOfUser1-1759413111-20m-.sca",
    "30m": "QuestionB-Original-Sim/DataOfUser1-1759413115-30m-.sca",
    "40m": "QuestionB-Original-Sim/DataOfUser1-1759413119-40m-.sca",
    "50m": "QuestionB-Original-Sim/DataOfUser1-1759407075-default-.sca",
    #"60m": "QuestionB-Original-Sim/DataOfUser1-1759414176-60m-.sca" # File before tx power change
    "60m": "QuestionB-Original-Sim/DataOfUser1-1759415401-60m-.sca",
    "70m": "QuestionB-Original-Sim/DataOfUser1-1759415506-70m-.sca",
    "80m": "QuestionB-Original-Sim/DataOfUser1-1759415511-80m-.sca",
    "90m": "QuestionB-Original-Sim/DataOfUser1-1759415513-90m-.sca",
    "100m": "QuestionB-Original-Sim/DataOfUser1-1759415516-100m-.sca",
    "110m": "QuestionB-Original-Sim/DataOfUser1-1759415689-110m-.sca",
    "120m": "QuestionB-Original-Sim/DataOfUser1-1759415691-120m-.sca",
    "130m": "QuestionB-Original-Sim/DataOfUser1-1759415693-130m-.sca",
    "140m": "QuestionB-Original-Sim/DataOfUser1-1759415695-140m-.sca",
    "150m": "QuestionB-Original-Sim/DataOfUser1-1759415697-150m-.sca",
    # "160m": "QuestionB-Original-Sim/DataOfUser1-1759415701-160m-.sca" # File before second tx power change
    "160m": "QuestionB-Original-Sim/DataOfUser1-1759416980-160m-.sca",
    "170m": "QuestionB-Original-Sim/DataOfUser1-1759416985-170m-.sca",
    "180m": "QuestionB-Original-Sim/DataOfUser1-1759416988-180m-.sca",
    "190m": "QuestionB-Original-Sim/DataOfUser1-1759417049-190m-.sca",
    "200m": "QuestionB-Original-Sim/DataOfUser1-1759417053-200m-.sca"
}


altered_files_dictionary = { # altered bit rate of 50Mbps, tx power 40.0
    "0m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-0m-.sca",
    "10m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-10m-.sca",
    "20m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-20m-.sca",
    "30m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-30m-.sca",
    "40m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-40m-.sca",
    "50m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-.sca",
    "60m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-60m-.sca",
    "70m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-70m-.sca",
    "80m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-80m-.sca",
    "90m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-90m-.sca",
    "100m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-100m-.sca",
    "110m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-110m-.sca",
    "120m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-120m-.sca",
    "130m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-130m-.sca",
    "140m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-140m-.sca",
    "150m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-150m-.sca",
    "160m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-160m-.sca",
    "170m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-170m-.sca",
    "180m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-180m-.sca",
    "190m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-190m-.sca",
    "200m": "QuestionB-Altered-Sim/DataOfUser1--50000kbps-200m-.sca"
}

# Simulation parameters
SIMULATION_TIME_SEC = 20.0  # Runtime is 20 seconds

def parse_sca_file(filename):
    """
    Parse OMNeT++ scalar results file (.sca) and extract network performance data.
    
    Args:
        filename (str): Path to the .sca file
        
    Returns:
        dict: Dictionary containing parsed network metrics
    """
    data = defaultdict(dict)
    
    print(f"Parsing trace file: {filename}")
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                
                # Parse scalar values
                if line.startswith('scalar'):
                    parts = line.split()
                    if len(parts) >= 4:
                        node = parts[1]
                        metric = parts[2]
                        value = parts[3]
                        
                        try:
                            # Convert to appropriate numeric type
                            if '.' in value or 'e' in value.lower():
                                data[node][metric] = float(value)
                            else:
                                data[node][metric] = int(value)
                        except ValueError:
                            data[node][metric] = value
                
                # Parse statistic fields (for packet size statistics)
                elif line.startswith('field'):
                    parts = line.split()
                    if len(parts) >= 3:
                        field_name = parts[1]
                        field_value = parts[2]
                        
                        try:
                            if '.' in field_value or 'e' in field_value.lower():
                                data['statistics'][field_name] = float(field_value)
                            else:
                                data['statistics'][field_name] = int(field_value)
                        except ValueError:
                            data['statistics'][field_name] = field_value
                            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None
    
    print("File parsed successfully!")
    return dict(data)

def calculate_metrics_for_file(data, distance_label):
    """
    Calculate network performance metrics for a single file.
    
    Args:
        data (dict): Parsed network data from .sca file
        distance_label (str): Label for the distance (e.g., "10m")
        
    Returns:
        dict: Dictionary containing calculated metrics
    """
    if data is None:
        return None
        
    try:
        # Extract key values from the parsed data
        tx_packets = data.get('node[0]', {}).get('sender-tx-packets', 0)
        rx_packets = data.get('node[1]', {}).get('receiver-rx-packets', 0)
        
        # Packet size statistics
        avg_packet_size = data.get('statistics', {}).get('mean', 1000)  # bytes
        
        # Delay statistics (in nanoseconds)
        delay_average = data.get('.', {}).get('delay-average', 0)
        
        # Calculate Average Throughput (Kbps)
        # Throughput = (Successfully received bits) / (Total time)
        total_bits_received = rx_packets * avg_packet_size * 8  # Convert bytes to bits
        avg_throughput_kbps = (total_bits_received / SIMULATION_TIME_SEC) / 1000
        
        # Calculate Average Delay (ms)
        # Convert from nanoseconds to milliseconds
        avg_delay_ms = delay_average / 1000000 if delay_average > 0 else 0
        
        # Calculate Packet Loss Ratio (PLR)
        if tx_packets > 0:
            packet_loss_ratio = (tx_packets - rx_packets) / tx_packets
        else:
            packet_loss_ratio = 0
        
        return {
            'distance_label': distance_label,
            'avg_throughput_kbps': avg_throughput_kbps,
            'avg_delay_ms': avg_delay_ms,
            'packet_loss_ratio': packet_loss_ratio,
            'tx_packets': tx_packets,
            'rx_packets': rx_packets,
            'avg_packet_size_bytes': avg_packet_size
        }
        
    except Exception as e:
        print(f"Error calculating metrics for {distance_label}: {e}")
        return None

def process_all_files():
    """
    Process all files in the dictionary and calculate metrics for each.
    
    Returns:
        list: List of dictionaries containing metrics for each file
    """
    print("Starting analysis")
    print("=" * 60)
    
    results = []
    
    for distance_label, filename in altered_files_dictionary.items(): # Change for altered / Original
        print(f"\nProcessing {distance_label} scenario...")
        
        # Parse the file
        parsed_data = parse_sca_file(filename)
        
        # Calculate metrics
        metrics = calculate_metrics_for_file(parsed_data, distance_label)
        
        if metrics:
            results.append(metrics)
            print(f"Throughput: {metrics['avg_throughput_kbps']:.2f} Kbps")
            print(f"Delay: {metrics['avg_delay_ms']:.2f} ms")
            print(f"PLR: {metrics['packet_loss_ratio']:.4f}")
        else:
            print(f"Failed to process {distance_label}")
    
    return results

def create_summary_dataframe(results):
    """
    Create a pandas DataFrame with summary statistics.
    
    Args:
        results (list): List of metric dictionaries
        
    Returns:
        pandas.DataFrame: DataFrame containing all metrics
    """
    df = pd.DataFrame(results)
    
    # Add percentage PLR column
    df['packet_loss_percentage'] = df['packet_loss_ratio'] * 100
    
    # Extract numeric distance values for sorting
    df['distance_numeric'] = df['distance_label'].str.extract(r'(\d+)').astype(int)
    df = df.sort_values('distance_numeric')
    
    return df

def print_text_summary(df):
    """
    Print a comprehensive text summary of the results.
    
    Args:
        df (pandas.DataFrame): DataFrame containing metrics
    """
    print("\n" + "=" * 80)
    print("NETWORK PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Simulation Duration: {SIMULATION_TIME_SEC} seconds")
    print(f"Number of Scenarios Analyzed: {len(df)}")
    
    print("\nDETAILED RESULTS BY DISTANCE:")
    print("-" * 80)
    print(f"{'Distance':<10} {'Throughput':<15} {'Delay':<12} {'PLR':<8} {'Tx Pkts':<8} {'Rx Pkts':<8}")
    print(f"{'(Label)':<10} {'(Kbps)':<15} {'(ms)':<12} {'(%)':<8} {'(#)':<8} {'(#)':<8}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        print(f"{row['distance_label']:<10} {row['avg_throughput_kbps']:<15.2f} "
              f"{row['avg_delay_ms']:<12.2f} {row['packet_loss_percentage']:<8.3f} "
              f"{row['tx_packets']:<8} {row['rx_packets']:<8}")
    
    print("\nSTATISTICAL SUMMARY:")
    print("-" * 40)
    print(f"Maximum Throughput: {df['avg_throughput_kbps'].max():.2f} Kbps")
    print(f"Minimum Throughput: {df['avg_throughput_kbps'].min():.2f} Kbps")
    
    print(f"\nAverage Delay: {df['avg_delay_ms'].mean():.2f} ms")
    print(f"Maximum Delay: {df['avg_delay_ms'].max():.2f} ms")
    print(f"Minimum Delay: {df['avg_delay_ms'].min():.2f} ms")
    print(f"Delay Std Dev: {df['avg_delay_ms'].std():.2f} ms")
    
    print(f"\nAverage PLR: {df['packet_loss_percentage'].mean():.3f}%")
    print(f"Maximum PLR: {df['packet_loss_percentage'].max():.3f}%")
    print(f"Minimum PLR: {df['packet_loss_percentage'].min():.3f}%")
    print(f"PLR Std Dev: {df['packet_loss_percentage'].std():.3f}%")

def create_visualisations(df):
    """
    Create individual visualisations for each network performance metric vs distance.
    
    Args:
        df (pandas.DataFrame): DataFrame containing metrics
    """
    print("\nCreating visualisations...")
    
    # Set up the plotting style
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    
    # Color scheme
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 1. Throughput vs Distance
    plt.figure(figsize=(10, 6))
    plt.plot(df['distance_numeric'], df['avg_throughput_kbps'], 'o-', 
             color=colors[0], linewidth=3, markersize=10, label='Throughput')
    plt.xlabel('Distance (m)', fontweight='bold', fontsize=14)
    plt.ylabel('Average Throughput (Kbps)', fontweight='bold', fontsize=14)
    plt.title('Network Throughput vs Distance', fontweight='bold', fontsize=16, pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Add value labels
    for i, row in df.iterrows():
        plt.annotate(f'{row["avg_throughput_kbps"]:.1f}', 
                    (row['distance_numeric'], row['avg_throughput_kbps']),
                    textcoords="offset points", xytext=(0,15), ha='center', fontsize=10)
    
    plt.tight_layout()
    #plt.savefig('QuestionB-ThroughputVsDistance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Delay vs Distance  
    plt.figure(figsize=(10, 6))
    plt.plot(df['distance_numeric'], df['avg_delay_ms'], 's-', 
             color=colors[1], linewidth=3, markersize=10, label='Average Delay')
    plt.xlabel('Distance (m)', fontweight='bold', fontsize=14)
    plt.ylabel('Average Delay (ms)', fontweight='bold', fontsize=14)
    plt.title('Network Delay vs Distance', fontweight='bold', fontsize=16, pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Add value labels
    for i, row in df.iterrows():
        plt.annotate(f'{row["avg_delay_ms"]:.2f}', 
                    (row['distance_numeric'], row['avg_delay_ms']),
                    textcoords="offset points", xytext=(0,15), ha='center', fontsize=10)
    
    plt.tight_layout()
    #plt.savefig('QuestionB-DelayVsDistance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Packet Loss Ratio vs Distance
    plt.figure(figsize=(10, 6))
    plt.plot(df['distance_numeric'], df['packet_loss_percentage'], '^-', 
             color=colors[2], linewidth=3, markersize=10, label='Packet Loss Ratio')
    plt.xlabel('Distance (m)', fontweight='bold', fontsize=14)
    plt.ylabel('Packet Loss Ratio (%)', fontweight='bold', fontsize=14)
    plt.title('Packet Loss Ratio vs Distance', fontweight='bold', fontsize=16, pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Add value labels
    for i, row in df.iterrows():
        plt.annotate(f'{row["packet_loss_percentage"]:.3f}%', 
                    (row['distance_numeric'], row['packet_loss_percentage']),
                    textcoords="offset points", xytext=(0,15), ha='center', fontsize=10)
    
    plt.tight_layout()
    #plt.savefig('QuestionB-PLRVsDistance.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    Main function to orchestrate the multi-file network performance analysis.
    """
    # Process all files
    results = process_all_files()
    
    if not results:
        print("No valid results obtained. Exiting...")
        return
    
    # Create summary DataFrame
    df = create_summary_dataframe(results)
    
    # Print text summary
    print_text_summary(df)
    
    # Create visualisations
    create_visualisations(df)
    
    # Save results to CSV
    df.to_csv('QuestionB-DistanceAnalysis.csv', index=False)
    
    print("\nDistance-based analysis complete!")

# Execute the analysis
if __name__ == "__main__":
    main()
    