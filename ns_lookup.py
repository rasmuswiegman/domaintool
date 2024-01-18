#!/usr/bin/env python3

import dns.resolver
import sys

list = (sys.argv[1])

with open(list) as my_file:
        domains = my_file.readlines()

for domain in domains:
    print(' ' )
    try:
        #answersa = dns.resolver.resolve(domain.strip(), 'a')
        answersns = dns.resolver.resolve(domain.strip(), 'NS')
        #answersmx = dns.resolver.resolve(domain.strip(), 'MX')
        #answerstxt = dns.resolver.resolve(domain.strip(), 'txt')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            print(domain.strip(), 'Does not have any NS Record')
    else:
        #for ipval in answersa:
        #    print(domain.strip(), '- A -', ipval.to_text())
        for ipval in answersns:
            print(domain.strip(), '- NS -', ipval.to_text())
       # for ipval in answersmx:
       #     print(domain.strip(), '- MX -', ipval.to_text())
       # for ipval in answerstxt:
       #     print(domain, '- TXT - ', ipval.to_text())
