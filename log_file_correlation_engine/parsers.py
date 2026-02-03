import re
import json
from datetime import datetime

def parse_apache_log(log_entry):
    """
    Parses an Apache access log entry.
    """
    match = re.match(r'(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+)\s?(\S+)?\s?(\S+)?" (\d{3}) (\d+)', log_entry)
    if match:
        return {
            'type': 'apache',
            'timestamp': datetime.strptime(match.group(4), '%d/%b/%Y:%H:%M:%S %z'),
            'ip': match.group(1),
            'method': match.group(5),
            'uri': match.group(6),
            'status': int(match.group(8)),
            'bytes_sent': int(match.group(9))
        }
    return None

def parse_ssh_log(log_entry):
    """
    Parses an SSH authentication log entry.
    """
    # Failed login
    match = re.search(r'(\w+\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]: Failed password for (?:invalid user\s)?(?:user )?(\w+) from (\S+) port \d+', log_entry)
    if match:
        # Add a default year to avoid DeprecationWarning
        timestamp_str = match.group(1)
        current_year = datetime.now().year
        timestamp = datetime.strptime(f"{timestamp_str} {current_year}", '%b %d %H:%M:%S %Y')
        return {
            'type': 'ssh',
            'timestamp': timestamp,
            'status': 'failure',
            'user': match.group(2),
            'ip': match.group(3)
        }

    # Successful login
    match = re.search(r'(\w+\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]: Accepted password for (?:user )?(\w+) from (\S+) port \d+', log_entry)
    if match:
        # Add a default year to avoid DeprecationWarning
        timestamp_str = match.group(1)
        current_year = datetime.now().year
        timestamp = datetime.strptime(f"{timestamp_str} {current_year}", '%b %d %H:%M:%S %Y')
        return {
            'type': 'ssh',
            'timestamp': timestamp,
            'status': 'success',
            'user': match.group(2),
            'ip': match.group(3)
        }
    return None

def parse_custom_app_log(log_entry):
    """
    Parses a custom application log entry (JSON format).
    """
    try:
        log_data = json.loads(log_entry)
        log_data['timestamp'] = datetime.fromisoformat(log_data['timestamp'])
        return log_data
    except (json.JSONDecodeError, KeyError):
        return None

def get_parser(log_type):
    """
    Returns the parser function for a given log type.
    """
    if log_type == 'apache':
        return parse_apache_log
    elif log_type == 'ssh':
        return parse_ssh_log
    elif log_type == 'custom':
        return parse_custom_app_log
    return None
