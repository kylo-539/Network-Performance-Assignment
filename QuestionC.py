"""
Network Performance EEN1058
Author: Kyle Sheehy
Date: October 2025

This script processes multiple OMNeT++ scalar results (.sca) files to calculate key network performance metrics 
for varying distances and users for both Wi-Fi 6 and Wi-Fi 7. A comprehensive analysis and visualisations are provided.

Metrics calculated:
- Average throughput (Kbps)
- Average delay (ms)
- Packet loss ratio (PLR)

The script also generates individual plot visualisations for each metric.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Configuration - Dictionary of files to process
Wifi6_0m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-0m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-0m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-0m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-0m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi6_30m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-30m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-30m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-30m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-30m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi6_60m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-60m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-60m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-60m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-60m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi6_90m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-90m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-90m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-90m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-90m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi6_120m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-120m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-120m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-120m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-120m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi6_150m = { 
    "users_1": "QuestionC/Wifi6/DataOfUser1-run-1763041112-150m-1users-WiFi6_80211ax-run-1763041112.sca",
    "users_10": "QuestionC/Wifi6/DataOfUser1-run-1763041112-150m-10users-WiFi6_80211ax-run-1763041112.sca",
    "users_20": "QuestionC/Wifi6/DataOfUser1-run-1763041112-150m-20users-WiFi6_80211ax-run-1763041112.sca",
    "users_50": "QuestionC/Wifi6/DataOfUser1-run-1763041112-150m-50users-WiFi6_80211ax-run-1763041112.sca",
}

Wifi7_0m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-0m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-0m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-0m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-0m-50users-WiFi7_80211be-run-1763041112.sca",
}

Wifi7_30m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-30m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-30m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-30m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-30m-50users-WiFi7_80211be-run-1763041112.sca",
}

Wifi7_60m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-60m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-60m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-60m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-60m-50users-WiFi7_80211be-run-1763041112.sca",
}

Wifi7_90m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-90m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-90m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-90m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-90m-50users-WiFi7_80211be-run-1763041112.sca",
}

Wifi7_120m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-120m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-120m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-120m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-120m-50users-WiFi7_80211be-run-1763041112.sca",
}

Wifi7_150m = { 
    "users_1": "QuestionC/Wifi7/DataOfUser1-run-1763041112-150m-1users-WiFi7_80211be-run-1763041112.sca",
    "users_10": "QuestionC/Wifi7/DataOfUser1-run-1763041112-150m-10users-WiFi7_80211be-run-1763041112.sca",
    "users_20": "QuestionC/Wifi7/DataOfUser1-run-1763041112-150m-20users-WiFi7_80211be-run-1763041112.sca",
    "users_50": "QuestionC/Wifi7/DataOfUser1-run-1763041112-150m-50users-WiFi7_80211be-run-1763041112.sca",
}

simTime = 20.0  # Simulation time in seconds

# Organized data structures for systematic analysis
WIFI_SCENARIOS = {
    "WiFi6": {
        "0m": Wifi6_0m,
        "30m": Wifi6_30m,
        "60m": Wifi6_60m,
        "90m": Wifi6_90m,
        "120m": Wifi6_120m,
        "150m": Wifi6_150m,
    }, 
    "WiFi7": {
        "0m": Wifi7_0m,
        "30m": Wifi7_30m,
        "60m": Wifi7_60m,
        "90m": Wifi7_90m,
        "120m": Wifi7_120m,
        "150m": Wifi7_150m,
    }
}

DISTANCES = ["0m", "30m", "60m", "90m", "120m", "150m"]
USER_COUNTS = ["users_1", "users_10", "users_20", "users_50"]

def parse_sca_file(filename):
    """
    Parse OMNeT++ scalar results file (.sca) and extract network performance data.
    
    Args:
        filename (str): Path to the .sca file
        
    Returns:
        dict: Dictionary containing parsed network metrics
    """
    data = defaultdict(dict)
    
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
        print(f"Warning: File '{filename}' not found!")
        return None
    except Exception as e:
        print(f"Error parsing file '{filename}': {e}")
        return None
    
    return dict(data)

def calculate_metrics_for_scenario(data, wifi_type, distance, user_count):
    """
    Calculate network performance metrics for a single scenario.
    
    Args:
        data (dict): Parsed network data from .sca file
        wifi_type (str): WiFi type ("WiFi6" or "WiFi7")
        distance (str): Distance (e.g., "0m", "30m")
        user_count (str): User count (e.g., "users_1", "users_10")
        
    Returns:
        dict: Dictionary containing calculated metrics
    """
    if data is None:
        return None
        
    try:
        # Extract key values from the parsed data
        # tx from node[0], rx from node[1] (correct node assignment)
        tx_packets = data.get('node[0]', {}).get('sender-tx-packets', 0)
        rx_packets = data.get('node[1]', {}).get('receiver-rx-packets', 0)
        
        # Packet size statistics
        avg_packet_size = data.get('statistics', {}).get('mean', 1000)  # bytes
        
        # Delay statistics (in nanoseconds) - read from correct location
        delay_average = data.get('.', {}).get('delay-average', 0)
        
        # Calculate Average Throughput (Kbps)
        # Throughput = (Successfully received bits) / (Total time)
        total_bits_received = rx_packets * avg_packet_size * 8  # Convert bytes to bits
        avg_throughput_kbps = (total_bits_received / simTime) / 1000
        
        # Calculate Average Delay (ms)
        # Convert from nanoseconds to milliseconds
        avg_delay_ms = delay_average / 1000000 if delay_average > 0 else 0
        
        # Calculate Packet Loss Ratio (PLR)
        if tx_packets > 0:
            packet_loss_ratio = (tx_packets - rx_packets) / tx_packets
        else:
            packet_loss_ratio = 0
        
        # Extract numeric values for analysis
        distance_numeric = int(distance.replace('m', ''))
        user_numeric = int(user_count.replace('users_', ''))
        
        return {
            'wifi_type': wifi_type,
            'distance': distance,
            'distance_numeric': distance_numeric,
            'user_count': user_count,        # Keep string for plotting filters
            'user_numeric': user_numeric,
            'avg_throughput_kbps': avg_throughput_kbps,
            'avg_delay_ms': avg_delay_ms,
            'packet_loss_ratio': packet_loss_ratio,
            'tx_packets': tx_packets,
            'rx_packets': rx_packets,
            'avg_packet_size_bytes': avg_packet_size
        }
        
    except Exception as e:
        print(f"Error calculating metrics for {wifi_type} {distance} {user_count}: {e}")
        return None

def process_all_scenarios():
    """
    Process all WiFi scenarios and calculate metrics for each.
    
    Returns:
        list: List of dictionaries containing metrics for each scenario
    """
    print("Starting comprehensive WiFi 6 vs WiFi 7 analysis")
    print("=" * 70)
    
    results = []
    total_scenarios = len(WIFI_SCENARIOS) * len(DISTANCES) * len(USER_COUNTS)
    current_scenario = 0
    
    for wifi_type, distance_dict in WIFI_SCENARIOS.items():
        print(f"\nProcessing {wifi_type} scenarios...")
        
        for distance, user_dict in distance_dict.items():
            for user_count, filename in user_dict.items():
                current_scenario += 1
                print(f"  [{current_scenario}/{total_scenarios}] {wifi_type} - {distance} - {user_count}")
                
                # Parse the file
                parsed_data = parse_sca_file(filename)
                
                # Calculate metrics
                metrics = calculate_metrics_for_scenario(parsed_data, wifi_type, distance, user_count)
                
                if metrics:
                    results.append(metrics)
                    print(f"    Throughput: {metrics['avg_throughput_kbps']:.1f} Kbps, "
                          f"Delay: {metrics['avg_delay_ms']:.2f} ms, "
                          f"PLR: {metrics['packet_loss_ratio']:.4f}")
                else:
                    print(f"    Failed to process scenario")
    
    return results

def create_summary_dataframe(results):
    """
    Create a pandas DataFrame with comprehensive analysis.
    
    Args:
        results (list): List of metric dictionaries
        
    Returns:
        pandas.DataFrame: DataFrame containing all metrics
    """
    df = pd.DataFrame(results)
    
    # Add percentage PLR column
    df['packet_loss_percentage'] = df['packet_loss_ratio'] * 100
    
    # Sort by WiFi type, distance, and user count
    df = df.sort_values(['wifi_type', 'distance_numeric', 'user_numeric'])
    
    return df

def print_comprehensive_summary(df):
    """
    Print a comprehensive text summary of the WiFi 6 vs WiFi 7 analysis.
    
    Args:
        df (pandas.DataFrame): DataFrame containing metrics
    """
    print("\n" + "=" * 100)
    print("COMPREHENSIVE WiFi 6 vs WiFi 7 PERFORMANCE ANALYSIS")
    print("=" * 100)
    print(f"Simulation Duration: {simTime} seconds")
    print(f"Total Scenarios Analyzed: {len(df)}")
    print(f"WiFi Technologies: WiFi 6, WiFi 7")
    print(f"Distances Tested: {', '.join(DISTANCES)}")
    print(f"User Counts: 1, 10, 20, 50 users")
    
    # Summary by WiFi type
    for wifi_type in ["WiFi6", "WiFi7"]:
        wifi_data = df[df['wifi_type'] == wifi_type]
        print(f"\n{wifi_type} PERFORMANCE SUMMARY:")
        print("-" * 50)
        print(f"Average Throughput: {wifi_data['avg_throughput_kbps'].mean():.2f} Kbps")
        print(f"Average Delay: {wifi_data['avg_delay_ms'].mean():.2f} ms")
        print(f"Average PLR: {wifi_data['packet_loss_percentage'].mean():.3f}%")
        print(f"Max Throughput: {wifi_data['avg_throughput_kbps'].max():.2f} Kbps")
        print(f"Min Throughput: {wifi_data['avg_throughput_kbps'].min():.2f} Kbps")
    
    # Comparative analysis
    wifi6_data = df[df['wifi_type'] == 'WiFi6']
    wifi7_data = df[df['wifi_type'] == 'WiFi7']
    
    print(f"\nCOMPARATIVE ANALYSIS:")
    print("-" * 40)
    throughput_improvement = ((wifi7_data['avg_throughput_kbps'].mean() - 
                              wifi6_data['avg_throughput_kbps'].mean()) / 
                             wifi6_data['avg_throughput_kbps'].mean()) * 100
    
    delay_improvement = ((wifi6_data['avg_delay_ms'].mean() - 
                         wifi7_data['avg_delay_ms'].mean()) / 
                        wifi6_data['avg_delay_ms'].mean()) * 100
    
    plr_improvement = ((wifi6_data['packet_loss_percentage'].mean() - 
                       wifi7_data['packet_loss_percentage'].mean()) / 
                      wifi6_data['packet_loss_percentage'].mean()) * 100
    
    print(f"WiFi 7 Throughput Improvement: {throughput_improvement:+.1f}%")
    print(f"WiFi 7 Delay Improvement: {delay_improvement:+.1f}%")
    print(f"WiFi 7 PLR Improvement: {plr_improvement:+.1f}%")

def create_comparative_visualizations(df):
    """
    Create comprehensive comparative visualizations for WiFi 6 vs WiFi 7.
    
    Args:
        df (pandas.DataFrame): DataFrame containing metrics
    """
    print("\nCreating comparative visualizations...")
    
    # Set up plotting style
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (15, 12)
    plt.rcParams['font.size'] = 11
    
    # Color schemes
    wifi6_color = '#1f77b4'  # Blue
    wifi7_color = '#ff7f0e'  # Orange
    
    # Create individual plots for each metric
    
    # 1. Throughput Analysis
    plt.figure(figsize=(15, 10))
    
    # Plot by distance for each user count
    for i, user_count in enumerate(['users_1', 'users_10', 'users_20', 'users_50']):
        plt.subplot(2, 2, i+1)
        
        # Filter data for current user count
        wifi6_subset = df[(df['wifi_type'] == 'WiFi6') & (df['user_count'] == user_count)]
        wifi7_subset = df[(df['wifi_type'] == 'WiFi7') & (df['user_count'] == user_count)]
        
        # Plot lines
        plt.plot(wifi6_subset['distance_numeric'], wifi6_subset['avg_throughput_kbps'], 
                'o-', color=wifi6_color, linewidth=2, markersize=6, label='WiFi 6')
        plt.plot(wifi7_subset['distance_numeric'], wifi7_subset['avg_throughput_kbps'], 
                's-', color=wifi7_color, linewidth=2, markersize=6, label='WiFi 7')
        
        plt.xlabel('Distance (m)')
        plt.ylabel('Throughput (Kbps)')
        plt.title(f'Throughput vs Distance - {user_count.replace("_", " ").title()}')
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.suptitle('WiFi 6 vs WiFi 7: Throughput Performance Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('QuestionC-Throughput-Analysis-WiFi6-vs-WiFi7.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Delay Analysis
    plt.figure(figsize=(15, 10))
    
    for i, user_count in enumerate(['users_1', 'users_10', 'users_20', 'users_50']):
        plt.subplot(2, 2, i+1)
        
        wifi6_subset = df[(df['wifi_type'] == 'WiFi6') & (df['user_count'] == user_count)]
        wifi7_subset = df[(df['wifi_type'] == 'WiFi7') & (df['user_count'] == user_count)]
        
        plt.plot(wifi6_subset['distance_numeric'], wifi6_subset['avg_delay_ms'], 
                'o-', color=wifi6_color, linewidth=2, markersize=6, label='WiFi 6')
        plt.plot(wifi7_subset['distance_numeric'], wifi7_subset['avg_delay_ms'], 
                's-', color=wifi7_color, linewidth=2, markersize=6, label='WiFi 7')
        
        plt.xlabel('Distance (m)')
        plt.ylabel('Average Delay (ms)')
        plt.title(f'Delay vs Distance - {user_count.replace("_", " ").title()}')
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.suptitle('WiFi 6 vs WiFi 7: Delay Performance Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('QuestionC-Delay-Analysis-WiFi6-vs-WiFi7.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. PLR Analysis
    plt.figure(figsize=(15, 10))
    
    for i, user_count in enumerate(['users_1', 'users_10', 'users_20', 'users_50']):
        plt.subplot(2, 2, i+1)
        
        wifi6_subset = df[(df['wifi_type'] == 'WiFi6') & (df['user_count'] == user_count)]
        wifi7_subset = df[(df['wifi_type'] == 'WiFi7') & (df['user_count'] == user_count)]
        
        plt.plot(wifi6_subset['distance_numeric'], wifi6_subset['packet_loss_percentage'], 
                'o-', color=wifi6_color, linewidth=2, markersize=6, label='WiFi 6')
        plt.plot(wifi7_subset['distance_numeric'], wifi7_subset['packet_loss_percentage'], 
                's-', color=wifi7_color, linewidth=2, markersize=6, label='WiFi 7')
        
        plt.xlabel('Distance (m)')
        plt.ylabel('Packet Loss Ratio (%)')
        plt.title(f'PLR vs Distance - {user_count.replace("_", " ").title()}')
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.suptitle('WiFi 6 vs WiFi 7: Packet Loss Ratio Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('QuestionC-PLR-Analysis-WiFi6-vs-WiFi7.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_side_by_side_distance_comparisons(df):
    """
    Create side-by-side comparisons for each distance, showing WiFi 6 vs WiFi 7
    performance for all user counts at that specific distance.
    
    Args:
        df (pandas.DataFrame): DataFrame containing metrics
    """
    print("\nCreating side-by-side distance comparison visualizations...")
    
    # Set up plotting style
    plt.style.use('default')
    plt.rcParams['font.size'] = 10
    
    # Color schemes
    wifi6_color = '#1f77b4'  # Blue
    wifi7_color = '#ff7f0e'  # Orange
    
    distances = sorted(df['distance_numeric'].unique())
    user_counts = sorted(df['user_numeric'].unique())
    
    # 1. Throughput Comparison for Each Distance
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('WiFi 6 vs WiFi 7: Throughput Comparison at Each Distance', 
                 fontsize=16, fontweight='bold')
    
    for i, distance in enumerate(distances):
        ax = axes[i//3, i%3]
        
        distance_data = df[df['distance_numeric'] == distance]
        wifi6_data = distance_data[distance_data['wifi_type'] == 'WiFi6'].sort_values('user_numeric')
        wifi7_data = distance_data[distance_data['wifi_type'] == 'WiFi7'].sort_values('user_numeric')
        
        # Create bar positions
        x = np.arange(len(user_counts))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar(x - width/2, wifi6_data['avg_throughput_kbps'], width, 
                      label='WiFi 6', color=wifi6_color, alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, wifi7_data['avg_throughput_kbps'], width, 
                      label='WiFi 7', color=wifi7_color, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar, value in zip(bars1, wifi6_data['avg_throughput_kbps']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi6_data['avg_throughput_kbps'])*0.01,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        for bar, value in zip(bars2, wifi7_data['avg_throughput_kbps']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi7_data['avg_throughput_kbps'])*0.01,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Customize subplot
        ax.set_xlabel('Number of Users', fontweight='bold')
        ax.set_ylabel('Throughput (Kbps)', fontweight='bold')
        ax.set_title(f'Throughput at {distance}m Distance', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'{u} users' for u in user_counts])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('QuestionC-SideBySide-Throughput-Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Delay Comparison for Each Distance
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('WiFi 6 vs WiFi 7: Delay Comparison at Each Distance', 
                 fontsize=16, fontweight='bold')
    
    for i, distance in enumerate(distances):
        ax = axes[i//3, i%3]
        
        distance_data = df[df['distance_numeric'] == distance]
        wifi6_data = distance_data[distance_data['wifi_type'] == 'WiFi6'].sort_values('user_numeric')
        wifi7_data = distance_data[distance_data['wifi_type'] == 'WiFi7'].sort_values('user_numeric')
        
        x = np.arange(len(user_counts))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, wifi6_data['avg_delay_ms'], width, 
                      label='WiFi 6', color=wifi6_color, alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, wifi7_data['avg_delay_ms'], width, 
                      label='WiFi 7', color=wifi7_color, alpha=0.8, edgecolor='black')
        
        # Add value labels
        for bar, value in zip(bars1, wifi6_data['avg_delay_ms']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi6_data['avg_delay_ms'])*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        for bar, value in zip(bars2, wifi7_data['avg_delay_ms']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi7_data['avg_delay_ms'])*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Number of Users', fontweight='bold')
        ax.set_ylabel('Average Delay (ms)', fontweight='bold')
        ax.set_title(f'Delay at {distance}m Distance', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'{u} users' for u in user_counts])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('QuestionC-SideBySide-Delay-Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. PLR Comparison for Each Distance
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('WiFi 6 vs WiFi 7: Packet Loss Ratio Comparison at Each Distance', 
                 fontsize=16, fontweight='bold')
    
    for i, distance in enumerate(distances):
        ax = axes[i//3, i%3]
        
        distance_data = df[df['distance_numeric'] == distance]
        wifi6_data = distance_data[distance_data['wifi_type'] == 'WiFi6'].sort_values('user_numeric')
        wifi7_data = distance_data[distance_data['wifi_type'] == 'WiFi7'].sort_values('user_numeric')
        
        x = np.arange(len(user_counts))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, wifi6_data['packet_loss_percentage'], width, 
                      label='WiFi 6', color=wifi6_color, alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, wifi7_data['packet_loss_percentage'], width, 
                      label='WiFi 7', color=wifi7_color, alpha=0.8, edgecolor='black')
        
        # Add value labels
        for bar, value in zip(bars1, wifi6_data['packet_loss_percentage']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi6_data['packet_loss_percentage'])*0.02,
                   f'{value:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        for bar, value in zip(bars2, wifi7_data['packet_loss_percentage']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(wifi7_data['packet_loss_percentage'])*0.02,
                   f'{value:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Number of Users', fontweight='bold')
        ax.set_ylabel('Packet Loss Ratio (%)', fontweight='bold')
        ax.set_title(f'PLR at {distance}m Distance', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'{u} users' for u in user_counts])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('QuestionC-SideBySide-PLR-Comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    Main function to orchestrate the comprehensive WiFi 6 vs WiFi 7 analysis.
    """
    # Process all scenarios
    results = process_all_scenarios()
    
    if not results:
        print("No valid results obtained. Exiting...")
        return
    
    # Create comprehensive DataFrame
    df = create_summary_dataframe(results)
    
    # Print comprehensive summary
    print_comprehensive_summary(df)
    
    # Create original comparative visualizations (user-based)
    create_comparative_visualizations(df)
    
    # Create new side-by-side distance comparisons
    create_side_by_side_distance_comparisons(df)
    
    # Save results to CSV
    df.to_csv('QuestionC-WiFi6-vs-WiFi7-Analysis.csv', index=False)
    
    print("\nAnalysis complete!")
    print("\nGenerated files:")
    print("- QuestionC-Throughput-Analysis-WiFi6-vs-WiFi7.png")
    print("- QuestionC-Delay-Analysis-WiFi6-vs-WiFi7.png") 
    print("- QuestionC-PLR-Analysis-WiFi6-vs-WiFi7.png")
    print("- QuestionC-SideBySide-Throughput-Comparison.png")
    print("- QuestionC-SideBySide-Delay-Comparison.png")
    print("- QuestionC-SideBySide-PLR-Comparison.png")
    print("- QuestionC-WiFi6-vs-WiFi7-Analysis.csv")

    # Execute the analysis
if __name__ == "__main__":
    main()