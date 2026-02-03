import yaml

class Rule:
    def __init__(self, name, description, conditions, timeframe=None):
        self.name = name
        self.description = description
        self.conditions = conditions
        self.timeframe = timeframe

    def matches(self, events):
        """
        Checks if a list of events matches the rule's conditions.
        """
        # This is a simplified matching logic. A real implementation would be more complex.
        if len(events) < len(self.conditions):
            return False

        # Check each condition against the corresponding event
        for i, condition in enumerate(self.conditions):
            event = events[i]
            for key, value in condition.items():
                if key not in event or str(event[key]) != str(value):
                    return False
        return True

def load_rules(filename):
    """
    Loads correlation rules from a YAML file.
    """
    with open(filename, 'r') as f:
        rules_data = yaml.safe_load(f)
    
    rules = []
    for rule_data in rules_data.get('rules', []):
        rule = Rule(
            name=rule_data.get('name'),
            description=rule_data.get('description'),
            conditions=rule_data.get('conditions', []),
            timeframe=rule_data.get('timeframe')
        )
        rules.append(rule)
    return rules
