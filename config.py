"""
Configration script.

This script allows for retrieval of stored settings.
"""

import json


def setting(configfile):
    """Will grab a setting."""
    with open(configfile) as f:
        CONFIG = json.load(f)
    return CONFIG
