#!/bin/bash
#
# ClawCrew One-Click Installer
# Usage: curl -sSL https://raw.githubusercontent.com/lanxindeng8/clawcrew/main/install.sh | bash
#
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Print logo
print_logo() {
    echo -e "${BLUE}"
    cat << "EOF"
   _____ _                _____
  / ____| |              / ____|
 | |    | | __ ___      _| |     _ __ _____      __
 | |    | |/ _` \ \ /\ / / |    | '__/ _ \ \ /\ / /
 | |____| | (_| |\ V  V /| |____| | |  __/\ V  V /
  \_____|_|\__,_| \_/\_/  \_____|_|  \___| \_/\_/

EOF
    echo -e "${NC}"
    echo "Multi-Agent AI Team Framework"
    echo "=============================="
    echo ""
}

# Print step
step() {
    echo -e "${BLUE}==>${NC} $1"
}

# Print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Print warning
warn() {
    echo -e "${YELLOW}!${NC} $1"
}

# Print error and exit
error() {
    echo -e "${RED}✗ Error:${NC} $1"
    exit 1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    else
        error "Unsupported OS: $OSTYPE"
    fi
    success "Detected OS: $OS"
}

# Check if command exists
has_command() {
    command -v "$1" &> /dev/null
}

# Check Python version
check_python() {
    step "Checking Python..."

    if has_command python3; then
        PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            success "Python $PY_VERSION"
            return 0
        else
            warn "Python $PY_VERSION found, but 3.10+ required"
        fi
    fi

    # Try to install Python
    if [ "$OS" == "macos" ]; then
        if has_command brew; then
            step "Installing Python via Homebrew..."
            brew install python@3.11
        else
            error "Python 3.10+ required. Install Homebrew first: https://brew.sh"
        fi
    else
        step "Installing Python via apt..."
        sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv python3-pip
    fi

    success "Python installed"
}

# Check pip
check_pip() {
    step "Checking pip..."

    if has_command pip3; then
        success "pip3"
    else
        step "Installing pip..."
        python3 -m ensurepip --upgrade 2>/dev/null || {
            if [ "$OS" == "macos" ]; then
                python3 -m pip install --upgrade pip
            else
                sudo apt-get install -y python3-pip
            fi
        }
        success "pip installed"
    fi
}

# Check jq
check_jq() {
    step "Checking jq..."

    if has_command jq; then
        success "jq"
    else
        step "Installing jq..."
        if [ "$OS" == "macos" ]; then
            brew install jq
        else
            sudo apt-get install -y jq
        fi
        success "jq installed"
    fi
}

# Check git
check_git() {
    step "Checking git..."

    if has_command git; then
        success "git"
    else
        error "git not found. Please install git first."
    fi
}

# Check OpenClaw
check_openclaw() {
    step "Checking OpenClaw..."

    if [ -f "$HOME/.openclaw/openclaw.json" ]; then
        success "OpenClaw configured"
    else
        warn "OpenClaw not found"
        echo ""
        echo "OpenClaw is required to run ClawCrew."
        echo "Please install OpenClaw first: https://openclaw.dev"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Install ClawCrew
install_clawcrew() {
    step "Installing ClawCrew..."

    # Check if installing from PyPI or local
    if [ -f "pyproject.toml" ]; then
        # Local development install
        pip3 install --user -e .
    else
        # Install from PyPI (when published)
        # For now, install from GitHub
        pip3 install --user git+https://github.com/lanxindeng8/clawcrew.git
    fi

    success "ClawCrew installed"
}

# Add to PATH if needed
setup_path() {
    # Get user site-packages bin directory
    USER_BIN=$(python3 -m site --user-base)/bin

    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        warn "Adding $USER_BIN to PATH"

        # Determine shell config file
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi

        echo "" >> "$SHELL_RC"
        echo "# ClawCrew" >> "$SHELL_RC"
        echo "export PATH=\"\$PATH:$USER_BIN\"" >> "$SHELL_RC"

        export PATH="$PATH:$USER_BIN"

        echo -e "${DIM}Added to $SHELL_RC (restart shell or run: source $SHELL_RC)${NC}"
    fi
}

# Run setup wizard
run_wizard() {
    echo ""
    step "Running configuration wizard..."
    echo ""

    # Check if clawcrew command is available
    if has_command clawcrew; then
        clawcrew init
    else
        # Try with full path
        USER_BIN=$(python3 -m site --user-base)/bin
        "$USER_BIN/clawcrew" init
    fi
}

# Print completion message
print_complete() {
    echo ""
    echo -e "${GREEN}=============================="
    echo "Installation complete!"
    echo -e "==============================${NC}"
    echo ""
    echo "Quick start:"
    echo "  clawcrew start    # Start the system"
    echo "  clawcrew status   # Check status"
    echo "  clawcrew --help   # Show all commands"
    echo ""
    echo "For more info: https://github.com/lanxindeng8/clawcrew"
    echo ""
}

# Main
main() {
    print_logo

    detect_os
    check_python
    check_pip
    check_jq
    check_git
    check_openclaw

    echo ""
    install_clawcrew
    setup_path

    # Ask about running wizard
    echo ""
    read -p "Run configuration wizard now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_wizard
    fi

    print_complete
}

# Run main
main "$@"
