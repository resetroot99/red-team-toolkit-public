#!/bin/bash

# RED Team Toolkit - Public Repository Installer
# Downloads and installs the latest version from GitHub

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/YOUR_USERNAME/red-team-toolkit-public"
INSTALL_DIR="$HOME/redtoolkit"

echo -e "${BLUE}RED Team Toolkit - Public Installer${NC}"
echo "======================================="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    echo -e "${RED}❌ Unsupported platform: $OSTYPE${NC}"
    echo "This installer supports macOS and Linux only"
    exit 1
fi

echo -e "${BLUE}Platform: $PLATFORM${NC}"

# Check for required tools
echo -e "${BLUE}🔍 Checking system requirements...${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    echo "Please install Python 3:"
    if [[ "$PLATFORM" == "macOS" ]]; then
        echo "  brew install python3"
        echo "  or download from https://python.org"
    else
        echo "  sudo apt-get install python3 python3-pip"
        echo "  or sudo yum install python3 python3-pip"
    fi
    exit 1
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is required but not installed${NC}"
    echo "Please install Git:"
    if [[ "$PLATFORM" == "macOS" ]]; then
        echo "  brew install git"
        echo "  or download from https://git-scm.com"
    else
        echo "  sudo apt-get install git"
        echo "  or sudo yum install git"
    fi
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 not found, trying to install...${NC}"
    python3 -m ensurepip --default-pip || {
        echo -e "${RED}❌ Could not install pip${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ System requirements met${NC}"

# Installation directory
echo ""
echo -e "${BLUE}📁 Installation directory: $INSTALL_DIR${NC}"

# Check if directory exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory already exists${NC}"
    read -p "Remove existing installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}✅ Removed existing installation${NC}"
    else
        echo -e "${RED}❌ Installation cancelled${NC}"
        exit 1
    fi
fi

# Clone repository
echo ""
echo -e "${BLUE}📥 Downloading RED Team Toolkit...${NC}"

git clone "$REPO_URL.git" "$INSTALL_DIR" || {
    echo -e "${RED}❌ Failed to clone repository${NC}"
    echo "Please check your internet connection and try again"
    exit 1
}

cd "$INSTALL_DIR"

# Install Python dependencies
echo ""
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip3 install -r requirements.txt --user || {
    echo -e "${YELLOW}⚠️  Some dependencies may not have installed correctly${NC}"
}

# Make main script executable
chmod +x redtoolkit.py

# Create launcher script
echo ""
echo -e "${BLUE}🔧 Setting up launcher...${NC}"

mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/redtoolkit" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 redtoolkit.py "\$@"
EOF

chmod +x "$HOME/.local/bin/redtoolkit"

# Add to PATH if not already there
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$SHELL_RC" ]] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo -e "${GREEN}✅ Added to PATH in $SHELL_RC${NC}"
fi

echo ""
echo -e "${GREEN}✅ Installation completed successfully!${NC}"
echo ""
echo -e "${BLUE}🚀 Usage:${NC}"
echo "  redtoolkit              # Run from anywhere (after restarting shell)"
echo "  cd $INSTALL_DIR && python3 redtoolkit.py  # Run directly"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Restart your terminal or run: source $SHELL_RC"
echo "2. Run: redtoolkit"
echo "3. Enter your license key when prompted"
echo ""
echo -e "${BLUE}📧 Support:${NC}"
echo "  Email: sudo@hxcode.xyz"
echo "  Website: www.509938.xyz"
echo ""

# Test installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
python3 redtoolkit.py --version

echo ""
echo -e "${GREEN}🎉 RED Team Toolkit installed successfully!${NC}"
echo -e "${YELLOW}⚠️  You'll need a license key to use the toolkit${NC}"
echo -e "${BLUE}🌐 Get your license key at: www.509938.xyz${NC}"
