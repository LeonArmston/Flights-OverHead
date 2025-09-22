#!/bin/bash

# Flights OverHead - Installation Script for Home Assistant
# This script helps install the integration into Home Assistant

set -e

echo "🛩️  Flights OverHead - Home Assistant Integration Installer"
echo "============================================================"

# Check if Home Assistant config directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/homeassistant/config"
    echo ""
    echo "Example: $0 /config"
    echo "Example: $0 ~/.homeassistant" 
    echo ""
    echo "The config directory should contain your configuration.yaml file"
    exit 1
fi

CONFIG_DIR="$1"

# Validate Home Assistant config directory
if [ ! -f "$CONFIG_DIR/configuration.yaml" ]; then
    echo "❌ Error: $CONFIG_DIR doesn't appear to be a Home Assistant config directory"
    echo "   (configuration.yaml not found)"
    exit 1
fi

echo "📁 Home Assistant config directory: $CONFIG_DIR"

# Create custom_components directory if it doesn't exist
CUSTOM_COMPONENTS_DIR="$CONFIG_DIR/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS_DIR" ]; then
    echo "📂 Creating custom_components directory..."
    mkdir -p "$CUSTOM_COMPONENTS_DIR"
fi

# Create the integration directory
INTEGRATION_DIR="$CUSTOM_COMPONENTS_DIR/flights_overhead"
echo "📦 Installing to: $INTEGRATION_DIR"

if [ -d "$INTEGRATION_DIR" ]; then
    echo "⚠️  Integration directory already exists. Backing up..."
    mv "$INTEGRATION_DIR" "$INTEGRATION_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$INTEGRATION_DIR"
mkdir -p "$INTEGRATION_DIR/translations"

# Copy integration files
echo "📄 Copying integration files..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SCRIPT_DIR/custom_components/flights_overhead/__init__.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/api.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/config_flow.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/const.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/manifest.json" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/sensor.py" "$INTEGRATION_DIR/"
cp "$SCRIPT_DIR/custom_components/flights_overhead/translations/en.json" "$INTEGRATION_DIR/translations/"

echo "✅ Integration installed successfully!"
echo ""
echo "Next steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Configuration → Integrations"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Flights OverHead'"
echo "5. Configure your location and search radius"
echo ""
echo "For examples and documentation, see:"
echo "- README.md"
echo "- configuration_example.yaml"
echo ""
echo "🎉 Enjoy tracking flights overhead!"