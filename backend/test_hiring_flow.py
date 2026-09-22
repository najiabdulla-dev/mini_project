import requests
import json
import sqlite3
import random

def run_test():
    base_url = "http://localhost:8000/api"
    
    rnd = random.randint(1000, 9999)
    email_a = f'usera_{rnd}@example.com'
    email_b = f'userb_{rnd}@example.com'

    print("\n--- SETUP: Creating test users via API ---")
    
    # Create User A
    res_reg_a = requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestClient', 'last_name': 'A',
        'email': email_a, 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    print(f"Register User A: {res_reg_a.status_code}, {res_reg_a.text}")
    
    # Create User B (Tony)
    res_reg_b = requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestProvider', 'last_name': 'B',
        'email': email_b, 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    print(f"Register User B: {res_reg_b.status_code}, {res_reg_b.text}")

    # Login User A
    res = requests.post(f"{base_url}/auth/login/", json={'email': email_a, 'password': 'SuperSecretPassword123!'})
    token_a = res.json().get('data', {}).get('access')
    if not token_a:
        print("Login A failed:", res.text)
        return
    headers_a = {'Authorization': f'Bearer {token_a}'}
    user_a_id = res.json()['data']['user']['id']

    # Login User B
    res = requests.post(f"{base_url}/auth/login/", json={'email': email_b, 'password': 'SuperSecretPassword123!'})
    token_b = res.json().get('data', {}).get('access')
    headers_b = {'Authorization': f'Bearer {token_b}'}
    user_b_id = res.json()['data']['user']['id']

    print(f"\nUser A ID: {user_a_id}, User B ID: {user_b_id}")

    print("\n=== STEP 1: Firing API call to create Hire Request (Simulating Flutter Send) ===")
    payload = {
        'provider': user_b_id,
        'title': 'Need help with Flutter',
        'description': 'Please fix this bug.',
        'budget': 50,
        'deadline': '2026-10-01'
    }
    print(f"PAYLOAD SENT: {json.dumps(payload, indent=2)}")
    
    res = requests.post(f"{base_url}/hiring/", json=payload, headers=headers_a)
    print(f"RESPONSE STATUS: {res.status_code}")
    print(f"RESPONSE BODY: {json.dumps(res.json(), indent=2)}")
    
    hire_request_id = res.json().get('data', res.json()).get('id', None)

    print("\n=== STEP 2: Prove what's actually in the database ===")
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Try finding it in hiring_hirerequest or similar
    table_name = next((t[0] for t in tables if 'hiring' in t[0] or 'request' in t[0].lower()), 'hiring_hirerequest')
    cursor.execute(f"SELECT id, client_id, provider_id, status, created_at FROM {table_name} WHERE id = ?", (hire_request_id,))
    row = cursor.fetchone()
    if row:
        print(f"Row found in DB: id={row[0]}, client_id={row[1]}, provider_id={row[2]}, status={row[3]}, created_at={row[4]}")
    else:
        print("NO ROW FOUND IN DB!")

    print("\n=== STEP 3: Prove what each list screen actually queries ===")
    print("Exact Django queryset from views.py:")
    print("return HireRequest.objects.filter(Q(client=user) | Q(provider=user)).select_related('client', 'provider')")

    print("\n--- FETCHING INCOMING REQUESTS FOR TONY (USER B) ---")
    print("Simulating fresh GET request on screen load...")
    res = requests.get(f"{base_url}/hiring/", headers=headers_b)
    print(f"RESPONSE STATUS: {res.status_code}")
    print(f"RAW RESPONSE BODY FOR TONY: {json.dumps(res.json(), indent=2)}")

    print("\n--- FETCHING OUTGOING REQUESTS FOR CLIENT (USER A) ---")
    res = requests.get(f"{base_url}/hiring/", headers=headers_a)
    print(f"RESPONSE STATUS: {res.status_code}")
    print(f"RAW RESPONSE BODY FOR USER A: {json.dumps(res.json(), indent=2)}")

if __name__ == '__main__':
    run_test()
