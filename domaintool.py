#!/usr/bin/env python3

import dns.resolver
import dns.reversename
import sys
import whois
import threading
import concurrent.futures
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from io import StringIO
import contextlib

# Colors
class Colors:
    GREEN = '\033[32;1m'
    RED = '\033[91m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'

@dataclass
class QueryResult:
    success: bool
    data: Any = None
    error: str = None

class DNSLookup:
    def __init__(self, resolver: dns.resolver.Resolver):
        self.resolver = resolver
        self.lock = threading.Lock()

    def _safe_resolve(self, domain: str, record_type: str) -> QueryResult:
        """Thread-safe DNS resolution with unified error handling"""
        try:
            with self.lock:
                response = self.resolver.resolve(domain, record_type)
            return QueryResult(success=True, data=list(response))
        except dns.resolver.NXDOMAIN:
            return QueryResult(success=False, error=f"NXDOMAIN")
        except dns.resolver.NoAnswer:
            return QueryResult(success=False, error=f"NoAnswer")
        except dns.exception.DNSException as e:
            return QueryResult(success=False, error=str(e))

    def get_a_records(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'A')
        output.write(f"{Colors.YELLOW}A Records for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No A Records found ({result.error}) for {domain}{Colors.ENDC}\n")

    def get_dns_servers(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'NS')
        output.write(f"{Colors.YELLOW}DNS Servers for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No DNS Servers found ({result.error}) for {domain}{Colors.ENDC}\n")

    def check_dnssec(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'DS')
        if result.success:
            output.write(f"{Colors.YELLOW}DNSSEC is enabled for {domain}{Colors.ENDC}\n")
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}DNSSEC not enabled ({result.error}) for {domain}{Colors.ENDC}\n")

    def get_mx_records(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'MX')
        output.write(f"{Colors.YELLOW}MX Records for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No MX Records found ({result.error}) for {domain}{Colors.ENDC}\n")

    def get_cname_records(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'cname')
        output.write(f"{Colors.YELLOW}cname Records for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No CNAME Records found ({result.error}) for {domain}{Colors.ENDC}\n")

    def get_txt_records(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(domain, 'TXT')
        output.write(f"{Colors.YELLOW}TXT records for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No TXT Records found ({result.error}) for {domain}{Colors.ENDC}\n")

    def get_dmarc_policy(self, domain: str, output: StringIO) -> None:
        result = self._safe_resolve(f'_dmarc.{domain}', 'TXT')
        output.write(f"{Colors.YELLOW}DMARC Policy for {domain}{Colors.ENDC}\n")
        if result.success:
            for record in result.data:
                output.write(f"{Colors.GREEN}{record}{Colors.ENDC}\n")
        else:
            output.write(f"{Colors.RED}No DMARC Policy found ({result.error}) for {domain}{Colors.ENDC}\n")

    def reverse_lookup(self, ip: str, output: StringIO = None) -> None:
        if output is None:
            output = sys.stdout
            direct_print = True
        else:
            direct_print = False
            
        try:
            reversed_ip = dns.reversename.from_address(ip)
            with self.lock:
                ptr_response = self.resolver.query(reversed_ip, 'PTR')
            
            if direct_print:
                print(f"{Colors.YELLOW}Reverse Lookup for {ip}{Colors.ENDC}")
                for ptr_record in ptr_response:
                    print(f"{Colors.GREEN}{ptr_record}{Colors.ENDC}")
            else:
                output.write(f"{Colors.YELLOW}Reverse Lookup for {ip}{Colors.ENDC}\n")
                for ptr_record in ptr_response:
                    output.write(f"{Colors.GREEN}{ptr_record}{Colors.ENDC}\n")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            msg = f"{Colors.RED}No PTR record found for {ip}{Colors.ENDC}"
            if direct_print:
                print(msg)
            else:
                output.write(f"{msg}\n")
        except dns.exception.DNSException as e:
            msg = f"{Colors.RED}Error during reverse lookup for {ip}: {e}{Colors.ENDC}"
            if direct_print:
                print(msg)
            else:
                output.write(f"{msg}\n")
        except Exception as e:
            msg = f"{Colors.RED}Unexpected error during reverse lookup for {ip}: {e}{Colors.ENDC}"
            if direct_print:
                print(msg)
            else:
                output.write(f"{msg}\n")

class WHOISLookup:
    @staticmethod
    def get_whois_info(domain: str, output: StringIO = None) -> None:
        if output is None:
            output = sys.stdout
            direct_print = True
        else:
            direct_print = False
            
        try:
            if direct_print:
                print(f"{Colors.YELLOW}WHOIS Information for {domain}{Colors.ENDC}")
            else:
                output.write(f"{Colors.YELLOW}WHOIS Information for {domain}{Colors.ENDC}\n")
            
            w = whois.whois(domain)
            
            # Helper function to handle list/single value fields
            def get_first_value(value):
                return value[0] if isinstance(value, list) and value else value
            
            # Helper function to format datetime
            def format_datetime(dt):
                if isinstance(dt, datetime):
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                return str(dt) if dt else "N/A"
            
            # Display information using dictionary mapping for cleaner code
            info_fields = {
                'Domain Name': get_first_value(w.domain_name),
                'Registrar': w.registrar,
                'Creation Date': format_datetime(get_first_value(w.creation_date)),
                'Expiration Date': format_datetime(get_first_value(w.expiration_date)),
                'Updated Date': format_datetime(get_first_value(w.updated_date)),
                'Organization': w.org,
                'Country': w.country
            }
            
            for field_name, value in info_fields.items():
                if value:
                    msg = f"{Colors.GREEN}{field_name}: {value}{Colors.ENDC}"
                    if direct_print:
                        print(msg)
                    else:
                        output.write(f"{msg}\n")
            
            # Handle name servers separately
            if w.name_servers:
                msg = f"{Colors.GREEN}Name Servers:{Colors.ENDC}"
                if direct_print:
                    print(msg)
                else:
                    output.write(f"{msg}\n")
                for ns in w.name_servers:
                    msg = f"{Colors.GREEN}  {ns}{Colors.ENDC}"
                    if direct_print:
                        print(msg)
                    else:
                        output.write(f"{msg}\n")
            
            # Handle status separately
            if w.status:
                status_list = w.status if isinstance(w.status, list) else [w.status]
                msg = f"{Colors.GREEN}Status:{Colors.ENDC}"
                if direct_print:
                    print(msg)
                else:
                    output.write(f"{msg}\n")
                for status in status_list:
                    msg = f"{Colors.GREEN}  {status}{Colors.ENDC}"
                    if direct_print:
                        print(msg)
                    else:
                        output.write(f"{msg}\n")
                    
        except Exception as e:
            msg = f"{Colors.RED}Error fetching WHOIS for {domain}: {e}{Colors.ENDC}"
            if direct_print:
                print(msg)
            else:
                output.write(f"{msg}\n")

class DomainProcessor:
    def __init__(self, resolver: dns.resolver.Resolver):
        self.dns_lookup = DNSLookup(resolver)
        self.whois_lookup = WHOISLookup()
        
        # Lookup method mapping for cleaner code
        self.lookup_methods = {
            'ns': self.dns_lookup.get_dns_servers,
            'a': self.dns_lookup.get_a_records,
            'mx': self.dns_lookup.get_mx_records,
            'dnssec': self.dns_lookup.check_dnssec,
            'txt': self.dns_lookup.get_txt_records,
            'cname': self.dns_lookup.get_cname_records,
            'dmarc': self.dns_lookup.get_dmarc_policy,
            'who': self.whois_lookup.get_whois_info
        }

    def process_single_domain(self, domain: str, options: List[str]) -> str:
        """Process a single domain and return formatted output"""
        output = StringIO()
        output.write(f"\n{Colors.YELLOW}LOOKING UP {domain}{Colors.ENDC}\n\n")
        
        # Determine which lookups to perform
        if '-all' in options:
            lookups_to_perform = list(self.lookup_methods.keys())
        else:
            lookups_to_perform = []
            for opt in options:
                lookup_key = opt.lstrip('-')
                if lookup_key in self.lookup_methods:
                    lookups_to_perform.append(lookup_key)
                elif lookup_key == 'dns':  # Handle -dns alias for -ns
                    lookups_to_perform.append('ns')
        
        # Perform lookups
        for lookup in lookups_to_perform:
            if lookup in self.lookup_methods:
                self.lookup_methods[lookup](domain, output)
                output.write("\n")  # Add spacing between different record types
        
        return output.getvalue()

    def process_domains_parallel(self, domains: List[str], options: List[str], max_workers: int = 5) -> None:
        """Process multiple domains in parallel but display results sequentially"""
        if len(domains) == 1:
            # Single domain - no need for threading overhead
            result = self.process_single_domain(domains[0], options)
            print(result, end='')
        else:
            # Multiple domains - use threading for parallel processing but collect results
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks and maintain order
                future_to_domain = {
                    executor.submit(self.process_single_domain, domain, options): domain 
                    for domain in domains
                }
                
                # Collect results in the order they were submitted
                results = {}
                for future in concurrent.futures.as_completed(future_to_domain):
                    domain = future_to_domain[future]
                    try:
                        results[domain] = future.result()
                    except Exception as e:
                        results[domain] = f"\n{Colors.RED}Error processing {domain}: {e}{Colors.ENDC}\n"
                
                # Print results in original order
                for domain in domains:
                    if domain in results:
                        print(results[domain], end='')

    def process_ip(self, ip: str, options: List[str]) -> None:
        """Process IP address lookups"""
        print(f"\n{Colors.YELLOW}LOOKING UP IP - {ip}{Colors.ENDC}\n")
        if '-r' in options:
            self.dns_lookup.reverse_lookup(ip)
        print()

def setup_resolver(custom_dns: Optional[str] = None, timeout: int = 2) -> dns.resolver.Resolver:
    """Setup and configure DNS resolver"""
    resolver = dns.resolver.Resolver()
    if custom_dns:
        resolver.nameservers = [custom_dns]
    resolver.timeout = timeout
    resolver.lifetime = timeout * 2  # Total time including retries
    return resolver

def load_domains_from_file(file_path: str) -> List[str]:
    """Load domains from file with error handling"""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{file_path}' not found.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error reading file '{file_path}': {e}{Colors.ENDC}")
        sys.exit(1)

def parse_arguments(args: List[str]) -> Dict[str, Any]:
    """Parse command line arguments into structured format"""
    parsed = {
        'options': [],
        'domains': [],
        'file_path': None,
        'ip': None,
        'custom_dns': None
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-f':
            i += 1
            if i < len(args):
                parsed['file_path'] = args[i]
            else:
                print(f"{Colors.RED}Error: Missing file path after '-f'.{Colors.ENDC}")
                sys.exit(1)
        elif arg == '-r':
            i += 1
            if i < len(args):
                parsed['ip'] = args[i]
            else:
                print(f"{Colors.RED}Error: Missing IP address after '-r'.{Colors.ENDC}")
                sys.exit(1)
        elif arg in ['-d', '--dns-server']:
            i += 1
            if i < len(args):
                parsed['custom_dns'] = args[i]
            else:
                print(f"{Colors.RED}Error: Missing custom DNS server after '-d' or '--dns-server'.{Colors.ENDC}")
                sys.exit(1)
        elif arg.startswith('-'):
            parsed['options'].append(arg)
        else:
            parsed['domains'].append(arg)
        i += 1
    
    return parsed

def print_help():
    help_text = """
Usage: ./domaintool.py -f <file_path> [OPTIONS]
       ./domaintool.py [OPTIONS] <domain1> <domain2> ...

OPTIONS:
  -h, --help     Show this help message
  -all           Look up all record types
  -dns, -ns      Look up Nameservers
  -mx            Look up MX records
  -dnssec        Look up DNSSEC status
  -txt           Look up TXT Records
  -a             Look up A Records
  -dmarc         Look up DMARC Policy
  -who           Look up WHOIS information
  -r <ip>        Perform reverse lookup from IP
  -d, --dns-server <server>  Specify custom DNS server
  -f <file>      Read domains from file

Examples:
  ./domaintool.py -all example.com
  ./domaintool.py -a -mx example.com google.com
  ./domaintool.py -f domains.txt -who
  ./domaintool.py -r 8.8.8.8
"""
    print(help_text)
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print_help()

    # Parse arguments
    parsed_args = parse_arguments(sys.argv[1:])
    
    # Handle help
    if '-h' in parsed_args['options'] or '--help' in parsed_args['options']:
        print_help()

    # Validate input
    if not any([parsed_args['file_path'], parsed_args['domains'], parsed_args['ip']]):
        print(f"{Colors.RED}Error: At least one domain, file path, or IP address must be provided.{Colors.ENDC}")
        print_help()

    # Setup resolver
    resolver = setup_resolver(parsed_args['custom_dns'])
    print(f"{Colors.YELLOW}Using DNS Server: {resolver.nameservers}{Colors.ENDC}")

    # Initialize processor
    processor = DomainProcessor(resolver)

    # Process requests
    if parsed_args['file_path']:
        domains = load_domains_from_file(parsed_args['file_path'])
        processor.process_domains_parallel(domains, parsed_args['options'])

    if parsed_args['domains']:
        processor.process_domains_parallel(parsed_args['domains'], parsed_args['options'])

    if parsed_args['ip']:
        processor.process_ip(parsed_args['ip'], parsed_args['options'])

if __name__ == "__main__":
    main()
