#!/usr/bin/env python3

import dns.resolver
import sys
import dns.dnssec

list = sys.argv[1]

with open(list) as my_file:
    domains = my_file.readlines()

for domain in domains:
    print(' ')
    try:
        answersns = dns.resolver.resolve(domain.strip(), 'NS')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        print(domain.strip(), 'Does Not have any NS Record')
    try:
        answersmx = dns.resolver.resolve(domain.strip(), 'MX')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        print(domain.strip(), 'Does Not have any MX Record')
    try:
        answerstxt = dns.resolver.resolve(domain.strip(), 'txt')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        print(domain.strip(), 'Does not have any TXT Record')
    else:
        for ipval in answersns:
            print(domain.strip(), '- NS -', ipval.to_text())
        for ipval in answersmx:
            print(domain.strip(), '- MX -', ipval.to_text())
        for ipval in answerstxt:
            print(domain, '- TXT - ', ipval.to_text())
