"""
Network Performance EEN1058
Author: Kyle Sheehy
Date: October 2025

This script processes OMNeT++ scalar results (.sca) files to calculate key network performance metrics:
- Bit rate (Kbps) of data traffic
- Average throughput (Kbps)
- Average delay (seconds)
- Packet loss ratio (PLR)

The script generates 4 individual plots and 1 combined plot for comprehensive analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Configuration
filename = "QuestionA/DataOfUser1-1759407075-default-.sca"

def parse_sca_file(filename):
    """
    Parse OMNeT++ scalar results file (.sca) and extract network performance data.

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

def calculate_network_metrics(data):
    """
    Calculate key network performance metrics from parsed data.
    
    Args:
        data (dict): Parsed network data from .sca file
        
    Returns:
        dict: Dictionary containing calculated metrics
    """
    print("\nCalculating network performance metrics...")
    
    metrics = {}
    
    # Extract key values from the parsed data
    try:
        # Transmission data
        tx_packets = data.get('node[0]', {}).get('sender-tx-packets', 0)
        rx_packets = data.get('node[1]', {}).get('receiver-rx-packets', 0)
        
        # Packet size statistics
        avg_packet_size = data.get('statistics', {}).get('mean', 1000)  # bytes
        
        # Delay statistics (in nanoseconds)
        delay_average = data.get('.', {}).get('delay-average', 0)  # in nanoseconds
        delay_max = data.get('.', {}).get('delay-max', 0)
        delay_min = data.get('.', {}).get('delay-min', 0)
        
        print(f"   Transmitted packets: {tx_packets}")
        print(f"   Received packets: {rx_packets}")
        print(f"   Average packet size: {avg_packet_size} bytes")
        
        # Simulation parameters
        simulation_time_sec = 20.0
        
        # 1. Calculate Bit Rate (Kbps)
        # Bit rate = (Total bits transmitted) / (Total transmission time)
        total_bits_transmitted = tx_packets * avg_packet_size * 8  # Convert bytes to bits
        bit_rate_kbps = (total_bits_transmitted / simulation_time_sec) / 1000
        
        # 2. Calculate Average Throughput (Kbps)
        # Throughput = (Successfully received bits) / (Total time)
        total_bits_received = rx_packets * avg_packet_size * 8
        avg_throughput_kbps = (total_bits_received / simulation_time_sec) / 1000
        
        # 3. Calculate Delays (seconds)
        # Convert from nanoseconds to seconds
        avg_delay_seconds = delay_average / 1000000000 if delay_average > 0 else 0
        max_delay_seconds = delay_max / 1000000000 if delay_max > 0 else 0
        min_delay_seconds = delay_min / 1000000000 if delay_min > 0 else 0
        
        # 4. Calculate Packet Loss Ratio (PLR)
        # PLR = (Transmitted packets - Received packets) / Transmitted packets
        if tx_packets > 0:
            packet_loss_ratio = (tx_packets - rx_packets) / tx_packets
        else:
            packet_loss_ratio = 0
        
        # Store all calculated metrics
        metrics = {
            'bit_rate_kbps': bit_rate_kbps,
            'avg_throughput_kbps': avg_throughput_kbps,
            'avg_delay_seconds': avg_delay_seconds,
            'max_delay_seconds': max_delay_seconds,
            'min_delay_seconds': min_delay_seconds,
            'packet_loss_ratio': packet_loss_ratio,
            'tx_packets': tx_packets,
            'rx_packets': rx_packets,
            'simulation_time_sec': simulation_time_sec,
            'avg_packet_size_bytes': avg_packet_size
        }
        
        # Display calculated metrics
        print(f"\nNetwork Performance Metrics:")
        print(f"   Bit Rate: {bit_rate_kbps:.2f} Kbps")
        print(f"   Average Throughput: {avg_throughput_kbps:.2f} Kbps")
        print(f"   Average Delay: {avg_delay_seconds:.6f} seconds")
        print(f"   Max Delay: {max_delay_seconds:.6f} seconds")
        print(f"   Min Delay: {min_delay_seconds:.6f} seconds")
        print(f"   Packet Loss Ratio: {packet_loss_ratio:.6f}")
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None

def create_individual_plots(metrics):
    """
    Create 3 individual plots for the metrics.
    
    Args:
        metrics (dict): Dictionary containing calculated network metrics
    """
    print("\nCreating individual plots...")
    
    # Set plotting style
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    
    # 1. Bit Rate and Throughput on Same Graph
    plt.figure(figsize=(10, 6))
    categories = ['Bit Rate', 'Throughput']
    values = [metrics['bit_rate_kbps'], metrics['avg_throughput_kbps']]
    colors = ['#FF6B6B', '#4ECDC4']
    
    bars = plt.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    plt.title('Bit Rate vs Average Throughput', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Rate (Kbps)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value:.2f} Kbps', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add efficiency indicator
    efficiency = (metrics['avg_throughput_kbps'] / metrics['bit_rate_kbps']) * 100 if metrics['bit_rate_kbps'] > 0 else 0
    plt.text(0.5, max(values) * 0.8, f'Efficiency: {efficiency:.1f}%', 
             ha='center', va='center', fontsize=12, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('QuestionA-Part1-BitRate-Throughput.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Delay Analysis (Min, Average, Max)
    plt.figure(figsize=(10, 6))
    delay_categories = ['Min Delay', 'Average Delay', 'Max Delay']
    delay_values = [metrics['min_delay_seconds'], metrics['avg_delay_seconds'], metrics['max_delay_seconds']]
    delay_colors = ['#95E1A3', '#FFC107', '#FF5722']
    
    bars = plt.bar(delay_categories, delay_values, color=delay_colors, alpha=0.8, edgecolor='black', linewidth=2)
    plt.title('Network Delay Analysis (Min, Average, Max)', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Delay (seconds)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar, value in zip(bars, delay_values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(delay_values)*0.01,
                f'{value:.6f} s', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('QuestionA-Part1-Delay.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Packet Loss Ratio Plot
    plt.figure(figsize=(8, 6))
    plt.bar(['Packet Loss Ratio'], [metrics['packet_loss_ratio']], color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=2)
    plt.title('Packet Loss Ratio (PLR)', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('PLR (ratio)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value label
    plt.text(0, metrics['packet_loss_ratio'] + max(metrics['packet_loss_ratio']*0.02, 0.001), 
             f'{metrics["packet_loss_ratio"]:.6f}', 
             ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('QuestionA-Part1-PLR.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_combined_plot(metrics):
    """
    Create a combined plot showing all metrics together.
    
    Args:
        metrics (dict): Dictionary containing calculated network metrics
    """
    print("\nCreating combined plot...")
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Network Performance Analysis - All Metrics', fontsize=18, fontweight='bold', y=0.95)
    
    # 1. Bit Rate vs Throughput (Top Left)
    categories = ['Bit Rate', 'Throughput']
    values = [metrics['bit_rate_kbps'], metrics['avg_throughput_kbps']]
    colors = ['#FF6B6B', '#4ECDC4']
    
    bars1 = ax1.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_title('Bit Rate vs Throughput', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Rate (Kbps)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, value in zip(bars1, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add efficiency indicator
    efficiency = (metrics['avg_throughput_kbps'] / metrics['bit_rate_kbps']) * 100 if metrics['bit_rate_kbps'] > 0 else 0
    ax1.text(0.5, max(values) * 0.8, f'Efficiency: {efficiency:.1f}%', 
             ha='center', va='center', fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # 2. Delay Analysis (Top Right)
    delay_categories = ['Min', 'Avg', 'Max']
    delay_values = [metrics['min_delay_seconds'], metrics['avg_delay_seconds'], metrics['max_delay_seconds']]
    delay_colors = ['#95E1A3', '#FFC107', '#FF5722']
    
    bars2 = ax2.bar(delay_categories, delay_values, color=delay_colors, alpha=0.8, edgecolor='black', linewidth=2)
    ax2.set_title('Network Delay Analysis', fontsize=14, fontweight='bold', pad=15)
    ax2.set_ylabel('Delay (seconds)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, value in zip(bars2, delay_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(delay_values)*0.01,
                f'{value:.6f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 3. Packet Loss Ratio (Bottom Left)
    ax3.bar(['PLR'], [metrics['packet_loss_ratio']], color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=2)
    ax3.set_title('Packet Loss Ratio', fontsize=14, fontweight='bold', pad=15)
    ax3.set_ylabel('PLR (ratio)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # Add value label
    ax3.text(0, metrics['packet_loss_ratio'] + max(metrics['packet_loss_ratio']*0.02, 0.001), 
             f'{metrics["packet_loss_ratio"]:.6f}', 
             ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 4. Performance Summary (Bottom Right)
    ax4.axis('off')  # Turn off axis for text display
    
    # Create a summary text display
    summary_text = f"""NETWORK PERFORMANCE SUMMARY
{'='*40}

DATA TRANSMISSION:
• Bit Rate: {metrics['bit_rate_kbps']:.2f} Kbps
• Throughput: {metrics['avg_throughput_kbps']:.2f} Kbps
• Efficiency: {efficiency:.1f}%

DELAY CHARACTERISTICS:
• Min Delay: {metrics['min_delay_seconds']:.6f} s
• Avg Delay: {metrics['avg_delay_seconds']:.6f} s
• Max Delay: {metrics['max_delay_seconds']:.6f} s

PACKET STATISTICS:
• Transmitted: {metrics['tx_packets']} packets
• Received: {metrics['rx_packets']} packets
• PLR: {metrics['packet_loss_ratio']:.6f}

SIMULATION INFO:
• Packet Size: {metrics['avg_packet_size_bytes']:.0f} bytes
• Duration: {metrics['simulation_time_sec']} seconds"""
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.1))
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Save and show the combined plot
    plt.savefig('QuestionA-Part1-CombinedMetrics.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    Main function to orchestrate the network performance analysis.
    """
    print("Starting Network Performance Analysis")
    print("=" * 50)
    
    # Step 1: Parse the trace file
    parsed_data = parse_sca_file(filename)
    if parsed_data is None:
        print("Failed to parse trace file. Exiting...")
        return
    
    # Step 2: Calculate network metrics
    metrics = calculate_network_metrics(parsed_data)
    if metrics is None:
        print("Failed to calculate metrics. Exiting...")
        return
    
    # Step 3: Create individual plots for each metric group
    create_individual_plots(metrics)
    
    # Step 4: Create combined plot with all metrics
    create_combined_plot(metrics)
    
    print("\nAnalysis completed! Generated files:")
    print("- QuestionA-Part1-BitRate-Throughput.png")
    print("- QuestionA-Part1-Delay.png")
    print("- QuestionA-Part1-PLR.png")
    print("- QuestionA-Part1-CombinedMetrics.png")

# Execute the analysis
if __name__ == "__main__":
    main()

