#!/usr/bin/env python3

import dns.resolver
import dns.exception
import sys

# colors
GREEN = '\033[32;1m'
RED = '\033[91m'
ENDC = '\033[0m'


def get_dns_servers(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query for the NS (Name Server) records of the domain
        ns_response = dns.resolver.resolve(domain, 'NS')
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

def check_dnssec(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query the DS (Delegation Signer) record for the domain
        ds_response = dns.resolver.resolve(domain, 'DS')
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

def get_a_records(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query for the MX (MAIL Server) records of the domain
        a_response = dns.resolver.resolve(domain, 'A')
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

def get_mx_records(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query for the MX (MAIL Server) records of the domain
        mx_response = dns.resolver.resolve(domain, 'MX')
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

def get_txt_records(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query for the TXT records of the domain
        txt_response = dns.resolver.resolve(domain, 'TXT')
        print("TXT Records for", domain)
        for TXT in txt_response:
            print(TXT)
    except dns.resolver.NXDOMAIN:
        print("TXT Records not found for", domain)
    except dns.resolver.NoAnswer:
        print("No TXTRecords found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching TXT Records for", domain)
        print(e)

def print_help():
    print("Usage: ./dnssec.py <input_file> [OPTIONS]")
    print("OPTIONS:")
    print("  -h         Show this help message")
    print("  -all       Look up all")
    print("  -dns       Look up Nameservers")
    print("  -mx        Look up MX records")
    print("  -dnssec    Look up if DNSSEC is enabled")
    print("  -txt       Look up TXT Records")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()

    input_file = sys.argv[1]

    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()

    selected_functions = sys.argv[2:]

    with open(input_file, 'r') as file:
        domains = [line.strip() for line in file]

    for domain in domains:
        print()
        print(f"{RED}LOOKING UP {GREEN}{domain}{ENDC}")
        #print(f"{RED}LOOKING UP {domain}{ENDC}")
        #print(f"{RED}LOOKING UP", domain"{ENDC}")
        print()

        if '-all' in selected_functions or '-dns' in selected_functions:
            get_dns_servers(domain)

        if '-all' in selected_functions or '-dnssec' in selected_functions:
            check_dnssec(domain)

        if '-all' in selected_functions or '-mx' in selected_functions:
            get_mx_records(domain)

        if '-all' in selected_functions or '-txt' in selected_functions:
            get_txt_records(domain)

        if '-all' in selected_functions or '-a' in selected_functions:
            get_a_records(domain)

        print()
