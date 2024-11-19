import re
import requests
from xml.etree import ElementTree as ET

def get_ip_version(ip):
    # Determine if the IP is IPv4 or IPv6
    if ':' in ip:
        return "IPv6"
    else:
        return "IPv4"

def validate_ip_cidr(ip_cidr):
    # Regular expression to match IPv4 and IPv6 with CIDR notation
    ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}/(8|16|24|32)$')
    ipv6_pattern = re.compile(r'^([0-9a-fA-F:]+)/(1[0-2][0-8]|1[0-1][0-9]|[1-9]?[0-9])$')
    
    if ipv4_pattern.match(ip_cidr):
        return True
    elif ipv6_pattern.match(ip_cidr):
        return True
    else:
        return False

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
    file_name = input("Enter the name of the file containing IP addresses with CIDR notation: ")
    
    try:
        with open(file_name, 'r') as file:
            ip_cidr_list = [line.strip() for line in file.readlines()]
        
        fwri_version_url = "https://ip/xmldata?item=All"
        fwri_version = fetch_fwri_version(fwri_version_url)
        
        if fwri_version is None:
            print("Unable to determine the FWRI version. Proceeding with default logic.")
        else:
            print(f"FWRI Version: {fwri_version}")
        
        for ip_cidr in ip_cidr_list:
            if validate_ip_cidr(ip_cidr):
                ip, cidr = ip_cidr.split('/')
                version = get_ip_version(ip)
                fwri_wrapped_version = f"FWRI{version}FWRI"
                print(f"IP: {ip}, CIDR: /{cidr}, Version: {fwri_wrapped_version}")
            else:
                print(f"Invalid IP/CIDR format: {ip_cidr}")
    
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
