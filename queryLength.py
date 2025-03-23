import requests

def query_length(base_url):
    low, high = 1, 1000  
    response_ok = True

    # Find an upper bound where the request fails
    while response_ok and high <= 100000:
        if requests.get(base_url, params={'query': 'a' * high}).status_code == 400:
            response_ok = False
        else:
            low, high = high, high * 2

    max_valid, last_valid_response = low, None

    # Binary search for the exact limit
    while low <= high:
        mid = (low + high) // 2
        response = requests.get(base_url, params={'query': 'a' * mid})

        try:
            response_data = response.json()
            if response.status_code == 200 and isinstance(response_data, dict) and 'results' in response_data:
                last_valid_response = response_data
                max_valid, low = mid, mid + 1
            else:
                high = mid - 1
        except:
            high = mid - 1

    # Check if API truncates longer queries or strictly limits them
    is_strict = True
    if max_valid > 0:
        response = requests.get(base_url, params={'query': 'a' * (max_valid + 10)})
        if response.status_code == 200 and response.json() == last_valid_response:
            is_strict = False

    return max_valid, is_strict

