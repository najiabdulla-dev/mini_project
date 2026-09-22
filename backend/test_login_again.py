import urllib.request
import json
import urllib.error

def test_login():
    url = 'http://127.0.0.1:8000/api/auth/login/'
    data = json.dumps({'email': 'demo2@test.com', 'password': 'DemoP@ss2'}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
        print("Success:", res.status)
    except urllib.error.HTTPError as e:
        print("Failed:", e.code, e.read().decode())

test_login()
