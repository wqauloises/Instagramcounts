#!/bin/bash
# Termux installation script for Instagramcounts

echo "Installing Instagramcounts for Termux..."

# Update packages
pkg update -y
pkg upgrade -y

# Install Python and dependencies
pkg install -y python3 pip git

# Clone or update repo
if [ -d "$HOME/Instagramcounts" ]; then
    cd "$HOME/Instagramcounts"
    git pull
else
    git clone https://github.com/wqauloises/Instagramcounts.git "$HOME/Instagramcounts"
    cd "$HOME/Instagramcounts"
fi

# Install Python dependencies
pip install -r requirements.txt

# Create shortcut
mkdir -p ~/.local/bin
cat > ~/.local/bin/instacounts << 'EOF'
#!/bin/bash
cd ~/Instagramcounts && python3 main.py "$@"
EOF
chmod +x ~/.local/bin/instacounts

echo "✅ Installation complete!"
echo ""
echo "Quick start:"
echo "  instacounts add <username>   - Add account"
echo "  instacounts track-all        - Track all accounts"
echo "  instacounts list             - Show accounts"
echo ""
echo "Data stored in: ~/.instacounts/"
echo "Widget file: ~/.instacounts/widget.json"