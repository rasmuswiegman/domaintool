# domain-tool

Created by Rasmus Wiegman \ admin@latency.dk
      
#### Please for any improvements or other suggestions, create an issue or send an email..</


Python script to gather information, regarding domains

Usage domaintool.py

#### Usage: 
<br>
./domaintool.py -f <file_path> [OPTIONS]
<br>
./domaintool.py [OPTIONS] <domain1> <domain2> ...

#### Flags:
   -f           Set filepath


#### OPTIONS:<br>
  -h            Show this help message <br>
  -d            Set DNS Server to be used <br>
  -all          Look up all <br>
  -dns          Look up Nameservers <br>
  -mx           Look up MX records <br>
  -dnssec/ds    Look up if DNSSEC is enabled <br>
  -txt          Look up TXT Records <br>
  -a            Look up A Records <br>
  -r            Perform reverse lookup from IP <br>

### Install as system wide service

```chmod +x install_domaintool.sh```

./install_domaintool.sh

After install

````domaintool -all example.com````     # Use from anywhere

````man domaintool````                      # Read manual

#### Uninstall
bash./install_domaintool.sh uninstall


###### In the folder gui-option/dist/ you can run the script as a GUI application.
