#!/usr/bin/env python3

import dns.resolver
import dns.exception
import socket
import sys

# colors
GREEN = '\033[32;1m'
RED = '\033[91m'
ENDC = '\033[0m'

def get_a_records(domain, resolver):
    try:
        a_response = resolver.resolve(domain, 'A')
        print("A Records for", domain)
        for A in a_response:
            print(A)
    except dns.resolver.NXDOMAIN:
        print("A Records not found for", domain)
    except dns.resolver.NoAnswer:
        print("No A Records found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching A records for", domain)
        print(e)

def get_dns_servers(domain, resolver):
    try:
        ns_response = resolver.resolve(domain, 'NS')
        print("DNS Servers for", domain)
        for ns in ns_response:
            print(ns)
    except dns.resolver.NXDOMAIN:
        print("DNS Servers not found for", domain)
    except dns.resolver.NoAnswer:
        print("No DNS Servers found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching DNS Servers for", domain)
        print(e)

def check_dnssec(domain, resolver):
    try:
        ds_response = resolver.resolve(domain, 'DS')
        print("DNSSEC is enabled for", domain)
        print("DS Records:")
        for record in ds_response:
            print(record)
    except dns.resolver.NXDOMAIN:
        print("DNSSEC is not enabled for", domain)
    except dns.resolver.NoAnswer:
        print("No DS records found for", domain)
    except dns.exception.DNSException as e:
        print("Error while checking DNSSEC for", domain)
        print(e)

def get_mx_records(domain, resolver):
    try:
        mx_response = resolver.resolve(domain, 'MX')
        print("MX Records for", domain)
        for MX in mx_response:
            print(MX)
    except dns.resolver.NXDOMAIN:
        print("MX Records not found for", domain)
    except dns.resolver.NoAnswer:
        print("No MX Records found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching Mail Servers for", domain)
        print(e)

def get_txt_records(domain, resolver):
    try:
        txt_response = resolver.resolve(domain, 'TXT')
        print("TXT Records for", domain)
        for TXT in txt_response:
            print(TXT)
    except dns.resolver.NXDOMAIN:
        print("TXT Records not found for", domain)
    except dns.resolver.NoAnswer:
        print("No TXT Records found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching TXT Records for", domain)
        print(e)

def reverse_lookup(ip):
    try:
        # Perform reverse lookup using socket
        domain = socket.gethostbyaddr(ip)[0]
        print(f"Reverse Lookup for {ip}: {domain}")
    except socket.herror as e:
        print(f"No PTR record found for {ip}")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"Error while performing reverse lookup for {ip}")
        print(f"Error details: {e}")

def process_domains(domains, options, resolver):
    for domain in domains:
        print()
        print(f"{RED}LOOKING UP {GREEN}{domain}{ENDC}")
        print()
        print("Used DNS Server:", resolver.nameservers)

        if '-all' in options or '-dns' in options:
            get_dns_servers(domain, resolver)

        if '-all' in options or '-a' in options:
            get_a_records(domain, resolver)

        if '-all' in options or '-mx' in options:
            get_mx_records(domain, resolver)

        if '-all' in options or '-dnssec' in options or '-ds' in options:
            check_dnssec(domain, resolver)

        if '-all' in options or '-txt' in options:
            get_txt_records(domain, resolver)
        
        if '-r' in options:
            reverse_lookup(ip)

        print()

def process_file(file_path, options, resolver):
    try:
        with open(file_path, 'r') as file:
            domains = [line.strip() for line in file]
            process_domains(domains, options, resolver)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def process_ip(ip, options):
    print()
    print(f"{RED}LOOKING UP {GREEN}{ip}{ENDC}")
    print()

def print_help():
    print("Usage: ./dnssec.py -f <file_path> [OPTIONS]")
    print("./dnssec.py [OPTIONS] <domain1> <domain2> ...")
    print("OPTIONS:")
    print("  -h             Show this help message")
    print("  -all           Look up all")
    print("  -dns           Look up Nameservers")
    print("  -mx            Look up MX records")
    print("  -dnssec/ds     Look up if DNSSEC is enabled")
    print("  -txt           Look up TXT Records")
    print("  -a             Look up A Records")
    print("  -r             Perform reverse lookup from IP")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()

    args = sys.argv[1:]
    options = []
    domains = []
    file_path = None
    ip = None

    # Separate file path, options, domains, and IP
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-f':
            i += 1
            if i < len(args):
                file_path = args[i]
            else:
                print("Error: Missing file path after '-f'.")
                sys.exit(1)
        elif arg == '-r':
            i += 1
            if i < len(args):
                ip = args[i]
            else:
                print("Error: Missing IP address after '-r'.")
                sys.exit(1)
        elif arg.startswith('-'):
            options.append(arg)
        else:
            domains.append(arg)
        i += 1

    if '-h' in options or '--help' in options:
        print_help()

    if not file_path and not domains and not ip:
        print("Error: At least one domain, a file path, or an IP address must be provided.")
        print_help()

    resolver = dns.resolver.Resolver()
    resolver.timeout = 1  # Set DNS timeout (adjust as needed)

    print("Using DNS Server:", resolver.nameservers)

    if file_path:
        process_file(file_path, options, resolver)

    if domains:
        process_domains(domains, options, resolver)

    if ip:
        process_ip(ip, options)

