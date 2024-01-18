#!/usr/bin/env python3

import dns.resolver
import sys

list = (sys.argv[1])

with open(list) as my_file:
        domains = my_file.readlines()

for domain in domains:
    print(' ' )
    try:
       answersns = dns.resolver.resolve(domain.strip(), 'NS')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            print(domain.strip(), 'Does not have any NS Record')
    else:
        for ipval in answersns:
            print(domain.strip(), '- NS -', ipval.to_text())
