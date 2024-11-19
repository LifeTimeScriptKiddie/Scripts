import requests
import re
import sys

def get_version_from_url(ip, protocol="https"):
    """
    Fetches the value between <frwi></frwi> tags in the given URL.
    Matches a version in the format X.YY (e.g., 2.22, 3.44).
    """
    url = f"{protocol}://{ip}/xmldata?item=All"
    version_pattern = r"<frwi>(\d\.\d{2})</frwi>"  # Matches 'X.YY' format within <frwi> tags
    
    try:
        response = requests.get(url, verify=False, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP/HTTPS issues
        
        # Search for the version pattern in the response content
        match = re.search(version_pattern, response.text, re.IGNORECASE)  # Case-insensitive for <frwi>
        if match:
            return match.group(1)  # Return the matched version
        else:
            return None  # No version found
    except requests.RequestException:
        return None  # Suppress error messages and return None

def validate_and_check_ips(file_path):
    """
    Processes a file containing IP addresses (with or without CIDR) and fetches the value within <frwi></frwi>.
    Outputs results in the format: IP: <IP>   |    ILO_Version: <Version>
    """
    try:
        with open(file_path, 'r') as file:
            ip_list = [line.strip().split('/')[0] for line in file if line.strip()]
        
        for ip in ip_list:
            # Try HTTPS first, then HTTP if HTTPS fails
            version = get_version_from_url(ip, protocol="https")
            if not version:  # If HTTPS fails, try HTTP
                version = get_version_from_url(ip, protocol="http")
            
            # Only print if a valid version is found
            if version:
                print(f"IP: {ip}   |    ILO_Version: {version}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python ilo3.py <targetipsfile>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validate_and_check_ips(file_path)

if __name__ == "__main__":
    main()
