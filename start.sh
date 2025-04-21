#!/bin/bash

# TCP Client-Server Project Start Script
# Team Member: Xiangyi Li

echo "===== TCP Client-Server Project ====="
echo "This script provides options to run the TCP client-server application"
echo

# Function to check if required dependencies are installed
check_dependencies() {
    echo "Checking dependencies..."
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed. Please install Python 3 to run this project."
        exit 1
    fi
    
    # Check for required Python packages
    python3 -c "import matplotlib" &> /dev/null
    if [ $? -ne 0 ]; then
        echo "Installing matplotlib package..."
        pip3 install matplotlib
    fi
    
    python3 -c "import numpy" &> /dev/null
    if [ $? -ne 0 ]; then
        echo "Installing numpy package..."
        pip3 install numpy
    fi
    
    echo "All dependencies are satisfied."
    echo
}

# Function to run the server
run_server() {
    echo "Starting TCP Server..."
    python3 server.py
}

# Function to run the client
run_client() {
    echo "Starting TCP Client..."
    python3 client.py
}

# Function to run the full test
run_test() {
    echo "Running full TCP client-server test..."
    echo "This will start the server, run the client, and generate performance data and visualizations."
    
    # Create directories if they don't exist
    mkdir -p test_results
    mkdir -p graphs
    
    # Run the test script
    python3 test_tcp.py
    
    # Check if test was successful
    if [ $? -eq 0 ]; then
        echo "Test completed successfully!"
        echo "Performance data and visualizations have been generated."
        echo "Check the 'graphs' directory for visualizations."
    else
        echo "Test failed. Please check the error messages above."
    fi
}

# Function to generate documentation
generate_docs() {
    echo "Generating documentation and visualizations..."
    
    # Run the data extraction script if it exists
    if [ -f "extract_data.py" ]; then
        python3 extract_data.py
        echo "Data extraction and visualization complete."
    else
        echo "Warning: extract_data.py not found. Cannot generate visualizations."
    fi
    
    echo "Documentation is available in documentation.md"
    echo "Visualizations are available in the 'graphs' directory."
}

# Main menu
show_menu() {
    echo "Please select an option:"
    echo "1. Run TCP Server"
    echo "2. Run TCP Client"
    echo "3. Run Full Test (Server + Client + Data Collection)"
    echo "4. Generate Documentation and Visualizations"
    echo "5. Exit"
    echo
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1) run_server ;;
        2) run_client ;;
        3) run_test ;;
        4) generate_docs ;;
        5) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid option. Please try again."; show_menu ;;
    esac
}

# Main script execution
check_dependencies
show_menu

exit 0
