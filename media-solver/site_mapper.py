import os
from bs4 import BeautifulSoup
import re

# Configuration
ROOT_DIR = "www.conradlegaloffice.com"
OUTPUT_FILE = "userflow-links.md"

def get_page_name(path):
    """Derived from directory path.
    e.g. www.conradlegaloffice.com/about-us/index.html -> About Us
    www.conradlegaloffice.com/index.html -> Home
    """
    rel_path = os.path.relpath(path, ROOT_DIR)
    if rel_path == "index.html":
        return "Home"
    
    parts = os.path.dirname(rel_path).split(os.sep)
    name = " / ".join([p.replace('-', ' ').title() for p in parts])
    if name == "": return "Home"
    return name

def resolve_path(source_file_path, href):
    """Resolves a relative href to a canonical path relative to ROOT_DIR."""
    if not href or href.startswith(('http', 'https', 'mailto:', 'tel:', 'javascript:', '#')):
        return None
    
    href = href.split('?')[0].split('#')[0]
    if not href:
        return None

    source_dir = os.path.dirname(source_file_path)
    abs_path = os.path.abspath(os.path.join(source_dir, href))
    root_abs = os.path.abspath(ROOT_DIR)
    
    if not abs_path.startswith(root_abs):
        return None 
        
    rel_path = os.path.relpath(abs_path, root_abs)
    
    if os.path.isdir(os.path.join(ROOT_DIR, rel_path)):
        rel_path = os.path.join(rel_path, "index.html")
    elif not rel_path.endswith('.html'):
         if os.path.exists(os.path.join(ROOT_DIR, rel_path)):
             pass 
         elif os.path.exists(os.path.join(ROOT_DIR, rel_path, 'index.html')):
             rel_path = os.path.join(rel_path, 'index.html')
    
    if rel_path.endswith('.html') and os.path.exists(os.path.join(ROOT_DIR, rel_path)):
        return rel_path
    
    return None

def is_hidden(element):
    """Checks if element or any parent has display:none style."""
    cursor = element
    while cursor and cursor.name != '[document]':
        if cursor.has_attr('style'):
            style = cursor['style'].lower()
            if 'display:none' in style.replace(' ', ''):
                return True
        if cursor.has_attr('hidden'):
             return True
        cursor = cursor.parent
    return False

def get_section_id(element):
    """Finds the closest parent with an ID."""
    cursor = element
    while cursor and cursor.name != '[document]':
        if cursor.has_attr('id'):
            return f"#{cursor['id']}"
        cursor = cursor.parent
    return "Unknown Section"

def main():
    all_files = []
    page_map = {} # path -> Page Name
    
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file == "index.html":
                full_path = os.path.join(root, file)
                name = get_page_name(full_path)
                rel_path = os.path.relpath(full_path, ROOT_DIR)
                all_files.append(full_path)
                page_map[rel_path] = name

    # Data Structures
    # Body Links: TargetPath -> List of {SourcePageName, Section, Hidden}
    body_access = {p: [] for p in page_map}
    
    # Global Links: Set of (Container, TargetPageName, Section, Hidden)
    # Using set to deduplicate identical links found on multiple pages
    global_links = set()

    for file_path in all_files:
        current_page_name = get_page_name(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        header = soup.find(id="HeaderZone")
        footer = soup.find(id="FooterZone")

        for a in soup.find_all('a', href=True):
            target_rel = resolve_path(file_path, a['href'])
            
            if target_rel and target_rel in page_map:
                target_name = page_map[target_rel]
                section = get_section_id(a)
                hidden = is_hidden(a)
                
                # Determine Container
                is_nav = header and (a in header.descendants)
                is_footer = footer and (a in footer.descendants)
                
                if is_nav:
                    global_links.add(("NavBar", target_name, section, hidden))
                elif is_footer:
                    global_links.add(("Footer", target_name, section, hidden))
                else:
                    # Body Link
                    entry = {
                        'source_name': current_page_name,
                        'section': section,
                        'hidden': hidden
                    }
                    body_access[target_rel].append(entry)

    # --- FORMATTING OUTPUT ---
    
    lines = []
    
    # TABLE 1: Page Tree (Body Links Only)
    lines.append("## Page Tree (Content Links)")
    lines.append("| **Page Name** | **Accessible From (Content)** | **Hidden** |")
    lines.append("| --- | --- | --- |")
    
    sorted_pages = sorted(page_map.items(), key=lambda x: x[1])
    
    for rel_path, page_name in sorted_pages:
        accesses = body_access.get(rel_path, [])
        
        if not accesses:
            lines.append(f"| {page_name} | None | (false) |")
            continue
            
        # Group by Source Page
        # Map: SourceName -> List[(Section, Hidden)]
        grouped = {}
        for entry in accesses:
            s_name = entry['source_name']
            if s_name not in grouped: grouped[s_name] = []
            
            # Dedup within same page source if same section/hidden
            val = (entry['section'], entry['hidden'])
            if val not in grouped[s_name]:
                grouped[s_name].append(val)
        
        sorted_sources = sorted(grouped.keys())
        
        col2_parts = []
        col3_parts = []
        
        for src in sorted_sources:
            items = grouped[src] # List of (section, hidden)
            
            sections_str = ", ".join([x[0] for x in items])
            col2_parts.append(f"{src} ({sections_str})")
            
            hidden_vals = ["true" if x[1] else "false" for x in items]
            hidden_str = "(" + ", ".join(hidden_vals) + ")"
            col3_parts.append(hidden_str)
            
        lines.append(f"| {page_name} | {', '.join(col2_parts)} | {','.join(col3_parts)} |")

    lines.append("\n")

    # TABLE 2: Global Navigation (NavBar & Footer)
    lines.append("## Global Navigation (NavBar & Footer)")
    lines.append("| **Container** | **Links To** | **Hidden** |")
    lines.append("| --- | --- | --- |")
    
    # We want rows: NavBar, Footer.
    # We need to aggregate the set `global_links` by Container.
    # Set Items: (Container, TargetPageName, Section, Hidden)
    
    nav_data = {"NavBar": [], "Footer": []}
    
    # Sort global links to ensure deterministic order (TargetName, Section)
    sorted_globals = sorted(list(global_links), key=lambda x: (x[1], x[2]))
    
    for container, target, section, hidden in sorted_globals:
        if container in nav_data:
            nav_data[container].append((target, section, hidden))
            
    for container in ["NavBar", "Footer"]:
        items = nav_data[container]
        if not items:
            continue
            
        # Group by Target Page to make it readable?
        # "Home(#Logo, #Link), About(#Link)"
        # Or just flat list? The user said "lists all the links".
        # Let's group by Target Page to be consistent with the "Page Name(#Section)" format.
        
        target_group = {} # TargetName -> List[(Section, Hidden)]
        
        for target, section, hidden in items:
            if target not in target_group: target_group[target] = []
            if (section, hidden) not in target_group[target]:
                target_group[target].append((section, hidden))
                
        sorted_targets = sorted(target_group.keys())
        
        col2_parts = []
        col3_parts = []
        
        for t in sorted_targets:
            t_items = target_group[t]
            
            sections_str = ", ".join([x[0] for x in t_items])
            col2_parts.append(f"{t} ({sections_str})")
            
            hidden_vals = ["true" if x[1] else "false" for x in t_items]
            hidden_str = "(" + ", ".join(hidden_vals) + ")"
            col3_parts.append(hidden_str)
            
        lines.append(f"| {container} | {', '.join(col2_parts)} | {','.join(col3_parts)} |")

    # Write File
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()