import requests
import json

def test():
    base_url = "http://localhost:8000/api"
    # Create User A
    res = requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestClient', 'last_name': 'A',
        'email': 'profiletest@example.com', 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    
    # Login User A
    res = requests.post(f"{base_url}/auth/login/", json={'email': 'profiletest@example.com', 'password': 'SuperSecretPassword123!'})
    token = res.json().get('data', {}).get('access')
    headers = {'Authorization': f'Bearer {token}'}

    print("--- FETCHING PROFILE ---")
    res = requests.get(f"{base_url}/profiles/me/", headers=headers)
    print(f"STATUS: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == '__main__':
    test()
