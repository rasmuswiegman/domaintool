# domain-tool

Created by Rasmus Wiegman \ admin@latency.dk


Python script to gather information, regarding domains in a list

Usage domaintool.py

 Usage: ./domaintool.py -f <file_path> [OPTIONS]
        ./domaintool.py [OPTIONS] <domain1> <domain2> ...

OPTIONS:
  -h            Show this help message
  -f            Set filepath
  -all          Look up all
  -dns          Look up Nameservers
  -mx           Look up MX records
  -dnssec/ds    Look up if DNSSEC is enabled
  -txt          Look up TXT Records
  -a            Look up A Records
  -r            Perform reverse lookup from IP