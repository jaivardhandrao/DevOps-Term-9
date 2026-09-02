#!/usr/bin/env bash

set -euo pipefail

current_date=$(date '+%Y-%m-%d %H:%M:%S %Z')
host_name=$(hostname)
current_user=$(whoami)
report_dir="system-report"
process_file="$report_dir/processes.txt"
summary_file="$report_dir/summary.txt"

read -r -p "Enter your name: " student_name
read -r -p "Enter your enrollment number: " enrollment_number

mkdir -p "$report_dir"
touch "$process_file" "$summary_file"
ps -eo pid,ppid,user,comm > "$process_file"

{
    echo "System information report"
    echo "Name: $student_name"
    echo "Enrollment number: $enrollment_number"
    echo "Date: $current_date"
    echo "Hostname: $host_name"
    echo "Username: $current_user"
    echo
    echo "Disk usage:"
    df -h
    echo
    echo "Running processes were saved to $process_file"
} | tee "$summary_file"

echo
echo "Running processes:"
cat "$process_file"
