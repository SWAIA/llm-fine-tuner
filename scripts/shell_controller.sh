#!/bin/bash

# Initializes or clears the log file
initialize_log_file() {
    >$1
}

# Runs the data preparation process
run_data_preparation() {
    python process.py --input_dir "$1" --output_file "$2" >>"$3" 2>&1
}

validate_output() {
    if [ -f $1 ]; then
        if [ "$(jq length $1)" -gt 0 ]; then
            echo "Output file contains valid JSON data." | tee -a $2
        else
            echo "Output file is empty or contains invalid JSON data." | tee -a $2
        fi
    else
        echo "Output file $1 does not exist." | tee -a $2
    fi
}
run_data_preparation() {
    python process.py --input_dir "$1" --output_file "$2" >>"$3" 2>&1
}

validate_output() {
    if [ -f $1 ]; then
        if [ "$(jq length $1)" -gt 0 ]; then
            echo "Output file contains valid JSON data." | tee -a $2
        else
            echo "Output file is empty or contains invalid JSON data." | tee -a $2
        fi
    else
        echo "Output file $1 does not exist." | tee -a $2
    fi
}

set_permissions() {
    chmod +x $1
}

upload_output() {
    scp $1 user@remote_server:/path/to/destination >>$2 2>&1
}

cleanup_temp_files() {
    rm -rf $1
}

run_all() {
    >$1
    run_data_preparation $2 $3 $1
    validate_output $3 $1
    upload_output $3 $1
    rm -rf $4
}

display_menu() {
    echo "Select an option:"
    echo "1. Run data preparation"
    echo "2. Validate output"
    echo "3. Upload output"
    echo "4. Run all steps"
    read -p "Enter your choice (1-4): " choice

    case $choice in
    1) run_data_preparation $1 $2 $3 ;;
    2) validate_output $2 $3 ;;
    3) upload_output $2 $3 ;;
    4) run_all $1 $2 $3 $4 ;;
    *) echo "Invalid choice. Exiting." ;;
    esac
}

main() {
    display_menu
}

main
