from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

proxies = {
    "http://": "socks5://127.0.0.1:9050",
    "https://": "socks5://127.0.0.1:9050"
}

starting_number = 20241111111
total_requests = 8888888
max_threads = 10
max_failures = 10  # Every result should be within 10
failure_count = 0  # Tracks consecutive failures
current_number = starting_number


def grab_url(number):
    url = f"https://wheregoes.com/trace/{number}"
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            url_textarea = soup.find('textarea', class_='copy-url')
            if url_textarea:
                obfuscated_url = url_textarea.get_text()
                final_url = obfuscated_url.replace('|', '')
                print(f"URL: {url} - Extracted Final URL: {final_url}")
                return number, final_url
            else:
                print(f"URL: {url} - Error - textarea not found in the trace.")
                return number, None
        else:
            print(f"URL: {url} - Status Code: {response.status_code}")
            return number, None
    except requests.exceptions.ProxyError:
        print(f"Proxy error while connecting to {url}. Proxy might be down.")
        return number, None
    except requests.exceptions.RequestException as e:
        print(f"Error with request to {url}: {e}")
        return number, None


while True:
    with open("wheregoesURLs.txt", "a") as file:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(grab_url, current_number + i) for i in range(max_threads)]

            for future in as_completed(futures):
                number, final_url = future.result()
                if final_url:
                    file.write(f"{number} | {final_url}\n")
                    failure_count = 0  # Reset failures so it'll increase the minimum number
                else:
                    failure_count += 1  # Increment failures if the result 404s
                    print(f"Fail Count: {failure_count}/10")

                # Test if you're at the front of results
                #   if so then jump back 10 & recheck since it'll grab the latest
                if failure_count >= max_failures:
                    print("Too many failures. Rechecking earlier numbers...\n")
                    current_number = max(starting_number, current_number - max_failures)
                    failure_count = 0
                    break

    # Increment the starting number for the next batch
    current_number += max_threads

    
