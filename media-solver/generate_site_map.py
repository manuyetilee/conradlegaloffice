import os
import argparse
from bs4 import BeautifulSoup

def get_page_name(path, root_dir):
    rel_path = os.path.relpath(path, root_dir)
    if rel_path == "index.html":
        return "Home"
    parts = os.path.dirname(rel_path).split(os.sep)
    name = " / ".join([p.replace('-', ' ').title() for p in parts])
    return name if name else "Home"

def resolve_path(source_file_path, href, root_dir):
    if not href or href.startswith(('http', 'https', 'mailto:', 'tel:', 'javascript:', '#')):
        return None
    href = href.split('?')[0].split('#')[0]
    if not href: return None
    source_dir = os.path.dirname(source_file_path)
    abs_path = os.path.abspath(os.path.join(source_dir, href))
    root_abs = os.path.abspath(root_dir)
    if not abs_path.startswith(root_abs): return None 
    rel_path = os.path.relpath(abs_path, root_abs)
    if os.path.isdir(os.path.join(root_dir, rel_path)):
        rel_path = os.path.join(rel_path, "index.html")
    elif not rel_path.endswith('.html'):
         if os.path.exists(os.path.join(root_dir, rel_path, 'index.html')):
             rel_path = os.path.join(rel_path, 'index.html')
    if rel_path.endswith('.html') and os.path.exists(os.path.join(root_dir, rel_path)):
        return rel_path
    return None

def is_hidden(element):
    cursor = element
    while cursor and cursor.name != '[document]':
        if cursor.has_attr('style') and 'display:none' in cursor['style'].lower().replace(' ', ''):
            return True
        if cursor.has_attr('hidden'): return True
        cursor = cursor.parent
    return False

def get_section_id(element):
    cursor = element
    while cursor and cursor.name != '[document]':
        if cursor.has_attr('id'): return f"#{cursor['id']}"
        cursor = cursor.parent
    return "No ID"

def main():
    parser = argparse.ArgumentParser(description="Generate a Notion-compatible Site Map and User Flow table.")
    parser.add_argument("--root", default="www.conradlegaloffice.com", help="Root directory of the website")
    parser.add_argument("--output", default="userflow-links.md", help="Output Markdown file")
    parser.add_argument("--header-id", default="HeaderZone", help="ID of the header/nav container")
    parser.add_argument("--footer-id", default="FooterZone", help="ID of the footer container")
    args = parser.parse_args()

    page_map = {}
    all_files = []
    for root, _, files in os.walk(args.root):
        for file in files:
            if file == "index.html":
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, args.root)
                page_map[rel_path] = get_page_name(full_path, args.root)
                all_files.append(full_path)

    body_access = {p: [] for p in page_map}
    global_links = set()

    for file_path in all_files:
        page_name = get_page_name(file_path, args.root)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        header = soup.find(id=args.header_id)
        footer = soup.find(id=args.footer_id)

        for a in soup.find_all('a', href=True):
            target_rel = resolve_path(file_path, a['href'], args.root)
            if target_rel in page_map:
                target_name = page_map[target_rel]
                sec, hid = get_section_id(a), is_hidden(a)
                if header and (a in header.descendants):
                    global_links.add(("NavBar", target_name, sec, hid))
                elif footer and (a in footer.descendants):
                    global_links.add(("Footer", target_name, sec, hid))
                else:
                    body_access[target_rel].append({'src': page_name, 'sec': sec, 'hid': hid})

    # --- HELPER TO GENERATE ROWS ---
    def generate_rows(data_map, is_global=False, show_hidden=False):
        # 1. Collect Data
        collected_data = [] # List of tuples: (name, count, link_column_string)

        if is_global:
            # data_map is {"NavBar": set(), "Footer": set()}
            for container in ["NavBar", "Footer"]:
                items = sorted(list(data_map.get(container, [])))
                filtered_items = [x for x in items if x[2] == show_hidden]
                
                count = len(filtered_items)
                if count == 0:
                    continue # Skip empty global containers in listing? Or show 0?
                             # Usually we just skip if empty for global nav tables.

                groups = {} 
                for t, s, h in filtered_items:
                    if t not in groups: groups[t] = []
                    groups[t].append(s)
                
                c2 = []
                for t in sorted(groups.keys()):
                    c2.append(f"{t} ({', '.join(groups[t])})")
                
                link_str = ", ".join(c2)
                collected_data.append((container, count, link_str))
        else:
            # data_map is {target_rel: [entries]}
            for rel, name in sorted(page_map.items(), key=lambda x: x[1]):
                accs = data_map.get(rel, [])
                filtered_accs = [e for e in accs if e['hid'] == show_hidden]
                count = len(filtered_accs)
                
                if count == 0:
                    if not show_hidden:
                         # For visible table, include 0s
                         collected_data.append((name, 0, "None"))
                    # For hidden table, skip 0s
                    continue
                
                grouped = {}
                for e in filtered_accs:
                    if e['src'] not in grouped: grouped[e['src']] = []
                    if e['sec'] not in grouped[e['src']]: grouped[e['src']].append(e['sec'])
                
                c2 = []
                for s in sorted(grouped.keys()):
                    c2.append(f"{s} ({', '.join(grouped[s])})")
                
                link_str = ", ".join(c2)
                collected_data.append((name, count, link_str))
        
        # 2. Sort Data
        # Rule: 0s at the bottom. Non-0s alphabetical.
        non_zeros = sorted([x for x in collected_data if x[1] > 0], key=lambda x: x[0])
        zeros = sorted([x for x in collected_data if x[1] == 0], key=lambda x: x[0])
        final_list = non_zeros + zeros
        
        # 3. Format Output
        output_rows = []
        for i, (name, cnt, links) in enumerate(final_list, 1):
            output_rows.append(f"| {i} | {name} | {cnt} | {links} |")
            
        return output_rows

    # --- WRITE OUTPUT ---
    with open(args.output, "w") as f:
        # Table 1: Visible Content
        f.write("## Page Tree (Visible Content Links)\n")
        f.write("| **#** | **Page Name** | **Count** | **Accessible From (Visible)** |\n| --- | --- | --- | --- |\n")
        f.write("\n".join(generate_rows(body_access, is_global=False, show_hidden=False)))
        f.write("\n\n")

        # Table 2: Visible Global
        f.write("## Global Navigation (Visible Links)\n")
        f.write("| **#** | **Container** | **Count** | **Links To** |\n| --- | --- | --- | --- |\n")
        
        # Prepare global data dict
        nav_data = {"NavBar": set(), "Footer": set()}
        for c, t, s, h in global_links: nav_data[c].add((t, s, h))
        
        f.write("\n".join(generate_rows(nav_data, is_global=True, show_hidden=False)))
        f.write("\n\n")

        # Table 3: Hidden Content
        f.write("## Hidden Content Links\n")
        f.write("| **#** | **Page Name** | **Count** | **Hidden Access From** |\n| --- | --- | --- | --- |\n")
        f.write("\n".join(generate_rows(body_access, is_global=False, show_hidden=True)))
        f.write("\n\n")

        # Table 4: Hidden Global
        f.write("## Hidden Global Navigation Links\n")
        f.write("| **#** | **Container** | **Count** | **Hidden Links To** |\n| --- | --- | --- | --- |\n")
        f.write("\n".join(generate_rows(nav_data, is_global=True, show_hidden=True)))

    print(f"Generated {args.output}")

if __name__ == "__main__":
    main()