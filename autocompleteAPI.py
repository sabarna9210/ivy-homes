
import requests
import time
from itertools import product

class APIScraper:
    def __init__(self, version=1):
        self.version = version
        self.base_url = f"http://35.200.185.69:8000/v{version}/autocomplete"
        self.alphabet = self._get_alphabet()
        self.results = set()
        self.request_count = 0
        self.delay = 60  # Initial delay of 1 minute
        self.limit = self._get_limit()

    def _get_alphabet(self):
        if self.version == 1:
            return "abcdefghijklmnopqrstuvwxyz"
        elif self.version == 2: 
            return "abcdefghijklmnopqrstuvwxyz0123456789"
        else : return "abcdefghijklmnopqrstuvwxyz0123456789_+-. "


    def _get_limit(self):
        #we have different limits of api calling and different query values for different versions which I have calculated  by the rateLimit.py function 
        if self.version == 1:
            return 100
        elif self.version == 2:
            return 50
        return 80

    def _fetch_query(self, query):
        url = f"{self.base_url}?query={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                self.results.update(data["results"])
            
            self.request_count += 1
            print(f"Fetched: {query} (Request {self.request_count})")

            return True
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"Rate limit hit! Retrying after {self.delay}s...")
                time.sleep(self.delay)
                return False
            else:
                print(f"Error fetching {query}: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error fetching {query}: {e}")
            return False

    def run(self):
        # If version != 1, process single-character queries first ans in Version 1   we do not need to store single letter query as it is already covered in two letter query
        if self.version != 1:
            for char in self.alphabet:
                self._fetch_query(char)

        # Process two-letter queries
        for i, j in product(self.alphabet, repeat=2):
            query = i + j
            success = self._fetch_query(query)

            # Rate limit handling
            if self.request_count % self.limit == 0:
                print(f"Pausing for {self.delay} seconds to avoid rate limits...")
                time.sleep(self.delay)

            # Increase delay on failure
            if not success:
                self.delay *= 2

        print(f"\nTotal Unique Results from v{self.version}: {len(self.results)}")
        print(self.results)
        self._save_results()

    def _save_results(self):
        filename = f"results_v{self.version}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for item in sorted(self.results):  # Sorting results for readability
                f.write(f"{item}\n")
        print(f"Results saved to {filename}")

if __name__ == "__main__":

    scraper = APIScraper(version=2)
    results = scraper.run()
