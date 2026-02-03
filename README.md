# Log file correlation engine

52. **Log File Correlation Engine:** Create a tool that can ingest logs from multiple sources (e.g., web server, firewall, OS) and correlate events to build a timeline of a security incident.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/log-file-correlation-engine.git
    cd log-file-correlation-engine
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage

The log file correlation engine can be run from the command line.

### 1. Prepare Log Files

Place your log files in a directory. For example, create a `logs` directory:

```bash
mkdir logs
# Move your log files into the 'logs' directory
```

### 2. Define Correlation Rules

Create a YAML file containing your correlation rules. An example `rules.yml` file:

```yaml
rules:
  - name: "SSH Brute-force Attempt"
    description: "Detects multiple failed SSH login attempts from the same IP address."
    timeframe: 60 # seconds
    conditions:
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "failure"

  - name: "Successful SSH Login After Failures"
    description: "Alerts on a successful SSH login from an IP that recently had multiple failed attempts."
    timeframe: 60 # seconds
    conditions:
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "success"

  - name: "Potential SQL Injection Attempt"
    description: "Detects a web request with a suspicious URL pattern followed by a server error."
    timeframe: 10 # seconds
    conditions:
      - type: "apache"
        uri: "/login.php?user=admin' OR '1'='1'"
      - type: "apache"
        status: 500
```

### 3. Run the Engine

Execute the engine using the `main.py` script, specifying the log directory, rules file, and log type:

```bash
python3 -m log_file_correlation_engine.main --logs <path_to_logs_directory> --rules <path_to_rules_file.yml> --log-type <log_type>
```

**Example:**

To process SSH logs in the `logs` directory using `rules.yml`:

```bash
python3 -m log_file_correlation_engine.main --logs ./logs --rules ./rules.yml --log-type ssh
```

Supported log types for `--log-type`:
- `apache`
- `ssh`
- `custom`

### Example Log Formats

**Apache Log:**

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
```

**SSH Log (authentication logs, e.g., `/var/log/auth.log`):**

```
Dec 10 06:55:46 server sshd[12345]: Failed password for invalid user admin from 103.207.39.182 port 36560 ssh2
Dec 10 06:55:52 server sshd[12345]: Accepted password for user user1 from 103.207.39.182 port 36560 ssh2
```

**Custom Application Log (JSON format):**

```json
{"timestamp": "2023-10-27T10:00:00", "level": "INFO", "message": "User logged in", "user": "testuser"}
```

This completes the project by providing the core functionality, tests, and documentation.