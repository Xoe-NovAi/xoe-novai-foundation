#!/usr/bin/env python3
"""
Vikunja API helper: checks available endpoints and reports authorization status.

Usage:
  export VIKUNJA_URL=http://127.0.0.1:3456
  export VIKUNJA_TOKEN=<your-token>
  python3 scripts/vikunja_api_helper.py

This script will try multiple header schemes and common paths to help diagnose 401/403 issues.
"""

import os
import requests

VIKUNJA_URL = os.getenv('VIKUNJA_URL', 'http://127.0.0.1:3456')
TOKEN = os.getenv('VIKUNJA_TOKEN')

HEADERS_CANDIDATES = []
if TOKEN:
    HEADERS_CANDIDATES.append({'Authorization': f'Token {TOKEN}'})
    HEADERS_CANDIDATES.append({'Authorization': f'Bearer {TOKEN}'})
    HEADERS_CANDIDATES.append({'X-Auth-Token': TOKEN})
else:
    HEADERS_CANDIDATES.append({})

PATHS = ['/', '/api', '/api/v1', '/api/v1/projects', '/v1/projects', '/api/migrators', '/api/admin']


def try_request(path, headers):
    url = VIKUNJA_URL.rstrip('/') + path
    try:
        r = requests.get(url, headers=headers, timeout=5)
        return r.status_code, r.text[:400]
    except Exception as e:
        return None, str(e)


def main():
    print(f"Checking Vikunja at: {VIKUNJA_URL}")
    for headers in HEADERS_CANDIDATES:
        print(f"\nTrying headers: {headers}")
        for path in PATHS:
            code, body = try_request(path, headers)
            print(f"  {path} -> {code} | {body[:80].replace('\n',' ')}")

    if not TOKEN:
        print("\nNo VIKUNJA_TOKEN provided. To create a token: log into Vikunja with an admin account, go to Settings or Admin -> API keys (or Service Tokens), create a token, and set VIKUNJA_TOKEN env var.")

if __name__ == '__main__':
    main()
