import os
import shutil
import re
from bs4 import BeautifulSoup

OLD_ROOT = "www.conradlegaloffice.com"
NEW_ROOT = "newconradoffice.com"

# Single Page Mappings (Source -> Target relative to roots)
# Note: Source paths assume standard index.html structure
MAPPINGS = [
    ("index.html", "index.html"),
    ("contact/index.html", "contact/index.html"),
    ("results/index.html", "results/index.html"),
    ("testimonials/index.html", "testimonials/index.html"),
    ("about-us/conrad-j-kuyawa/index.html", "about-us/index.html"), # Depth change: 2 -> 1
    ("personal-injury/index.html", "personal-injury/index.html"),
    ("personal-injury/premises-liability/index.html", "personal-injury/premises-liability/index.html"),
    ("personal-injury/wrongful-death/index.html", "personal-injury/wrongful-death/index.html"),
    ("landlord/index.html", "tenants/index.html"), # Rename
    ("landlord/tenant-representation/index.html", "tenants/tenant-representation/index.html"), # Rename
    ("landlord/lease-rental-agreements/index.html", "tenants/implied-warranty-habitability-california/index.html"), # Rename + Content Move
]

# Merge Mapping
MERGE_TARGET = "personal-injury/vehicle-accidents/index.html"
MERGE_SOURCES = [
    "personal-injury/car-accidents/index.html",
    "personal-injury/bus-accidents/index.html",
    "personal-injury/motorcycle-accidents/index.html",
    "personal-injury/truck-accidents/index.html"
]

def adjust_depth(content, source_path, target_path):
    src_depth = source_path.count('/')
    tgt_depth = target_path.count('/')
    diff = src_depth - tgt_depth
    if diff == 0: return content
    
    if diff > 0:
        if diff == 1: content = content.replace('../../', '../')
    elif diff < 0:
        if diff == -1: content = content.replace('../', '../../')
    return content

def patch_links(content):
    replacements = {
        '/landlord/': '/tenants/',
        'href="landlord/': 'href="tenants/',
        'lease-rental-agreements': 'implied-warranty-habitability-california',
        'about-us/conrad-j-kuyawa/': 'about-us/',
        'about-us/conrad-j-kuyawa': 'about-us',
        'personal-injury/car-accidents': 'personal-injury/vehicle-accidents',
        'personal-injury/bus-accidents': 'personal-injury/vehicle-accidents',
        'personal-injury/motorcycle-accidents': 'personal-injury/vehicle-accidents',
        'personal-injury/truck-accidents': 'personal-injury/vehicle-accidents',
        '../car-accidents/': '', 
        '../bus-accidents/': '',
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content

def process_file(source_rel, target_rel):
    src_full = os.path.join(OLD_ROOT, source_rel)
    tgt_full = os.path.join(NEW_ROOT, target_rel)
    if not os.path.exists(src_full): return

    with open(src_full, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    content = adjust_depth(content, source_rel, target_rel)
    content = patch_links(content)
    os.makedirs(os.path.dirname(tgt_full), exist_ok=True)
    with open(tgt_full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Copied {source_rel} -> {target_rel}")

def merge_vehicle_accidents():
    base_src = MERGE_SOURCES[0]
    base_full = os.path.join(OLD_ROOT, base_src)
    with open(base_full, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    main_content = soup.find(id="MainContent")
    if main_content:
        main_content.clear()
        for src in MERGE_SOURCES:
            src_path = os.path.join(OLD_ROOT, src)
            if os.path.exists(src_path):
                with open(src_path, 'r', encoding='utf-8', errors='ignore') as f_src:
                    src_soup = BeautifulSoup(f_src, 'html.parser')
                    src_content = src_soup.find(id="MainContent")
                    if src_content:
                        topic = src.split('/')[-2].replace('-', ' ').title()
                        header = soup.new_tag("h2")
                        header.string = topic
                        main_content.append(header)
                        for element in src_content.children:
                            if element.name: main_content.append(element)
    
    title_tag = soup.find('title')
    if title_tag: title_tag.string = "Vehicle Accidents - Law Office of Conrad J. Kuyawa"
    html_content = str(soup)
    html_content = patch_links(html_content)
    target_rel = MERGE_TARGET
    tgt_full = os.path.join(NEW_ROOT, target_rel)
    os.makedirs(os.path.dirname(tgt_full), exist_ok=True)
    with open(tgt_full, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Merged Vehicle Accidents -> {target_rel}")

def main():
    for src, tgt in MAPPINGS:
        process_file(src, tgt)
    merge_vehicle_accidents()

if __name__ == "__main__":
    main()
