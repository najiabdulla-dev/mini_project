import requests
import json
import random

def test():
    base_url = "http://localhost:8000/api"
    rnd = random.randint(1000, 9999)
    email_a = f'usera_{rnd}@example.com'
    
    requests.post(f"{base_url}/auth/register/", json={
        'first_name': 'TestClient', 'last_name': 'A',
        'email': email_a, 'password': 'SuperSecretPassword123!', 'password_confirm': 'SuperSecretPassword123!'
    })
    
    res = requests.post(f"{base_url}/auth/login/", json={'email': email_a, 'password': 'SuperSecretPassword123!'})
    token = res.json().get('data', {}).get('access')
    user_id = res.json().get('data', {}).get('user', {}).get('id')
    headers = {'Authorization': f'Bearer {token}'}

    print(f"--- FETCHING /profiles/{user_id}/ ---")
    res = requests.get(f"{base_url}/profiles/{user_id}/", headers=headers)
    print(f"STATUS: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == '__main__':
    test()
