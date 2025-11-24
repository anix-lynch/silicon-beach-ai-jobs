#!/usr/bin/env python3
"""
🔐 Universal Secret Getter
Works in both sandboxed and non-sandboxed environments

Usage:
    from scripts.get_secret import get_secret
    api_key = get_secret('GOOGLE_MAPS_API_KEY')
"""

import os
from pathlib import Path
from typing import Optional

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get secret from environment variable or secret files.
    Tries multiple locations to work in both sandboxed and non-sandboxed environments.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Secret value or default
    """
    # First, check if already in environment (highest priority)
    value = os.getenv(key)
    if value:
        return value
    
    # Try loading from secret files (in order of preference)
    secret_paths = [
        Path.home() / '.config' / 'secrets' / 'global.env',
        Path.home() / '.secrets' / 'global.env',
        Path.cwd() / '.env',
        Path.cwd() / '.env.local',
        Path.cwd().parent / '.env',
        Path.cwd().parent / '.env.local',
    ]
    
    for secret_file in secret_paths:
        if secret_file.exists() and secret_file.is_file():
            try:
                # Parse .env file format (key=value)
                with open(secret_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        # Parse key=value
                        if '=' in line:
                            file_key, file_value = line.split('=', 1)
                            file_key = file_key.strip()
                            file_value = file_value.strip().strip('"').strip("'")
                            if file_key == key:
                                return file_value
            except (IOError, PermissionError):
                # Can't read file (sandboxed?), continue to next
                continue
    
    # Not found anywhere
    return default

def load_all_secrets() -> dict:
    """
    Load all secrets from the first available secret file.
    Returns dict of key-value pairs.
    """
    secrets = {}
    
    secret_paths = [
        Path.home() / '.config' / 'secrets' / 'global.env',
        Path.home() / '.secrets' / 'global.env',
        Path.cwd() / '.env',
        Path.cwd() / '.env.local',
    ]
    
    for secret_file in secret_paths:
        if secret_file.exists() and secret_file.is_file():
            try:
                with open(secret_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            secrets[key] = value
                return secrets
            except (IOError, PermissionError):
                continue
    
    return secrets

# Example usage
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        key = sys.argv[1]
        value = get_secret(key)
        if value:
            print(value)
        else:
            sys.exit(1)
    else:
        # Print all available secrets (for debugging)
        secrets = load_all_secrets()
        for key, value in secrets.items():
            # Mask sensitive values
            if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                print(f"{key}=***")
            else:
                print(f"{key}={value}")

