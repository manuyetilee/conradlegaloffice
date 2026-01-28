# Conrad Legal Office Website

## Project Overview
This project is the static website for the **Law Office of Conrad J. Kuyawa**. It is built using standard HTML, CSS, and JavaScript without a complex build system or package manager (like Node.js or Webpack). The site structure is directory-based, where each section (e.g., `about-us`, `blog`) has its own directory with an `index.html` file.

## Directory Structure

*   **`www.conradlegaloffice.com/`**: The root directory of the website source code.
    *   **`index.html`**: The main homepage of the website.
    *   **`images-list/`**: A centralized flat directory containing all media assets (images, videos) used across the site. This was created to resolve broken relative paths during migration.
    *   **`[section]/`** (e.g., `about-us/`, `attorneys/`, `blog/`): Directories representing different pages of the site. Each contains an `index.html` file.
    *   **`assets/`, `cms/`, `common/`**: Directories containing supporting assets, scripts, and styles, likely remnants of the original CMS or template.

*   **`media-solver/`**: A utility directory containing tools developed to maintain this project.
    *   **`media_fixer.py`**: A Python script designed to scan HTML files and fix broken media references by remapping them to the `images-list` directory.
    *   **`README.md`**: Documentation for the media solver tool.

## Usage

### Running the Website
Since this is a static site, you can view it directly in a web browser or serve it using a simple HTTP server.

**Option 1: Python SimpleHTTPServer**
Run the following command from the `www.conradlegaloffice.com` directory:
```bash
cd www.conradlegaloffice.com
python3 -m http.server 8000
```
Then open `http://localhost:8000` in your browser.

**Option 2: Direct File Access**
Open the `www.conradlegaloffice.com/index.html` file directly in your web browser.

### Maintenance Tools

**Media Fixer**
If you encounter broken images or media links (e.g., after moving files or adding new pages), use the `media_fixer.py` script.

```bash
python3 media-solver/media_fixer.py
```
This script scans targeted HTML files and updates image `src` and link `href` attributes to point correctly to the `images-list` directory, handling timestamped filenames (e.g., `logo.12345.png` -> `logo.png`).

**Scorpion Cleanup**
A cleanup process was performed to remove third-party tracking scripts and branding from "Scorpion". If these reappear or new files are added with these references, they should be removed to maintain site cleanliness and performance.

## Development Conventions

*   **Static Assets:** All new images and media should be placed in `www.conradlegaloffice.com/images-list/` to maintain the flat structure required by the current linking strategy.
*   **Pathing:** When referencing assets from sub-pages (e.g., `blog/2023/index.html`), ensure the relative path is correct (e.g., `../../images-list/image.jpg`). The `media_fixer.py` script can automate this correction.
*   **HTML Structure:** The site follows a standard structure with `header`, `main`, and `footer` zones. Ensure common elements (nav, footer) are consistent across pages manually, as there is no templating engine.
