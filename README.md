# domain-tool

Created by Rasmus Wiegman \ admin@latency.dk


Python script to gather information, regarding domains in a list

The DNSSEC_CHECK.py checks wether domains are DNSSEC Signed

The ns-info.py gathers only information regarding NS records

Usage dnssec.py

Usage: ./dnssec.py <input_file> [OPTIONS]

-h         Show this help message
-all       Look up all
-dns       Look up Nameservers
-mx        Look up MX records
-dnssec    Look up if DNSSEC is enabled
