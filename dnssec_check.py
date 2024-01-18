#!/usr/bin/env python3

import dns.resolver
import dns.message
import dns.query
import dns.rdatatype
import sys

def get_dns_servers(domain):
    # Set up a DNS resolver
    resolver = dns.resolver.Resolver()

    try:
        # Query for the NS (Name Server) records of the domain
        ns_response = dns.resolver.resolve(domain, 'NS')
        print("DNS Servers (NS) for", domain)
        for ns in ns_response:
            print(ns)
    except dns.resolver.NXDOMAIN:
        print("DNS Servers (NS) not found for", domain)
    except dns.resolver.NoAnswer:
        print("No DNS Servers (NS) found for", domain)
    except dns.exception.DNSException as e:
        print("Error while fetching DNS Servers (NS) for", domain)
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, 'r') as file:
        domains = [line.strip() for line in file]

    for domain in domains:
        print()
        check_dnssec(domain)
        get_dns_servers(domain)
        print()
