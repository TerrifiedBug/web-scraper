import requests

def get_public_ip():
    url = "https://ifconfig.co/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        data = response.json()
        print(f"Your Public IP: {data['ip']} ({data['asn_org']})")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP: {e}")

if __name__ == "__main__":
    get_public_ip()