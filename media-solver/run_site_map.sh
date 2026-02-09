#!/bin/bash

# Site Map Generator Wrapper
# This script ensures dependencies are installed and runs the mapper.

echo "--- Site Map Generator ---"

# 1. Check for Python
if ! command -v python3 &> /dev/null;
    echo "Error: python3 is not installed."
    exit 1
fi

# 2. Install dependencies
echo "Checking dependencies..."
pip install beautifulsoup4 --quiet

# 3. Run the generator
# You can customize the --root, --header-id, and --footer-id here
python3 media-solver/generate_site_map.py \
    --root "www.conradlegaloffice.com" \
    --output "userflow-links.md" \
    --header-id "HeaderZone" \
    --footer-id "FooterZone"

echo "Done! You can find the table in userflow-links.md"
