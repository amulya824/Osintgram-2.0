#!/data/data/com.termux/files/usr/bin/bash

# Modified by Amulya Srivastava (2024)
# Original tool by Datalux
# Instagram OSINT Tool Setup Script for Termux

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Starting Osintgram setup for Termux...${NC}"

# Update package list
echo -e "${YELLOW}[*] Updating package list...${NC}"
pkg update -y

# Install required packages
echo -e "${YELLOW}[*] Installing required packages...${NC}"
pkg install -y python git

# Create necessary directories
echo -e "${YELLOW}[*] Creating necessary directories...${NC}"
mkdir -p config
mkdir -p output

# Install Python requirements
echo -e "${YELLOW}[*] Installing Python requirements...${NC}"
pip install -r requirements.txt

# Create credentials template
echo -e "${YELLOW}[*] Creating credentials template...${NC}"
echo "[Credentials]
username = YOUR_INSTAGRAM_USERNAME
password = YOUR_INSTAGRAM_PASSWORD" > config/credentials.ini

echo -e "${GREEN}[+] Setup completed!${NC}"
echo -e "${YELLOW}[*] Next steps:${NC}"
echo -e "1. Edit config/credentials.ini with your Instagram login details"
echo -e "2. Run: python3 main.py <target_username>"
echo -e "3. Type 'list' to see available commands"
echo -e "\n${RED}Note: Make sure to use valid Instagram credentials${NC}"
