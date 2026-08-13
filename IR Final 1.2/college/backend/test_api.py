import requests

API_URL = 'http://127.0.0.1:5000/api'

def test_endpoints():
    endpoints = [
        ('/health', 'GET'),
        ('/statistics', 'GET'),
        ('/colleges', 'GET'),
        ('/recommend-colleges?rank=50000&category=OBC', 'GET'),
        ('/admission-probability?rank=15000&category=GM&college_id=3&branch=CSE', 'GET'),
        ('/cutoff-trends?college_id=3&branch=CSE', 'GET')
    ]
    
    for endpoint, method in endpoints:
        print(f'Testing {endpoint}...')
        try:
            if method == 'GET':
                response = requests.get(API_URL + endpoint)
            
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print('Success!')
            else:
                print(f'Failed: {response.text[:200]}')
        except Exception as e:
            print(f'Error: {str(e)}')
        print('-'*40)

if __name__ == '__main__':
    test_endpoints()
