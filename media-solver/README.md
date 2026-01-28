# Media Solver Documentation

## Overview
The `media_fixer.py` script automates the process of fixing broken media references in HTML files after a site migration or restructuring. It is designed to scan a specific set of HTML files, identify broken image or video links, and re-map them to a centralized flat directory of assets (default: `images-list`).

## Key Features
- **Centralized Asset Lookup:** Scans a target directory (e.g., `images-list`) to build an index of available files.
- **Intelligent Matching:** Handles filename discrepancies caused by CMS timestamps.
  - *Example:* If `logo.1234567890.png` is missing, it automatically falls back to `logo.png` if available.
- **Dynamic Path Correction:** Calculates the correct relative path (`../` or `../../`) based on the depth of the HTML file being processed.
- **Preserves Query Parameters:** Retains hashes (`#`) or query strings (`?`) attached to media URLs (e.g., for SVG sprites).

## Usage

1.  Navigate to the `media-solver` directory or the project root.
2.  Run the script using Python 3:

```bash
python3 media-solver/media_fixer.py
```

### Configuration
By default, the script assumes:
- **Project Root:** `www.conradlegaloffice.com`
- **Images Directory:** `images-list` inside the project root.

You can modify these defaults by editing the constants at the top of the `media_fixer.py` file or extending the `argparse` configuration.

## Files Refactored
The following list of files was processed and updated during the refactoring session:

### Root Level
- `www.conradlegaloffice.com/about-us/index.html`
- `www.conradlegaloffice.com/attorneys/index.html`
- `www.conradlegaloffice.com/blog/index.html`
- `www.conradlegaloffice.com/contact/index.html`
- `www.conradlegaloffice.com/criminal-defense/index.html`
- `www.conradlegaloffice.com/landlord/index.html`
- `www.conradlegaloffice.com/personal-injury/index.html`
- `www.conradlegaloffice.com/testimonials/index.html`
- `www.conradlegaloffice.com/results/index.html`
- `www.conradlegaloffice.com/site-map/index.html`

### Personal Injury Sub-pages
- `www.conradlegaloffice.com/personal-injury/slip-and-fall/index.html`
- `www.conradlegaloffice.com/personal-injury/bus-accidents/index.html`
- `www.conradlegaloffice.com/personal-injury/car-accidents/index.html`
- `www.conradlegaloffice.com/personal-injury/hospital-negligence/index.html`
- `www.conradlegaloffice.com/personal-injury/motorcycle-accidents/index.html`
- `www.conradlegaloffice.com/personal-injury/nursing-home-abuse-neglect/index.html`
- `www.conradlegaloffice.com/personal-injury/premises-liability/index.html`
- `www.conradlegaloffice.com/personal-injury/truck-accidents/index.html`
- `www.conradlegaloffice.com/personal-injury/wrongful-death/index.html`

### Landlord Sub-pages
- `www.conradlegaloffice.com/landlord/evictions/index.html`
- `www.conradlegaloffice.com/landlord/landlord-representation/index.html`
- `www.conradlegaloffice.com/landlord/tenant-representation/index.html`
- `www.conradlegaloffice.com/landlord/lease-rental-agreements/index.html`
