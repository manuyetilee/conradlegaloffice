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
## Session Summary (Jan 28, 2026)

### Completed Tasks
1.  **Media Refactoring:**
    *   Remapped over 700 broken media references across 24 HTML files to point to the centralized `images-list` directory.
    *   Implemented logic to automatically resolve CMS-style timestamped filenames (e.g., `file.12345.png` -> `file.png`).
2.  **Codebase Cleanup:**
    *   **Scorpion Removal:** Systematically removed all third-party branding, tracking scripts (`analytics.scorpion.co`), and "Scorpion Footer" containers from 75 HTML files.
    *   **Duplicate Cleanup:** Deleted 193 duplicate asset files found outside `images-list` and removed 18 empty parent directories.
    *   **System Files:** Removed 36 `.db` (thumbs/desktop) files and 34 resulting empty directories.
3.  **UI & Content Updates:**
    *   **Video Player:** Replaced the broken homepage video with a custom-built modal player featuring a thumbnail, play button, and playback control logic.
    *   **Global Rebranding:** Updated logos across all pages (`logo-dark.png` -> `Logo.png`, `logo-light.png` -> `Logo2.png`).
    *   **Address Update:** Globally updated the business address from Pittsburg, CA to `530 Divisadero St, PMB 804, San Francisco, CA 94117`.
4.  **Tooling:** Established the `media-solver/` directory containing the `media_fixer.py` script for ongoing maintenance.

### Next Session Goals
- **Form Functionality:** Investigate and fix the backend integration/submission logic for contact forms.
- **UI/UX Improvements:** Identify and fix any remaining broken links in the navigation or content.
- **Layout Fixes:** Address broken CSS layouts or responsive design issues identified during browsing.

### Session Summary (Jan 29, 2026)

**Completed Tasks:**
1.  **Global Phone Number Update:**
    *   **New Number:** `(877) 364-6210`.
    *   **Header:** Replaced the "Get in Touch" section with a fully clickable CTA block (Title Case text + Phone Number with Icon). Added hover effects and pointer cursor. Applied to 74 pages.
    *   **Footer:** Added the clickable phone number with a phone icon above the address on all pages. Added pointer cursor on hover.
    *   **Contact Page:** Added a clickable phone number button next to the "Submit Form" button. Styled them side-by-side in a flex container with a `450px` max-width. Set the phone button to a dark blue background.
2.  **CSS Refinement:**
    *   Globally removed `margin-left` from `.btn.v1 svg` across 16 CSS files to improve icon alignment within buttons.
3.  **Submit Button Restoration:** Fixed an issue where the submit button was accidentally removed from forms on non-contact pages. Restored functionality across 32 affected pages.

**Current State:**
- All forms are functional and correctly styled.
- Phone numbers are updated, interactive, and consistent across the site.
- Branding and contact info are fully updated to the new requirements.
