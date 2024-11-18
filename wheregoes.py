from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

proxies = {
    "http://": "socks5://127.0.0.1:9050",
    "https://": "socks5://127.0.0.1:9050"
}

starting_number = 20241111111
total_requests = 8888888
max_threads = 20  # Number of concurrent threads

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
                print(f"URL: {url} - %d Extracted Final URL: {final_url}")
                return number, final_url
            else:
                print(f"URL: {url} - No URL textarea found in the trace.")
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

with open("wheregoesURLs.txt", "a") as file:
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        
        futures = [executor.submit(grab_url, starting_number + i) for i in range(total_requests)]
        
        for future in as_completed(futures):
            number, final_url = future.result()
            if final_url:
                file.write(f"{number} | {final_url}\n")
