import requests

def get_version_from_url(ip, protocol="https"):
    """
    Fetches the <FRWI>version</FRWI> value from the given URL.
    Tries both HTTPS and HTTP if necessary.
    """
    url = f"{protocol}://{ip}/xmldata?item=All"
    try:
        response = requests.get(url, verify=False, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP/HTTPS issues
        # Look for <FRWI>version</FRWI> in the response content
        start_tag = "<FRWI>version</FRWI>"
        start_index = response.text.find(start_tag)
        if start_index != -1:
            version_start = start_index + len(start_tag)
            version_end = response.text.find("<", version_start)
            version = response.text[version_start:version_end].strip()
            return version
        else:
            return "<FRWI>version</FRWI> tag not found"
    except requests.RequestException as e:
        return f"Error: {e}"

def validate_and_check_ips(file_path):
    """
    Processes a file containing IP addresses (with or without CIDR) and fetches <FRWI>version</FRWI>.
    """
    try:
        with open(file_path, 'r') as file:
            ip_list = [line.strip().split('/')[0] for line in file if line.strip()]
        
        for ip in ip_list:
            print(f"Checking IP: {ip}")
            
            # Try HTTPS first, then HTTP if HTTPS fails
            version = get_version_from_url(ip, protocol="https")
            if "Error" in version:  # If HTTPS fails, try HTTP
                print("  HTTPS failed, trying HTTP...")
                version = get_version_from_url(ip, protocol="http")
            
            print(f"  Version: {version}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Enter the file path containing the list of IP addresses:")
    file_path = input().strip()
    validate_and_check_ips(file_path)

if __name__ == "__main__":
    main()
