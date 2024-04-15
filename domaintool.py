#!/usr/bin/env python3

import dns.resolver
import dns.reversename
import sys

# colors
GREEN = '\033[32;1m'
RED = '\033[91m'
YELLOW = '\033[33m'
ENDC = '\033[0m'

def get_a_records(domain, resolver):
    try:
        a_response = resolver.resolve(domain, 'A')
        print(f"{YELLOW}A Records for {domain}{ENDC}")
        for A in a_response:
            print(f"{GREEN}{A}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}No A Records not found for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No A Records found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while fetching A records for", domain)
        print(e)

def get_dns_servers(domain, resolver):
    try:
        ns_response = resolver.resolve(domain, 'NS')
        print(f"{YELLOW}DNS Servers for {domain}{ENDC}")
        for ns in ns_response:
            print(f"{GREEN}{ns}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}No DNS Servers found for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No DNS Servers found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while fetching DNS Servers for", domain)
        print(e)

def check_dnssec(domain, resolver):
    try:
        ds_response = resolver.resolve(domain, 'DS')
        print(f"{YELLOW}DNSSEC is enabled for {domain}{ENDC}")
        for record in ds_response:
            print(f"{GREEN}{record}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}DNSSEC is not enabled for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No DS Records found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while checking DNSSEC for", domain)
        print(e)

def get_mx_records(domain, resolver):
    try:
        mx_response = resolver.resolve(domain, 'MX')
        print(f"{YELLOW}MX Records for {domain}{ENDC}")
        for MX in mx_response:
            print(f"{GREEN}{MX}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}MX Records not found for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No MX Records found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while fetching Mail Servers for", domain)
        print(e)

def get_txt_records(domain, resolver):
    try:
        txt_response = resolver.resolve(domain, 'TXT')
        print(f"{YELLOW}TXT records for {domain}{ENDC}")
        for TXT in txt_response:
            print(f"{GREEN}{TXT}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}TXT Records not found for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No TXT Records found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while fetching TXT Records for", domain)
        print(e)

def get_dmarc_policy(domain, resolver):
    try:
        dmarc_response = resolver.resolve(f'_dmarc.{domain}', 'TXT')
        print(f"{YELLOW}DMARC Policy for {domain}{ENDC}")
        for record in dmarc_response:
            print(f"{GREEN}{record}{ENDC}")
    except dns.resolver.NXDOMAIN:
        print(f"{RED}DMARC Policy not found for (NXDOMAIN) {domain}{ENDC}")
    except dns.resolver.NoAnswer:
        print(f"{RED}No DMARC Policy found for (NoAnswer) {domain}{ENDC}")
    except dns.exception.DNSException as e:
        print("Error while fetching DMARC Policy for", domain)
        print(e)

def reverse_lookup(ip, resolver):
    try:
        reversed_ip = dns.reversename.from_address(ip)
        ptr_response = resolver.query(reversed_ip, 'PTR')

        print(f"Reverse Lookup for {ip}:")
        for ptr_record in ptr_response:
            print(ptr_record)
    except dns.resolver.NXDOMAIN:
        print(f"No PTR record found for {ip}")
    except dns.resolver.NoAnswer:
        print(f"No PTR record found for {ip}")
    except dns.exception.DNSException as e:
        print(f"Error while performing reverse lookup for {ip}")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"Unexpected error during reverse lookup for {ip}")
        print(f"Error details: {e}")

def process_domains(domains, options, resolver):
    for domain in domains:
        print()
        print(f"{YELLOW}LOOKING UP {domain}{ENDC}")
        print()

        if '-all' in options or '-dns' in options or '-ns' in options:
            get_dns_servers(domain, resolver)

        if '-all' in options or '-a' in options:
            get_a_records(domain, resolver)

        if '-all' in options or '-mx' in options:
            get_mx_records(domain, resolver)

        if '-all' in options or '-dnssec' in options:
            check_dnssec(domain, resolver)

        if '-all' in options or '-txt' in options:
            get_txt_records(domain, resolver)

        if '-all' in options or '-dmarc' in options:
            get_dmarc_policy(domain, resolver)
        print()

def process_file(file_path, options, resolver):
    try:
        with open(file_path, 'r') as file:
            domains = [line.strip() for line in file]
            process_domains(domains, options, resolver)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def process_ip(ip, options, resolver):
    print()
    print(f"{YELLOW}LOOKING UP IP - {ip}{ENDC}")
    print()

    if '-r' in options:
        reverse_lookup(ip, resolver)

    print()

def print_help():
    print("Usage: ./domaintool.py -f <file_path> [OPTIONS]")
    print("       ./domaintool.py [OPTIONS] <domain1> <domain2> ...")
    print("OPTIONS:")
    print("  -h         Show this help message")
    print("  -all       Look up all")
    print("  -dns       Look up Nameservers")
    print("  -ns        Same as -dns")
    print("  -mx        Look up MX records")
    print("  -dnssec    Look up if DNSSEC is enabled")
    print("  -txt       Look up TXT Records")
    print("  -a         Look up A Records")
    print("  -dmarc     Look up DMARC Policy")
    print("  -r         Perform reverse lookup from IP")
    print("  -d, --dns-server <custom_dns>  Specify a custom DNS server")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()

    args = sys.argv[1:]
    options = []
    domains = []
    file_path = None
    ip = None
    custom_dns = None

    # Separate file path, options, domains, IP, and custom DNS
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
        elif arg in ['-d', '--dns-server']:
            i += 1
            if i < len(args):
                custom_dns = args[i]
            else:
                print("Error: Missing custom DNS server after '-d' or '--dns-server'.")
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

    # Set custom DNS server if provided
    if custom_dns:
        resolver.nameservers = [custom_dns]

    resolver.timeout = 1  # Set DNS timeout (adjust as needed)

    print("Using DNS Server:", resolver.nameservers)

    if file_path:
        process_file(file_path, options, resolver)

    if domains:
        process_domains(domains, options, resolver)

    if ip:
        process_ip(ip, options, resolver)

