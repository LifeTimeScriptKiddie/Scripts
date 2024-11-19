import requests
from xml.etree import ElementTree as ET

def get_ip_version(ip):
    # Determine if the IP is IPv4 or IPv6
    if ':' in ip:
        return "IPv6"
    else:
        return "IPv4"

def validate_ipv4(ip):
    # Validate the IP address part
    ip_parts = ip.split('.')
    if len(ip_parts) != 4:
        return False
    
    for part in ip_parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    
    return True

def validate_ipv4_cidr(ip_cidr):
    parts = ip_cidr.split('/')
    if len(parts) != 2:
        return False
    
    ip, cidr = parts
    
    # Validate the IP address part
    if not validate_ipv4(ip):
        return False
    
    # Validate the CIDR part
    try:
        cidr_value = int(cidr)
        if cidr_value < 0 or cidr_value > 32:
            return False
    except ValueError:
        return False
    
    return True

def fetch_fwri_version(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        
        root = ET.fromstring(response.content)
        fwri_version_element = root.find('.//FWRI/version')
        
        if fwri_version_element is not None:
            return fwri_version_element.text
        else:
            print("FWRI version element not found in the XML response.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the FWRI version: {e}")
        return None

def main():
    file_name = input("Enter the name of the file containing IPv4 addresses (with or without CIDR notation): ")
    
    try:
        with open(file_name, 'r') as file:
            ip_list = [line.strip() for line in file.readlines()]
        
        fwri_version_url = "https://ip/xmldata?item=All"
        fwri_version = fetch_fwri_version(fwri_version_url)
        
        if fwri_version is None:
            print("Unable to determine the FWRI version. Proceeding with default logic.")
        else:
            print(f"FWRI Version: {fwri_version}")
        
        for ip in ip_list:
            if '/' in ip:
                # Check if it's a valid IPv4 with CIDR
                if validate_ipv4_cidr(ip):
                    ip_part, cidr = ip.split('/')
                    version = get_ip_version(ip_part)
                    fwri_wrapped_version = f"FWRI{version}FWRI"
                    print(f"IP: {ip_part}, CIDR: /{cidr}, Version: {fwri_wrapped_version}")
                else:
                    print(f"Invalid IPv4/CIDR format: {ip}")
            else:
                # Check if it's a valid IPv4 without CIDR
                if validate_ipv4(ip):
                    version = get_ip_version(ip)
                    fwri_wrapped_version = f"FWRI{version}FWRI"
                    print(f"IP: {ip}, Version: {fwri_wrapped_version}")
                else:
                    print(f"Invalid IPv4 format: {ip}")
    
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
