import requests
import json
import random

def test():
    base_url = "http://localhost:8000/api"
    rnd = random.randint(1000, 9999)
    email_a = f'usera_{rnd}@example.com'
    email_b = f'userb_{rnd}@example.com'
    
    # Register A & B
    requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestClient', 'last_name': 'A',
        'email': email_a, 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestProvider', 'last_name': 'B',
        'email': email_b, 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    
    # Login A
    res = requests.post(f"{base_url}/auth/login/", json={'email': email_a, 'password': 'SuperSecretPassword123!'})
    token_a = res.json().get('data', {}).get('access')
    
    # Login B
    res = requests.post(f"{base_url}/auth/login/", json={'email': email_b, 'password': 'SuperSecretPassword123!'})
    token_b = res.json().get('data', {}).get('access')
    user_b_id = res.json().get('data', {}).get('user', {}).get('id')
    
    headers_a = {'Authorization': f'Bearer {token_a}'}
    headers_b = {'Authorization': f'Bearer {token_b}'}

    print("--- User A (Client) creates hire request ---")
    res = requests.post(f"{base_url}/hiring/", headers=headers_a, json={
        'provider': user_b_id,
        'title': 'Need help with Flutter',
        'description': 'Please fix this bug.',
        'budget': 50,
        'deadline': '2026-10-01'
    })
    request_id = res.json().get('id')
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- User B (Provider) accepts hire request ---")
    res = requests.post(f"{base_url}/hiring/{request_id}/status/", headers=headers_b, json={
        'action': 'accept'
    })
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- User B (Provider) starts job ---")
    res = requests.post(f"{base_url}/hiring/{request_id}/status/", headers=headers_b, json={
        'action': 'start'
    })
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Check User A's Notifications ---")
    res = requests.get(f"{base_url}/notifications/", headers=headers_a)
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Check User A's Conversations (Inbox) ---")
    res = requests.get(f"{base_url}/messages/conversations/", headers=headers_a)
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Check User B's Conversations (Inbox) ---")
    res = requests.get(f"{base_url}/messages/conversations/", headers=headers_b)
    print(json.dumps(res.json(), indent=2))

if __name__ == '__main__':
    test()
