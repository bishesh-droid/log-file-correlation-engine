import os
from datetime import timedelta
from . import parsers
from . import rules

class CorrelationEngine:
    def __init__(self, rules_file, time_window=timedelta(minutes=5)):
        self.rules = rules.load_rules(rules_file)
        self.time_window = time_window
        self.events = []

    def process_log_file(self, file_path, log_type):
        """
        Processes a single log file.
        """
        parser = parsers.get_parser(log_type)
        if not parser:
            print(f"No parser found for log type: {log_type}")
            return

        with open(file_path, 'r') as f:
            for line in f:
                event = parser(line.strip())
                if event:
                    self.add_event(event)

    def add_event(self, event):
        """
        Adds an event to the engine and checks for rule matches.
        """
        self.events.append(event)
        self.events.sort(key=lambda e: e['timestamp'])
        self.cleanup_events()
        self.check_rules()

    def cleanup_events(self):
        """
        Removes old events that are outside the time window.
        """
        now = self.events[-1]['timestamp']
        self.events = [e for e in self.events if now - e['timestamp'] <= self.time_window]

    def check_rules(self):
        """
        Checks all rules against the current event stream.
        """
        for rule in self.rules:
            # This is a very basic implementation. A real engine would have
            # more sophisticated logic to handle event sequences and timeframes.
            
            # Simple check for the last N events
            if len(self.events) >= len(rule.conditions):
                # Get the last N events for checking
                events_to_check = self.events[-len(rule.conditions):]
                
                # Check if the events match the rule conditions
                if rule.matches(events_to_check):
                    self.generate_alert(rule, events_to_check)

    def generate_alert(self, rule, events):
        """
        Generates an alert for a matched rule.
        """
        print("="*40)
        print(f"ALERT: Rule '{rule.name}' matched!")
        print(f"Description: {rule.description}")
        print("Events:")
        for event in events:
            print(f"  - {event}")
        print("="*40)
