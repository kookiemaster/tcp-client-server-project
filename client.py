#!/usr/bin/env python3
"""
TCP Client Implementation for CS 258 Project
Team Members: Xiangyi Li

This client implements a simplified TCP sliding window protocol.
It connects to the server, sends sequence numbers, processes ACKs,
simulates packet drops, and handles retransmissions.
"""

import socket
import time
import random
import logging
import threading
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TCPClient:
    """TCP Client implementation with sliding window protocol simulation."""
    
    def __init__(self, server_host='127.0.0.1', server_port=12345, 
                 window_size=10, max_seq_num=2**16, drop_rate=0.01):
        """
        Initialize the TCP client.
        
        Args:
            server_host (str): Server IP address to connect to
            server_port (int): Server port number
            window_size (int): Initial sliding window size
            max_seq_num (int): Maximum sequence number (2^16 as per requirements)
            drop_rate (float): Probability of packet drop (0.01 = 1%)
        """
        self.server_host = server_host
        self.server_port = server_port
        self.window_size = window_size
        self.max_seq_num = max_seq_num
        self.drop_rate = drop_rate
        self.client_socket = None
        
        # For sliding window protocol
        self.base = 0  # First sequence number in the window
        self.next_seq_num = 0  # Next sequence number to be sent
        self.window = {}  # Map of sequence numbers to their status (sent, acked)
        
        # For tracking packets
        self.sent_packets = 0
        self.acked_packets = 0
        self.dropped_packets = set()
        self.retransmission_queue = set()
        
        # For visualization
        self.start_time = None
        self.window_size_history = []
        self.window_size_timestamps = []
        self.seq_sent_history = []
        self.seq_sent_timestamps = []
        self.seq_dropped_history = []
        self.seq_dropped_timestamps = []
        
        # For retransmission statistics
        self.retransmission_counts = {}  # seq_num -> count of retransmissions
        
    def connect(self):
        """Connect to the TCP server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            logger.info(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Send initial string to server
            initial_string = "network"
            self.client_socket.send(initial_string.encode('utf-8'))
            
            # Receive connection setup success message
            response = self.client_socket.recv(1024).decode('utf-8')
            logger.info(f"Server response: {response}")
            
            if "success" in response.lower():
                logger.info("Connection setup successful")
                return True
            else:
                logger.error("Connection setup failed")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def start(self, total_packets=10_000_000):
        """
        Start the TCP client and send packets.
        
        Args:
            total_packets (int): Total number of packets to send
        """
        if not self.connect():
            return
        
        self.start_time = time.time()
        
        try:
            # Start a thread to receive ACKs
            ack_thread = threading.Thread(target=self.receive_acks)
            ack_thread.daemon = True
            ack_thread.start()
            
            # Start sending packets
            while self.sent_packets < total_packets:
                # Process any pending retransmissions first
                self.process_retransmissions()
                
                # Send new packets if window allows
                while (self.next_seq_num < self.base + self.window_size and 
                       self.next_seq_num < total_packets and 
                       self.next_seq_num < self.max_seq_num):
                    
                    # Simulate packet drop
                    if random.random() < self.drop_rate:
                        logger.debug(f"Dropping packet with sequence number {self.next_seq_num}")
                        self.dropped_packets.add(self.next_seq_num)
                        self.retransmission_queue.add(self.next_seq_num)
                        
                        # Record for visualization
                        self.seq_dropped_history.append(self.next_seq_num)
                        self.seq_dropped_timestamps.append(time.time() - self.start_time)
                        
                        # Update retransmission count
                        if self.next_seq_num not in self.retransmission_counts:
                            self.retransmission_counts[self.next_seq_num] = 0
                    else:
                        # Send the packet (sequence number)
                        self.send_packet(self.next_seq_num)
                    
                    # Update window and counters
                    self.window[self.next_seq_num] = {'sent': True, 'acked': False}
                    self.next_seq_num += 1
                    self.sent_packets += 1
                    
                    # Record window size for visualization
                    self.window_size_history.append(self.window_size)
                    self.window_size_timestamps.append(time.time() - self.start_time)
                
                # Retransmit dropped packets after every 100 sequence numbers
                if self.next_seq_num % 100 == 0 and self.retransmission_queue:
                    self.process_retransmissions()
                
                # Small delay to prevent CPU overload
                time.sleep(0.001)
            
            # Wait for all ACKs or timeout
            timeout = time.time() + 30  # 30 seconds timeout
            while self.acked_packets < total_packets and time.time() < timeout:
                time.sleep(0.1)
            
            logger.info(f"Transmission completed. Sent: {self.sent_packets}, ACKed: {self.acked_packets}")
            
            # Generate visualization
            self.generate_visualizations()
            
        except Exception as e:
            logger.error(f"Error during transmission: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            logger.info("Client shutdown")
    
    def send_packet(self, seq_num):
        """
        Send a packet (sequence number) to the server.
        
        Args:
            seq_num (int): Sequence number to send
        """
        try:
            message = f"SEQ:{seq_num}"
            self.client_socket.send(message.encode('utf-8'))
            logger.debug(f"Sent packet with sequence number {seq_num}")
            
            # Record for visualization
            self.seq_sent_history.append(seq_num)
            self.seq_sent_timestamps.append(time.time() - self.start_time)
            
        except Exception as e:
            logger.error(f"Error sending packet: {e}")
    
    def receive_acks(self):
        """Receive and process ACKs from the server."""
        try:
            buffer_size = 1024
            while True:
                data = self.client_socket.recv(buffer_size)
                if not data:
                    break
                
                # Process the received ACKs
                self.process_acks(data)
                
        except Exception as e:
            logger.error(f"Error receiving ACKs: {e}")
    
    def process_acks(self, data):
        """
        Process ACKs received from the server.
        
        Args:
            data (bytes): Data received from server containing ACKs
        """
        try:
            data_str = data.decode('utf-8')
            if data_str.startswith("ACK:"):
                ack_numbers_str = data_str[4:].strip()
                ack_numbers = [int(num) for num in ack_numbers_str.split(',') if num]
                
                # Process each ACK
                for ack_num in ack_numbers:
                    if ack_num in self.window and not self.window[ack_num]['acked']:
                        self.window[ack_num]['acked'] = True
                        self.acked_packets += 1
                        
                        # Remove from retransmission queue if present
                        if ack_num in self.retransmission_queue:
                            self.retransmission_queue.remove(ack_num)
                
                # Slide the window
                self.slide_window()
                
                # Log progress periodically
                if self.acked_packets % 1000 == 0:
                    logger.info(f"Packets sent: {self.sent_packets}, ACKed: {self.acked_packets}, "
                                f"Window size: {self.window_size}")
        
        except Exception as e:
            logger.error(f"Error processing ACKs: {e}")
    
    def slide_window(self):
        """Slide the window based on received ACKs."""
        # Find the new base (first unacked packet)
        while self.base in self.window and self.window[self.base]['acked']:
            self.base += 1
        
        # Adjust window size (simple congestion control)
        # Increase window size if all packets in current window are ACKed
        all_acked = all(self.window.get(seq_num, {}).get('acked', False) 
                        for seq_num in range(self.base, self.next_seq_num))
        
        if all_acked:
            self.window_size = min(self.window_size + 1, 100)  # Cap at 100 for simplicity
        
        # Record window size for visualization
        self.window_size_history.append(self.window_size)
        self.window_size_timestamps.append(time.time() - self.start_time)
    
    def process_retransmissions(self):
        """Process and retransmit dropped packets."""
        retransmitted = set()
        
        for seq_num in self.retransmission_queue:
            # Simulate packet drop for retransmissions too
            if random.random() < self.drop_rate:
                logger.debug(f"Dropping retransmission of sequence number {seq_num}")
                
                # Record for visualization
                self.seq_dropped_history.append(seq_num)
                self.seq_dropped_timestamps.append(time.time() - self.start_time)
            else:
                # Retransmit the packet
                self.send_packet(seq_num)
                logger.debug(f"Retransmitted packet with sequence number {seq_num}")
                
                # Update retransmission count
                if seq_num in self.retransmission_counts:
                    self.retransmission_counts[seq_num] += 1
                else:
                    self.retransmission_counts[seq_num] = 1
                
                retransmitted.add(seq_num)
        
        # Remove successfully retransmitted packets from the queue
        self.retransmission_queue -= retransmitted
    
    def generate_visualizations(self):
        """Generate visualizations and save statistics."""
        try:
            # 1. TCP Sender window size over time
            plt.figure(figsize=(12, 6))
            plt.plot(self.window_size_timestamps, self.window_size_history)
            plt.title('TCP Sender Window Size Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Window Size')
            plt.grid(True)
            plt.savefig('sender_window_size.png')
            plt.close()
            
            # 2. TCP Sequence numbers sent over time
            plt.figure(figsize=(12, 6))
            plt.scatter(self.seq_sent_timestamps, self.seq_sent_history, s=1, alpha=0.5)
            plt.title('TCP Sequence Numbers Sent Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Sequence Number')
            plt.grid(True)
            plt.savefig('sequence_numbers_sent.png')
            plt.close()
            
            # 3. TCP Sequence numbers dropped over time
            plt.figure(figsize=(12, 6))
            plt.scatter(self.seq_dropped_timestamps, self.seq_dropped_history, s=1, alpha=0.5, color='red')
            plt.title('TCP Sequence Numbers Dropped Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Sequence Number')
            plt.grid(True)
            plt.savefig('sequence_numbers_dropped_client.png')
            plt.close()
            
            # Save retransmission statistics
            retrans_stats = {}
            for seq_num, count in self.retransmission_counts.items():
                if count in retrans_stats:
                    retrans_stats[count] += 1
                else:
                    retrans_stats[count] = 1
            
            with open('client_retransmission_stats.txt', 'w') as f:
                f.write("# of retransmissions | # of packets\n")
                f.write("-" * 40 + "\n")
                for retrans_count in sorted(retrans_stats.keys()):
                    f.write(f"{retrans_count} | {retrans_stats[retrans_count]}\n")
            
            # Save overall statistics
            with open('client_stats.txt', 'w') as f:
                f.write(f"Client IP Address: {socket.gethostbyname(socket.gethostname())}\n")
                f.write(f"Server IP Address: {self.server_host}\n")
                f.write(f"Total Packets Sent: {self.sent_packets}\n")
                f.write(f"Total Packets ACKed: {self.acked_packets}\n")
                f.write(f"Packets Dropped: {len(self.dropped_packets)}\n")
                f.write(f"Drop Rate: {self.drop_rate}\n")
            
            logger.info("Visualizations and statistics generated successfully")
        
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")

if __name__ == "__main__":
    # For testing with a smaller number of packets
    test_packets = 10000  # Use 10,000,000 for the full project requirement
    
    client = TCPClient()
    client.start(total_packets=test_packets)
