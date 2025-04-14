# TCP Client-Server Project Requirements Verification

## Code Requirements Verification

### Server Implementation
- [x] Passive listening mode implemented
- [x] Connection setup with acknowledgment implemented
- [x] Processing of sequence numbers implemented
- [x] Tracking of missing packets implemented
- [x] Calculation and reporting of goodput implemented

### Client Implementation
- [x] Connection initiation to server implemented
- [x] Sliding window protocol implemented
- [x] Processing of ACKs implemented
- [x] 1% probabilistic packet dropping implemented
- [x] Retransmission of dropped packets implemented

## Rubric Requirements Verification

### Executable Code Files (2 points)
- [x] Server code file (server.py) created
- [x] Client code file (client.py) created
- [x] Code compiles with no syntax errors
- [x] Code is modular/divided into functions
- [x] Code is well documented
- [x] Code implements the desired project

### Screenshots of Output (4 points)
- [x] Sender IP Address and Receiver IP Address documented
- [x] Number of packets sent and number of packets received documented
- [x] Good-put calculated and documented

### Graphs (6 points)
- [x] TCP Sender and Receiver window size over time in the x-axis graph created
- [x] TCP Sequence number received over time in the x-axis graph created
- [x] TCP Sequence number dropped over time in the x-axis graph created

### Table (2 points)
- [x] Table showing # of retransmissions vs # of packets created

## Project Specific Requirements Verification

- [x] TCP client/server communication over network implemented
- [x] Server starts in passive mode listening for transmission
- [x] Client contacts server on given IP address and port number
- [x] Client passes initial string to server
- [x] Server responds with connection setup "success" message
- [x] Client sends TCP segments in sliding window manner
- [x] Client sends sequence numbers to server
- [x] Server responds with corresponding ACK numbers
- [x] Client adjusts sliding window based on ACKs
- [x] Server tracks missing sequence numbers
- [x] Client probabilistically drops 1% of packets
- [x] Client retransmits dropped packets

## Test Results Verification

- [x] Test successfully demonstrates TCP sliding window protocol
- [x] Test successfully demonstrates packet dropping and retransmission
- [x] Performance data collected and analyzed
- [x] Visualizations generated from test data

## Documentation Verification

- [x] Documentation includes project overview
- [x] Documentation includes implementation details
- [x] Documentation includes performance metrics
- [x] Documentation includes visualizations
- [x] Documentation includes IP addresses
- [x] Documentation includes packet counts
- [x] Documentation includes goodput measurements

## Final Deliverables Verification

- [x] Server code file (server.py) included in final package
- [x] Client code file (client.py) included in final package
- [x] Documentation file (documentation.md) included in final package
- [x] Graphs and visualizations included in final package
- [x] All files organized in a structured manner
- [x] Final package compiled into a zip file

All project requirements have been successfully met. The implementation fulfills all the specified functionality, the documentation covers all required aspects, and the visualizations demonstrate all required metrics.
