#!/bin/bash

# DNS Tool Installer Script
# Works on both macOS and Linux
# Installs domaintool.py as a system-wide command

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script variables
SCRIPT_NAME="domaintool"
SCRIPT_FILE="domaintool.py"
INSTALL_DIR="/usr/local/bin"
SERVICE_NAME="domaintool"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null && python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    else
        print_error "Python 3 is required but not found!"
        exit 1
    fi
    print_status "Found Python: $PYTHON_CMD"
}

# Function to check Python package installation methods
# Function to check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip is required but not found!"
        exit 1
    fi
    print_status "Found pip: $PIP_CMD"
}

# Function to check Python package installation methods
check_python_environment() {
    print_status "Checking Python environment..."
    
    # Check for virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_status "Virtual environment detected: $VIRTUAL_ENV"
        return 0
    fi
    
    # Check for conda environment
    if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        print_status "Conda environment detected: $CONDA_DEFAULT_ENV"
        return 0
    fi
    
    # Check Python installation type
    local python_path=$($PYTHON_CMD -c "import sys; print(sys.executable)")
    print_status "Python executable: $python_path"
    
    if [[ "$python_path" == *"/usr/bin/"* ]] || [[ "$python_path" == *"/bin/"* ]]; then
        print_warning "System Python detected - may need --break-system-packages"
    elif [[ "$python_path" == *"homebrew"* ]] || [[ "$python_path" == *"brew"* ]]; then
        print_warning "Homebrew Python detected - may need --break-system-packages"
    fi
}

# Function to check Python package installation methods
# Function to provide installation alternatives
show_installation_alternatives() {
    print_status "Alternative installation methods:"
    echo ""
    print_status "1. Using virtual environment (recommended):"
    echo "   python3 -m venv dns_tool_env"
    echo "   source dns_tool_env/bin/activate"
    echo "   pip install dnspython python-whois"
    echo "   # Then run this installer"
    echo ""
    print_status "2. Using system Python with break-system-packages:"
    echo "   pip3 install --break-system-packages dnspython python-whois"
    echo ""
    print_status "3. Using user installation:"
    echo "   pip3 install --user dnspython python-whois"
    echo ""
    print_status "4. Using package manager (if available):"
    echo "   # Ubuntu/Debian:"
    echo "   sudo apt install python3-dns python3-whois"
    echo "   # Fedora/RHEL:"
    echo "   sudo dnf install python3-dns python3-whois"
    echo "   # macOS with Homebrew:"
    echo "   brew install python-dnspython"
    echo ""
}

# Function to check if system packages flag is needed
needs_break_system_packages() {
    # Check if we're in a system-managed Python environment
    if $PIP_CMD install --help 2>&1 | grep -q "break-system-packages"; then
        return 0
    else
        return 1
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    local deps=("dnspython" "python-whois")
    local pip_flags=""
    
    # Determine pip flags based on environment
    if check_root; then
        # For root installation, try different approaches
        if needs_break_system_packages; then
            pip_flags="--break-system-packages"
            print_warning "Using --break-system-packages flag for system Python"
        fi
    else
        # For user installation, prefer --user but fallback to --break-system-packages
        pip_flags="--user"
    fi
    
    for dep in "${deps[@]}"; do
        print_status "Installing $dep..."
        
        # Try installation with different methods
        local install_success=false
        
        # Method 1: Try with current flags
        if [[ "$install_success" == false ]]; then
            if $PIP_CMD install $pip_flags $dep 2>/dev/null; then
                install_success=true
                print_success "$dep installed successfully"
            fi
        fi
        
        # Method 2: Try with --break-system-packages if method 1 failed
        if [[ "$install_success" == false ]] && needs_break_system_packages; then
            print_warning "Retrying $dep installation with --break-system-packages..."
            if $PIP_CMD install --break-system-packages $dep 2>/dev/null; then
                install_success=true
                print_success "$dep installed with --break-system-packages"
            fi
        fi
        
        # Method 3: Try with --user if we're not root and previous methods failed
        if [[ "$install_success" == false ]] && ! check_root; then
            print_warning "Retrying $dep installation with --user..."
            if $PIP_CMD install --user $dep 2>/dev/null; then
                install_success=true
                print_success "$dep installed with --user"
            fi
        fi
        
        # Method 4: Try with --force-reinstall --break-system-packages as last resort
        if [[ "$install_success" == false ]] && needs_break_system_packages; then
            print_warning "Final attempt for $dep with --force-reinstall --break-system-packages..."
            if $PIP_CMD install --force-reinstall --break-system-packages $dep 2>/dev/null; then
                install_success=true
                print_success "$dep installed with force reinstall"
            fi
        fi
        
        # Check if installation ultimately failed
        if [[ "$install_success" == false ]]; then
            print_error "Failed to install $dep. Trying manual installation..."
            print_status "Please run manually:"
            print_status "  $PIP_CMD install --break-system-packages $dep"
            print_status "  or"
            print_status "  $PIP_CMD install --user $dep"
            
            # Ask user if they want to continue
            echo -n "Continue installation anyway? (y/N): "
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                print_error "Installation cancelled"
                exit 1
            fi
        fi
    done
    
    print_success "Dependencies installation completed!"
}

# Function to install the script
install_script() {
    print_status "Installing $SCRIPT_NAME to $INSTALL_DIR..."
    
    # Check if script file exists
    if [[ ! -f "$SCRIPT_FILE" ]]; then
        print_error "$SCRIPT_FILE not found in current directory!"
        exit 1
    fi
    
    # Copy script to install directory
    if check_root; then
        cp "$SCRIPT_FILE" "$INSTALL_DIR/$SCRIPT_NAME"
        chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    else
        sudo cp "$SCRIPT_FILE" "$INSTALL_DIR/$SCRIPT_NAME"
        sudo chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    fi
    
    print_success "$SCRIPT_NAME installed to $INSTALL_DIR"
}

# Function to create man page
create_man_page() {
    print_status "Creating man page..."
    
    local man_dir="/usr/local/share/man/man1"
    local man_file="$man_dir/$SCRIPT_NAME.1"
    
    # Create man directory if it doesn't exist
    if check_root; then
        mkdir -p "$man_dir"
    else
        sudo mkdir -p "$man_dir"
    fi
    
    # Create man page content
    cat > /tmp/$SCRIPT_NAME.1 << 'EOF'
.TH DOMAINTOOL 1 "2025" "1.0" "DNS Tool Manual"
.SH NAME
domaintool \- DNS lookup and WHOIS information tool
.SH SYNOPSIS
.B domaintool
[\fIOPTIONS\fR] \fIdomain1\fR [\fIdomain2\fR ...]
.br
.B domaintool
\fB\-f\fR \fIfile\fR [\fIOPTIONS\fR]
.br
.B domaintool
\fB\-r\fR \fIip_address\fR
.SH DESCRIPTION
.B domaintool
is a comprehensive DNS lookup and WHOIS information tool that supports multiple record types and parallel processing.
.SH OPTIONS
.TP
.B \-h, \-\-help
Show help message and exit
.TP
.B \-all
Look up all record types (A, NS, MX, TXT, DMARC, DNSSEC, WHOIS)
.TP
.B \-a
Look up A records
.TP
.B \-ns, \-dns
Look up nameserver (NS) records
.TP
.B \-mx
Look up mail exchange (MX) records
.TP
.B \-txt
Look up TXT records
.TP
.B \-dmarc
Look up DMARC policy records
.TP
.B \-dnssec
Check DNSSEC status
.TP
.B \-who
Look up WHOIS information
.TP
.B \-r \fIip_address\fR
Perform reverse DNS lookup for IP address
.TP
.B \-f \fIfile\fR
Read domains from file (one per line)
.TP
.B \-d \fIdns_server\fR, \-\-dns\-server \fIdns_server\fR
Use custom DNS server
.SH EXAMPLES
.TP
Look up all records for a domain:
.B domaintool \-all example.com
.TP
Look up A and MX records for multiple domains:
.B domaintool \-a \-mx example.com google.com
.TP
Look up domains from file with WHOIS info:
.B domaintool \-f domains.txt \-who
.TP
Reverse lookup for IP address:
.B domaintool \-r 8.8.8.8
.TP
Use custom DNS server:
.B domaintool \-d 1.1.1.1 \-all example.com
.SH AUTHOR
DNS Tool by User
.SH SEE ALSO
.BR dig (1),
.BR nslookup (1),
.BR whois (1)
EOF

    # Install man page
    if check_root; then
        mv /tmp/$SCRIPT_NAME.1 "$man_file"
    else
        sudo mv /tmp/$SCRIPT_NAME.1 "$man_file"
    fi
    
    print_success "Man page created at $man_file"
}

# Function to create desktop entry (Linux only)
create_desktop_entry() {
    if [[ "$OS" == "linux" ]]; then
        print_status "Creating desktop entry..."
        
        local desktop_dir="/usr/share/applications"
        local desktop_file="$desktop_dir/$SCRIPT_NAME.desktop"
        
        cat > /tmp/$SCRIPT_NAME.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DNS Tool
Comment=DNS lookup and WHOIS information tool
Exec=gnome-terminal -- $SCRIPT_NAME
Icon=utilities-terminal
Terminal=true
Categories=Network;System;
Keywords=dns;whois;network;lookup;
EOF

        if check_root; then
            mv /tmp/$SCRIPT_NAME.desktop "$desktop_file"
        else
            sudo mv /tmp/$SCRIPT_NAME.desktop "$desktop_file"
        fi
        
        print_success "Desktop entry created"
    fi
}

# Function to update shell completion
setup_completion() {
    print_status "Setting up shell completion..."
    
    # Bash completion
    cat > /tmp/$SCRIPT_NAME-completion.bash << 'EOF'
_domaintool_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="-h --help -all -a -ns -dns -mx -txt -dmarc -dnssec -who -r -f -d --dns-server"
    
    case ${prev} in
        -f)
            COMPREPLY=( $(compgen -f ${cur}) )
            return 0
            ;;
        -d|--dns-server)
            COMPREPLY=( $(compgen -W "8.8.8.8 1.1.1.1 208.67.222.222" -- ${cur}) )
            return 0
            ;;
        -r)
            return 0
            ;;
    esac
    
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -F _domaintool_completion domaintool
EOF

    # Install bash completion
    local completion_dir="/usr/local/etc/bash_completion.d"
    if [[ "$OS" == "linux" ]]; then
        completion_dir="/etc/bash_completion.d"
    fi
    
    if check_root; then
        mkdir -p "$completion_dir"
        mv /tmp/$SCRIPT_NAME-completion.bash "$completion_dir/$SCRIPT_NAME"
    else
        sudo mkdir -p "$completion_dir"
        sudo mv /tmp/$SCRIPT_NAME-completion.bash "$completion_dir/$SCRIPT_NAME"
    fi
    
    print_success "Shell completion installed"
}

# Function to uninstall
uninstall() {
    print_status "Uninstalling $SCRIPT_NAME..."
    
    # Remove main script
    if [[ -f "$INSTALL_DIR/$SCRIPT_NAME" ]]; then
        if check_root; then
            rm -f "$INSTALL_DIR/$SCRIPT_NAME"
        else
            sudo rm -f "$INSTALL_DIR/$SCRIPT_NAME"
        fi
        print_success "Removed $INSTALL_DIR/$SCRIPT_NAME"
    fi
    
    # Remove man page
    local man_file="/usr/local/share/man/man1/$SCRIPT_NAME.1"
    if [[ -f "$man_file" ]]; then
        if check_root; then
            rm -f "$man_file"
        else
            sudo rm -f "$man_file"
        fi
        print_success "Removed man page"
    fi
    
    # Remove desktop entry (Linux)
    local desktop_file="/usr/share/applications/$SCRIPT_NAME.desktop"
    if [[ -f "$desktop_file" ]]; then
        if check_root; then
            rm -f "$desktop_file"
        else
            sudo rm -f "$desktop_file"
        fi
        print_success "Removed desktop entry"
    fi
    
    # Remove completion
    local completion_files=(
        "/usr/local/etc/bash_completion.d/$SCRIPT_NAME"
        "/etc/bash_completion.d/$SCRIPT_NAME"
    )
    
    for comp_file in "${completion_files[@]}"; do
        if [[ -f "$comp_file" ]]; then
            if check_root; then
                rm -f "$comp_file"
            else
                sudo rm -f "$comp_file"
            fi
            print_success "Removed completion file"
            break
        fi
    done
    
    print_success "Uninstallation completed!"
    exit 0
}

# Function to show usage
show_usage() {
    echo "DNS Tool Installer"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  install       Install domaintool as system command (default)"
    echo "  uninstall     Remove domaintool from system"
    echo "  --help, -h    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Install domaintool"
    echo "  $0 install      # Install domaintool"
    echo "  $0 uninstall    # Remove domaintool"
    echo ""
}

# Main installation function
main_install() {
    print_status "Starting DNS Tool installation..."
    print_status "Detected OS: $OS"
    
    # Check requirements
    check_python
    check_pip
    check_python_environment
    
    # Try to install dependencies
    if ! install_dependencies; then
        print_error "Dependency installation failed!"
        show_installation_alternatives
        echo ""
        echo -n "Do you want to continue installation without automatic dependency installation? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
        print_warning "Continuing without automatic dependency installation..."
        print_warning "You'll need to install 'dnspython' and 'python-whois' manually"
    fi
    
    # Install main script
    install_script
    
    # Create additional files
    create_man_page
    create_desktop_entry
    setup_completion
    
    print_success "Installation completed successfully!"
    echo ""
    print_status "You can now use 'domaintool' from anywhere in your terminal"
    print_status "Type 'domaintool --help' to see usage information"
    print_status "Type 'man domaintool' to see the manual page"
    echo ""
    print_warning "You may need to restart your terminal or run 'source ~/.bashrc' for completion to work"
}

# Parse command line arguments
case "${1:-install}" in
    install)
        OS=$(detect_os)
        if [[ "$OS" == "unknown" ]]; then
            print_error "Unsupported operating system: $OSTYPE"
            exit 1
        fi
        main_install
        ;;
    uninstall)
        uninstall
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
