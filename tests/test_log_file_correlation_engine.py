import unittest
import os
import shutil
import builtins
from datetime import datetime, timedelta
from log_file_correlation_engine.parsers import parse_apache_log, parse_ssh_log, parse_custom_app_log
from log_file_correlation_engine.rules import load_rules
from log_file_correlation_engine.engine import CorrelationEngine

class TestParsers(unittest.TestCase):

    def test_parse_apache_log(self):
        log_entry = '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
        parsed = parse_apache_log(log_entry)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['ip'], '127.0.0.1')
        self.assertEqual(parsed['status'], 200)

    def test_parse_ssh_log_failure(self):
        log_entry = 'Dec 10 06:55:46 server sshd[12345]: Failed password for invalid user admin from 103.207.39.182 port 36560 ssh2'
        parsed = parse_ssh_log(log_entry)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['status'], 'failure')
        self.assertEqual(parsed['user'], 'admin')
        self.assertEqual(parsed['ip'], '103.207.39.182')

    def test_parse_ssh_log_success(self):
        log_entry = 'Dec 10 06:55:52 server sshd[12345]: Accepted password for user user1 from 103.207.39.182 port 36560 ssh2'
        parsed = parse_ssh_log(log_entry)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['status'], 'success')
        self.assertEqual(parsed['user'], 'user1')
        self.assertEqual(parsed['ip'], '103.207.39.182')

    def test_parse_custom_app_log(self):
        log_entry = '{"timestamp": "2023-10-27T10:00:00", "level": "INFO", "message": "User logged in", "user": "testuser"}'
        parsed = parse_custom_app_log(log_entry)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['level'], 'INFO')
        self.assertEqual(parsed['user'], 'testuser')

class TestRules(unittest.TestCase):

    def setUp(self):
        self.rules_dir = 'rules'
        self.rules_file = os.path.join(self.rules_dir, 'test_rules.yml')
        os.makedirs(self.rules_dir, exist_ok=True)
        with open(self.rules_file, 'w') as f:
            f.write("""
rules:
  - name: "Test Rule"
    description: "A test rule."
    conditions:
      - type: "ssh"
        status: "failure"
""")

    def tearDown(self):
        shutil.rmtree(self.rules_dir)

    def test_load_rules(self):
        rules = load_rules(self.rules_file)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, 'Test Rule')

class TestEngine(unittest.TestCase):

    def setUp(self):
        # Create dummy files for testing
        self.logs_dir = 'test_logs'
        self.rules_dir = 'test_rules_dir'
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.rules_dir, exist_ok=True)

        self.ssh_log_file = os.path.join(self.logs_dir, 'ssh.log')
        with open(self.ssh_log_file, 'w') as f:
            f.write('Dec 10 06:55:46 server sshd[12345]: Failed password for user user1 from 1.2.3.4 port 1234 ssh2\n')
            f.write('Dec 10 06:55:48 server sshd[12345]: Failed password for user user1 from 1.2.3.4 port 1234 ssh2\n')
            f.write('Dec 10 06:55:50 server sshd[12345]: Accepted password for user user1 from 1.2.3.4 port 1234 ssh2\n')

        self.rules_file = os.path.join(self.rules_dir, 'rules.yml')
        with open(self.rules_file, 'w') as f:
            f.write("""
rules:
  - name: "Successful SSH Login After Failures"
    description: "Test rule for successful login after failures."
    conditions:
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "failure"
      - type: "ssh"
        status: "success"
""")

    def tearDown(self):
        # Clean up dummy files
        shutil.rmtree(self.logs_dir)
        shutil.rmtree(self.rules_dir)

    def test_correlation_engine(self):
        engine = CorrelationEngine(self.rules_file)
        # We need to manually parse and add events to the engine for this test
        # as process_log_file is designed for file paths
        
        events = []
        with open(self.ssh_log_file, 'r') as f:
            for line in f:
                event = parse_ssh_log(line.strip())
                if event:
                    # Setting a fixed year for comparison, as ssh logs don't have it
                    event['timestamp'] = event['timestamp'].replace(year=2023)
                    events.append(event)
        
        # Sort events by timestamp
        events.sort(key=lambda e: e['timestamp'])
        
        # Keep track of alerts
        original_print = builtins.print
        self.alert_fired = False
        def mock_print(*args, **kwargs):
            if "ALERT" in args[0]:
                self.alert_fired = True
            original_print(*args, **kwargs)

        builtins.print = mock_print
        
        for event in events:
            engine.add_event(event)

        builtins.print = original_print # Restore print
        
        self.assertTrue(self.alert_fired, "Alert was not fired for the test rule")


if __name__ == '__main__':
    unittest.main()
