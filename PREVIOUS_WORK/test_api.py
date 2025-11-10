#!/usr/bin/env python3
"""Test QuantConnect API connection"""

import os
from dotenv import load_dotenv
import requests
import time
import hashlib
import hmac

load_dotenv()

user_id = os.getenv("QUANTCONNECT_USER_ID")
api_token = os.getenv("QUANTCONNECT_API_TOKEN")

print(f"User ID: {user_id}")
print(f"API Token: {api_token[:10]}..." if api_token else "None")

# Test HMAC authentication (QC API v2 requirement)
url = "https://www.quantconnect.com/api/v2/projects/read"

# Generate timestamp and hash
timestamp = str(int(time.time()))
message = f"{api_token}:{timestamp}".encode('utf-8')
signature = hashlib.sha256(message).hexdigest()

print(f"\nTimestamp: {timestamp}")
print(f"Signature: {signature[:20]}...")

# QC API v2 authentication headers
headers = {
    "Timestamp": timestamp
}

auth = (user_id, signature)

print(f"\nTesting API connection to {url}")

try:
    response = requests.get(url, auth=auth, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data.get('success')}")
        if data.get('projects'):
            print(f"Projects found: {len(data['projects'])}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Exception: {e}")
