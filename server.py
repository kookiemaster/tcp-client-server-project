#!/usr/bin/env python3
"""
TCP Server Implementation for CS 258 Project
Team Members: Xiangyi Li

This server implements a simplified TCP sliding window protocol.
It listens for connections from clients, processes sequence numbers,
tracks missing packets, and calculates goodput.
"""

import socket
import time
import threading
import logging
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TCPServer:
    """TCP Server implementation with sliding window protocol simulation."""
    
    def __init__(self, host='0.0.0.0', port=12345, max_seq_num=2**16):
        """
        Initialize the TCP server.
        
        Args:
            host (str): Host IP address to bind to
            port (int): Port number to listen on
            max_seq_num (int): Maximum sequence number (2^16 as per requirements)
        """
        self.host = host
        self.port = port
        self.max_seq_num = max_seq_num
        self.server_socket = None
        self.client_address = None
        
        # Data structures for tracking packets
        self.received_packets = set()
        self.missing_packets = set()
        self.total_received = 0
        self.total_expected = 0
        self.highest_seq_received = -1
        
        # For goodput calculation
        self.goodput_values = []
        self.goodput_timestamps = []
        self.start_time = None
        
        # For visualization
        self.window_size_history = []
        self.window_size_timestamps = []
        self.seq_received_history = []
        self.seq_received_timestamps = []
        self.seq_dropped_history = []
        self.seq_dropped_timestamps = []
        
        # For retransmission statistics
        self.retransmission_stats = defaultdict(int)
        self.packet_retransmission_count = defaultdict(int)
        
    def start(self):
        """Start the TCP server and listen for connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            logger.info(f"Server started on {self.host}:{self.port}")
            logger.info("Waiting for client connection...")
            
            # Accept client connection
            client_socket, self.client_address = self.server_socket.accept()
            logger.info(f"Connection established with {self.client_address}")
            
            # Start time for measurements
            self.start_time = time.time()
            
            # Handle client connection in a separate thread
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
            # Wait for the client thread to finish
            client_thread.join()
            
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            logger.info("Server shutdown")
            
            # Generate visualization after completion
            self.generate_visualizations()
    
    def handle_client(self, client_socket):
        """
        Handle client connection and process data.
        
        Args:
            client_socket (socket): Socket connected to the client
        """
        try:
            # Receive initial string from client
            initial_data = client_socket.recv(1024).decode('utf-8')
            logger.info(f"Received initial string: {initial_data}")
            
            # Send connection setup success message
            client_socket.send("Connection setup success".encode('utf-8'))
            
            # Process sequence numbers from client
            buffer_size = 1024
            while True:
                data = client_socket.recv(buffer_size)
                if not data:
                    break
                
                # Process the received sequence numbers
                self.process_sequence_numbers(data, client_socket)
                
                # Check if we've reached the target number of packets
                if self.total_expected >= 10_000_000:
                    logger.info("Reached target packet count. Finishing...")
                    break
            
            logger.info("Client disconnected")
            
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def process_sequence_numbers(self, data, client_socket):
        """
        Process sequence numbers received from client.
        
        Args:
            data (bytes): Data received from client containing sequence numbers
            client_socket (socket): Socket connected to the client
        """
        # Parse sequence numbers from data
        # Format: "SEQ:number1,number2,..."
        try:
            data_str = data.decode('utf-8')
            if data_str.startswith("SEQ:"):
                seq_numbers_str = data_str[4:].strip()
                seq_numbers = [int(num) for num in seq_numbers_str.split(',') if num]
                
                # Process each sequence number
                for seq_num in seq_numbers:
                    self.total_expected += 1
                    
                    # Update highest sequence received
                    if seq_num > self.highest_seq_received:
                        self.highest_seq_received = seq_num
                    
                    # Check if this is a new packet or retransmission
                    if seq_num in self.missing_packets:
                        self.missing_packets.remove(seq_num)
                        self.received_packets.add(seq_num)
                        self.total_received += 1
                        
                        # Update retransmission statistics
                        self.packet_retransmission_count[seq_num] += 1
                        retrans_count = self.packet_retransmission_count[seq_num]
                        self.retransmission_stats[retrans_count] += 1
                        
                        # Record for visualization
                        self.seq_received_history.append(seq_num)
                        self.seq_received_timestamps.append(time.time() - self.start_time)
                    elif seq_num not in self.received_packets:
                        self.received_packets.add(seq_num)
                        self.total_received += 1
                        
                        # Record for visualization
                        self.seq_received_history.append(seq_num)
                        self.seq_received_timestamps.append(time.time() - self.start_time)
                
                # Check for missing packets in the sequence
                for seq_num in range(0, self.highest_seq_received + 1):
                    if seq_num not in self.received_packets and seq_num not in self.missing_packets:
                        self.missing_packets.add(seq_num)
                        
                        # Record for visualization
                        self.seq_dropped_history.append(seq_num)
                        self.seq_dropped_timestamps.append(time.time() - self.start_time)
                
                # Calculate and record window size (estimate based on highest seq - lowest missing)
                if self.missing_packets:
                    window_size = self.highest_seq_received - min(self.missing_packets)
                else:
                    window_size = self.highest_seq_received
                
                self.window_size_history.append(window_size)
                self.window_size_timestamps.append(time.time() - self.start_time)
                
                # Calculate goodput periodically (after every 1000 packets)
                if self.total_received % 1000 == 0:
                    goodput = self.total_received / self.total_expected
                    self.goodput_values.append(goodput)
                    self.goodput_timestamps.append(time.time() - self.start_time)
                    logger.info(f"Packets received: {self.total_received}, Goodput: {goodput:.4f}")
                
                # Send ACK for the received sequence numbers
                ack_message = f"ACK:{','.join(str(seq_num) for seq_num in seq_numbers)}"
                client_socket.send(ack_message.encode('utf-8'))
        
        except Exception as e:
            logger.error(f"Error processing sequence numbers: {e}")
    
    def generate_visualizations(self):
        """Generate visualizations and save statistics."""
        try:
            # 1. TCP Sender and Receiver window size over time
            plt.figure(figsize=(12, 6))
            plt.plot(self.window_size_timestamps, self.window_size_history)
            plt.title('TCP Receiver Window Size Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Window Size')
            plt.grid(True)
            plt.savefig('receiver_window_size.png')
            plt.close()
            
            # 2. TCP Sequence number received over time
            plt.figure(figsize=(12, 6))
            plt.scatter(self.seq_received_timestamps, self.seq_received_history, s=1, alpha=0.5)
            plt.title('TCP Sequence Numbers Received Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Sequence Number')
            plt.grid(True)
            plt.savefig('sequence_numbers_received.png')
            plt.close()
            
            # 3. TCP Sequence number dropped over time
            plt.figure(figsize=(12, 6))
            plt.scatter(self.seq_dropped_timestamps, self.seq_dropped_history, s=1, alpha=0.5, color='red')
            plt.title('TCP Sequence Numbers Dropped Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Sequence Number')
            plt.grid(True)
            plt.savefig('sequence_numbers_dropped.png')
            plt.close()
            
            # 4. Goodput over time
            plt.figure(figsize=(12, 6))
            plt.plot(self.goodput_timestamps, self.goodput_values)
            plt.title('Goodput Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Goodput (received/sent)')
            plt.grid(True)
            plt.savefig('goodput.png')
            plt.close()
            
            # Save retransmission statistics to a file
            with open('retransmission_stats.txt', 'w') as f:
                f.write("# of retransmissions | # of packets\n")
                f.write("-" * 40 + "\n")
                for retrans_count in sorted(self.retransmission_stats.keys()):
                    f.write(f"{retrans_count} | {self.retransmission_stats[retrans_count]}\n")
            
            # Save overall statistics
            with open('server_stats.txt', 'w') as f:
                f.write(f"Server IP Address: {self.host}\n")
                f.write(f"Client IP Address: {self.client_address[0] if self.client_address else 'N/A'}\n")
                f.write(f"Total Packets Expected: {self.total_expected}\n")
                f.write(f"Total Packets Received: {self.total_received}\n")
                f.write(f"Missing Packets: {len(self.missing_packets)}\n")
                f.write(f"Average Goodput: {sum(self.goodput_values)/len(self.goodput_values) if self.goodput_values else 0:.4f}\n")
            
            logger.info("Visualizations and statistics generated successfully")
        
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")

if __name__ == "__main__":
    server = TCPServer()
    server.start()
