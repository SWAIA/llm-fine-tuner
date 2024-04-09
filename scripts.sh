# Initialize log files for tracking data preparation process
initialize_log_files() {
    echo "Initializing log files..."
    >data_preparation.log # Clear existing log or create new
    echo "Log file initialized."
}

# Start the data preparation process and log its progress
start_data_preparation() {
    echo "Starting data preparation process..." | tee -a data_preparation.log
    # Execute Python script for data processing and log output
    python process.py --input_dir ./data --output_file structured_output.json >>data_preparation.log 2>&1
    echo "Data preparation completed. Output saved to structured_output.json." | tee -a data_preparation.log
}

# Cleanup temporary files created during data preparation
cleanup_temp_files() {
    echo "Cleaning up temporary data files..."
    rm -rf ./data/tmp # Remove temporary data directory
    echo "Temporary data files removed." | tee -a data_preparation.log
}

# Sequentially call functions to execute the data preparation workflow
initialize_log_files
start_data_preparation
cleanup_temp_files
