import os
import re
import argparse

# Default Configuration
PROJECT_ROOT = "www.conradlegaloffice.com"
IMAGES_DIR_NAME = "images-list"
EXTENSIONS = "png|jpg|jpeg|gif|mov|mp4|svg"

# List of all files processed during the session
DEFAULT_TARGET_FILES = [
    # Initial batch
    "about-us/index.html",
    "attorneys/index.html",
    "blog/index.html",
    "contact/index.html",
    "criminal-defense/index.html",
    "landlord/index.html",
    "personal-injury/index.html",
    "about-us/conrad-j-kuyawa/index.html",
    # Second batch
    "testimonials/index.html",
    "results/index.html",
    "site-map/index.html",
    # Third batch (nested)
    "personal-injury/slip-and-fall/index.html",
    "personal-injury/bus-accidents/index.html",
    "personal-injury/car-accidents/index.html",
    "personal-injury/hospital-negligence/index.html",
    "personal-injury/motorcycle-accidents/index.html",
    "personal-injury/nursing-home-abuse-neglect/index.html",
    "personal-injury/premises-liability/index.html",
    "personal-injury/truck-accidents/index.html",
    "personal-injury/wrongful-death/index.html",
    "landlord/evictions/index.html",
    "landlord/landlord-representation/index.html",
    "landlord/tenant-representation/index.html",
    "landlord/lease-rental-agreements/index.html"
]

def main():
    parser = argparse.ArgumentParser(description="Fix broken media references in HTML files by remapping them to a centralized image list.")
    parser.add_argument("--root", default=PROJECT_ROOT, help="Root directory of the web project")
    parser.add_argument("--images-dir", default=IMAGES_DIR_NAME, help="Name of the directory containing the flat list of images")
    args = parser.parse_args()

    project_root = args.root
    images_dir_path = os.path.join(project_root, args.images_dir)

    print(f"Indexing images in {images_dir_path}...")
    if not os.path.exists(images_dir_path):
        print(f"Error: Directory {images_dir_path} does not exist.")
        return

    # Build Index: filename -> relative path inside images-list (usually just filename)
    available_images = {}
    count_indexed = 0
    for root, dirs, files in os.walk(images_dir_path):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), images_dir_path)
            available_images[f] = rel_path
            count_indexed += 1

    print(f"Indexed {count_indexed} files.")

    # Regex to capture media paths inside quotes
    # Captures:
    # 1. Quote character
    # 2. Full original path
    # 3. Filename part (basename + extension)
    path_pattern = r'''
        (["'])
        (
            (?:[^"'\s]*/)?
            (
                [^"'\s/]+
                (?:''' + EXTENSIONS + r''')
            )
            (?:[#?][^"'\s]*)?
        )
        \1
    '''
    path_regex = re.compile(path_pattern, re.IGNORECASE | re.VERBOSE)

    total_replacements = 0

    target_files_full_paths = [os.path.join(project_root, f) for f in DEFAULT_TARGET_FILES]

    for file_path in target_files_full_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        replacements_in_file = 0

        # Calculate depth for relative path prefix (e.g. ../../)
        # We assume the images-list is at the project root.
        # file_path is something like "www/subdir/file.html"
        # project_root is "www"
        # rel_from_root = "subdir/file.html"
        rel_from_root = os.path.relpath(file_path, project_root)
        depth = rel_from_root.count(os.sep)
        
        # ../ for each directory level
        path_prefix = "../" * depth + args.images_dir + "/"

        def replacement_match(match):
            nonlocal replacements_in_file
            try:
                quote = match.group(1)
                full_path = match.group(2)
                filename_part = match.group(3)
            except IndexError:
                return match.group(0)
            
            # Ignore absolute URLs or data URIs
            if full_path.startswith(('http:', 'https:', 'data:', '//', 'tel:', 'mailto:')):
                return match.group(0)

            # Extract basename (remove query params for lookup)
            basename = filename_part.split('?')[0].split('#')[0]
            target_rel_path = None
            
            # Logic 1: Exact match
            if basename in available_images:
                target_rel_path = available_images[basename]
            else:
                # Logic 2: Cleaned match (remove timestamp like .1234567890.)
                clean_name = re.sub(r'\.\d{10,}\.', '.', basename)
                if clean_name in available_images:
                    target_rel_path = available_images[clean_name]
            
            if target_rel_path:
                suffix = ""
                match_suffix = re.search(r'([#?].*)$', full_path)
                if match_suffix:
                    suffix = match_suffix.group(1)
                
                new_path = f"{path_prefix}{target_rel_path}{suffix}"
                
                if new_path != full_path:
                    # print(f"  Fix: {full_path} -> {new_path}")
                    replacements_in_file += 1
                    return f"{quote}{new_path}{quote}"
            
            return match.group(0)

        new_content = path_regex.sub(replacement_match, content)

        if replacements_in_file > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Fixed {replacements_in_file} references.")
            total_replacements += replacements_in_file
        else:
            print("  No references found/fixed.")

    print(f"\nTotal fixed references across all files: {total_replacements}")

if __name__ == "__main__":
    main()
