# domain-tool

Created by Rasmus Wiegman \ admin@latency.dk
      
<h4>Please for any improvements or other suggestions, create an issue or send an email..</h4>


Python script to gather information, regarding domains

Usage domaintool.py

 Usage: 
<br>
./domaintool.py -f <file_path> [OPTIONS]
<br>
./domaintool.py [OPTIONS] <domain1> <domain2> ...

Flags:
   -f           Set filepath


OPTIONS:
  -h            Show this help message <br>
  -d            Set DNS Server to be used
  -all          Look up all
  -dns          Look up Nameservers
  -mx           Look up MX records
  -dnssec/ds    Look up if DNSSEC is enabled
  -txt          Look up TXT Records
  -a            Look up A Records
  -r            Perform reverse lookup from IP


<h4>In the folder gui-option/dist/ ypu can run the script as a GUI application.</h4>
