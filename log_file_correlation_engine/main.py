import argparse
import os
from .engine import CorrelationEngine

def main():
    parser = argparse.ArgumentParser(description="Log File Correlation Engine")
    parser.add_argument('--logs', required=True, help="Directory containing log files")
    parser.add_argument('--rules', required=True, help="YAML file containing correlation rules")
    parser.add_argument('--log-type', required=True, choices=['apache', 'ssh', 'custom'], help="Type of log files to process")

    args = parser.parse_args()

    engine = CorrelationEngine(args.rules)

    for filename in sorted(os.listdir(args.logs)):
        file_path = os.path.join(args.logs, filename)
        if os.path.isfile(file_path):
            print(f"Processing log file: {file_path}")
            engine.process_log_file(file_path, args.log_type)

if __name__ == '__main__':
    main()
