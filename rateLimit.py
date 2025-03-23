import requests
import time

def find_rate_limit(base_url):
    initial_delay = 2.0       # Start with a safe delay (seconds)
    delay_decrement = 0.05    # Decrease delay by 0.05s each test
    delay_increment = 0.01    # Increase delay by 0.01s to fine-tune the limit
    min_delay = 0.05          # Minimum delay to test (20 req/s)
    batch_size = 10           # Number of requests per test batch
    cooldown = 5              # Wait time between test runs (seconds)

    current_delay = initial_delay
    safe_config = None

    # Phase 1: Decrease delay until a 429 response is received.
    while current_delay >= min_delay:
        rate_limited = False
        req_times = []
        for _ in range(batch_size):
            start = time.monotonic()
            response = requests.get(base_url, params={'query': 'a'})
            req_times.append(time.monotonic() - start)
            if response.status_code == 429:
                rate_limited = True
                break
            time.sleep(current_delay)
        avg_req_time = sum(req_times) / len(req_times) if req_times else 0
        achieved_rps = 1 / (avg_req_time + current_delay) if (avg_req_time + current_delay) > 0 else 0

        if not rate_limited:
            safe_config = {'delay': current_delay, 'rps': achieved_rps}
            print(f"Safe at delay {current_delay:.2f}s with {achieved_rps:.1f} req/s")
            current_delay = round(current_delay - delay_decrement, 2)
        else:
            print(f"Rate limit hit at delay {current_delay:.2f}s")
            break

        time.sleep(cooldown)

    if safe_config is None:
        print("Rate limit hit even at the initial delay.")
        return None

    # Phase 2: Fine-tune by increasing the delay until 429 is avoided.
    exact_delay = safe_config['delay']
    while True:
        test_delay = round(exact_delay + delay_increment, 2)
        rate_limited = False
        req_times = []
        for _ in range(batch_size):
            start = time.monotonic()
            response = requests.get(base_url, params={'query': 'a'})
            req_times.append(time.monotonic() - start)
            if response.status_code == 429:
                rate_limited = True
                break
            time.sleep(test_delay)
        if not rate_limited:
            exact_delay = test_delay
            print(f"Found exact safe delay: {exact_delay:.2f}s")
            break
        else:
            exact_delay = test_delay
            print(f"Increasing delay to {exact_delay:.2f}s due to rate limit.")
            time.sleep(cooldown)

    avg_req_time = sum(req_times) / len(req_times) if req_times else 0
    achieved_rps = 1 / (avg_req_time + exact_delay) if (avg_req_time + exact_delay) > 0 else 0
    safe_config = {'delay': exact_delay, 'rps': achieved_rps}
    print(f"\nMax sustainable RPS: {safe_config['rps']:.1f} (Exact Delay: {safe_config['delay']}s)")
    return safe_config

# Example usage
safe_config = find_rate_limit("http://35.200.185.69:8000/v2/autocomplete")
