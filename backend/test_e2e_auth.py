"""
End-to-end test script for the Skill Swap auth flow.
Tests: Register → Login → Get Profile → Update Profile → Logout
"""

import urllib.request
import json
import sys
import os

BASE_URL = 'http://localhost:8000/api/auth'


def api_call(endpoint, data=None, method='POST', token=None):
    """Make an API call and return (status, response_dict)."""
    url = f'{BASE_URL}/{endpoint}/'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    print('=' * 60)
    print('  SKILL SWAP — AUTH FLOW END-TO-END TEST')
    print('=' * 60)

    email = 'demo2@test.com'
    password = 'DemoP@ss2'

    # 1. Register
    print('\n1. REGISTER')
    status, result = api_call('register', {
        'email': email,
        'password': password,
        'password_confirm': password,
        'first_name': 'Demo',
        'last_name': 'User',
    })
    print(f'   Status: {status}')
    print(f'   Success: {result.get("success")}')
    print(f'   Message: {result.get("message")}')
    # Tolerate if user already exists
    if status == 400 and 'email' in result.get('errors', {}):
        print('   User already exists, proceeding to login.')
    else:
        assert status == 201, f'Registration failed: {result}'

    # 2. Login
    print('\n2. LOGIN')
    status, result = api_call('login', {
        'email': email,
        'password': password,
    })
    print(f'   Status: {status}')
    assert status == 200, f'Login failed: {result}'
    
    access_token = result['data']['access']
    refresh_token = result['data']['refresh']
    user = result['data']['user']
    print(f'   User: {user["full_name"]} ({user["email"]})')
    print(f'   Access:  {access_token[:50]}...')
    print(f'   Refresh: {refresh_token[:50]}...')

    # 3. Get Profile
    print('\n3. GET PROFILE (/me/)')
    req = urllib.request.Request(
        f'{BASE_URL}/me/',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    resp = urllib.request.urlopen(req)
    profile = json.loads(resp.read())
    print(f'   Status: {resp.status}')
    print(f'   Name: {profile["full_name"]}')
    print(f'   Email: {profile["email"]}')
    print(f'   Verified: {profile["is_verified"]}')
    assert resp.status == 200

    # 4. Update Profile
    print('\n4. UPDATE PROFILE (PATCH /me/)')
    status, result = api_call('me', {
        'bio': 'Full-stack developer | Flutter & Django',
        'location': 'Mumbai, India',
        'hourly_rate': '25.00',
        'languages': ['English', 'Hindi'],
        'availability': 'available',
    }, method='PATCH', token=access_token)
    print(f'   Status: {status}')
    print(f'   Bio: {result["data"]["bio"]}')
    print(f'   Location: {result["data"]["location"]}')
    assert status == 200, f'Profile update failed: {result}'

    # 5. Logout
    print('\n5. LOGOUT')
    status, result = api_call('logout', {
        'refresh': refresh_token,
    }, token=access_token)
    print(f'   Status: {status}')
    print(f'   Message: {result.get("message")}')
    assert status == 200, f'Logout failed: {result}'

    print('\n' + '=' * 60)
    print('  ✅ ALL AUTH FLOW STEPS PASSED!')
    print('=' * 60)


if __name__ == '__main__':
    main()
