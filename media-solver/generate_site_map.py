import os
import argparse
import csv
import re
from bs4 import BeautifulSoup

def get_page_name(path, root_dir):
    rel_path = os.path.relpath(path, root_dir)
    dir_name = os.path.dirname(rel_path)
    if dir_name == "": return "index.html"
    return dir_name

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

def is_child_or_self(source, target):
    if source == target: return True
    if source.startswith(target + "/"): return True
    return False

def sanitize_id(name):
    # Create a safe ID for Mermaid/DOT
    safe = re.sub(r'[^a-zA-Z0-9]', '_', name)
    if safe[0].isdigit(): safe = '_' + safe
    return safe

def main():
    parser = argparse.ArgumentParser(description="Generate Site Map in MD, CSV, MMD, and DOT formats.")
    parser.add_argument("--root", default="www.conradlegaloffice.com", help="Root directory")
    parser.add_argument("--output-md", default="userflow-links.md", help="Output Markdown file")
    parser.add_argument("--output-csv", default="userflow-links.csv", help="Output CSV file")
    parser.add_argument("--output-mmd", default="userflow-links.mmd", help="Output Mermaid file")
    parser.add_argument("--output-dot", default="userflow-links.dot", help="Output DOT file")
    parser.add_argument("--header-id", default="HeaderZone", help="Header ID")
    parser.add_argument("--footer-id", default="FooterZone", help="Footer ID")
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
    sitemap_page_links = [] 

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
                    if page_name == 'site-map':
                        if not hid: 
                            sitemap_page_links.append((target_name, sec))
                    else:
                        body_access[target_rel].append({'src': page_name, 'sec': sec, 'hid': hid})

    # --- ORPHAN LOGIC (Recursive) ---
    clean_graph_sources = {} 
    valid_links_details = {}

    # Build Graph for Analysis
    for rel, target_name in page_map.items():
        raw_access = body_access.get(rel, [])
        valid_sources = set()
        details_list = []
        
        for entry in raw_access:
            src_name = entry['src']
            if entry['hid']: continue
            if src_name == 'site-map': continue
            if is_child_or_self(src_name, target_name): continue
            
            valid_sources.add(src_name)
            details_list.append(entry)
            
        clean_graph_sources[target_name] = valid_sources
        valid_links_details[target_name] = details_list

    # Detect Orphans
    orphans_status = {}
    
    # 1. Ghost Pages
    for target, sources in clean_graph_sources.items():
        if len(sources) == 0:
            orphans_status[target] = "Ghost Page (0 Links)"
            
    # 2. Recursive Unlinked
    while True:
        found_new_orphan = False
        for target, sources in clean_graph_sources.items():
            if target in orphans_status: continue
            active_sources = [s for s in sources if s not in orphans_status]
            if len(active_sources) == 0:
                orphans_status[target] = "Unlinked Tree (Recursive)"
                found_new_orphan = True
        if not found_new_orphan:
            break
            
    # 3. Isolated Cycles
    forward_graph = {name: set() for name in page_map.values()}
    for target, sources in clean_graph_sources.items():
        for s in sources:
            if s in forward_graph:
                forward_graph[s].add(target)
                
    queue = ['index.html']
    reachable = set(['index.html'])
    
    # Only verify reachability if index.html exists in our map
    if 'index.html' in page_map.values():
        while queue:
            current = queue.pop(0)
            children = forward_graph.get(current, set())
            for child in children:
                if child not in reachable:
                    reachable.add(child)
                    queue.append(child)
        
        for name in page_map.values():
            if name not in reachable and name not in orphans_status:
                orphans_status[name] = "Isolated Cycle / Island"

    # --- DATA PREPARATION FOR TABLES ---
    visible_rows = []
    orphan_rows = []
    
    # Also collect edges for Graphs: Source -> Target
    graph_edges = set() 
    
    for rel, name in sorted(page_map.items(), key=lambda x: x[1]):
        if name in orphans_status:
            status = orphans_status[name]
            orphan_rows.append((name, 0, status))
        else:
            raw_details = valid_links_details.get(name, [])
            active_entries = [e for e in raw_details if e['src'] not in orphans_status]
            count = len(active_entries)
            
            grouped = {}
            for e in active_entries:
                s = e['src']
                if s not in grouped: grouped[s] = []
                if e['sec'] not in grouped[s]: grouped[s].append(e['sec'])
                # Add edge to graph
                graph_edges.add((s, name))
            
            c2 = []
            for s in sorted(grouped.keys()):
                c2.append(f"{s}({', '.join(grouped[s])})")
            
            visible_rows.append((name, count, ", ".join(c2)))

    # Global
    global_rows = []
    nav_data = {"NavBar": set(), "Footer": set()}
    for c, t, s, h in global_links: nav_data[c].add((t, s, h))
    for container in ["NavBar", "Footer"]:
        items = sorted(list(nav_data[c]))
        filtered_items = [x for x in items if not x[2]]
        if not filtered_items: continue
        groups = {}
        for t, s, h in filtered_items:
            if t not in groups: groups[t] = []
            groups[t].append(s)
        c2 = []
        for t in sorted(groups.keys()):
            c2.append(f"{t}({', '.join(groups[t])})")
        global_rows.append((container, len(filtered_items), ", ".join(c2)))

    # Site Map
    sm_groups = {}
    for t, s in sitemap_page_links:
        if t not in sm_groups: sm_groups[t] = []
        if s not in sm_groups[t]: sm_groups[t].append(s)
    sm_rows = []
    for t in sorted(sm_groups.keys()):
        sm_rows.append((t, len(sm_groups[t]), f"{t}({', '.join(sm_groups[t])})"))


    # --- WRITE MARKDOWN ---
    with open(args.output_md, "w") as f:
        f.write("## Page Tree (Visible Content Links)\n")
        f.write("*Pages with 0 valid incoming links (excluding Site Map, self/child references, and recursive orphans) are listed in the 'Orphaned' table below.*\\n\\n")
        f.write("| **#** | **Page Name** | **Count** | **Accessible From (Visible)** |\n| --- | --- | --- | --- |\n")
        for i, (n, c, l) in enumerate(visible_rows, 1):
            f.write(f"| {i} | {n} | {c} | {l} |\n")
        f.write("\n\n")

        f.write("## Global Navigation (Visible Links)\n")
        f.write("| **#** | **Container** | **Count** | **Links To** |\n| --- | --- | --- | --- |\n")
        for i, (n, c, l) in enumerate(global_rows, 1):
            f.write(f"| {i} | {n} | {c} | {l} |\n")
        f.write("\n\n")

        f.write("## Excluded / Orphaned Pages (0 Content Links)\n")
        f.write("* **Ghost Page**: Has 0 incoming content links.\n")
        f.write("* **Unlinked Tree**: Linked only from Ghost Pages or other Unlinked Trees.\n")
        f.write("* **Isolated Cycle**: Pages that link to each other but are disconnected from Home.*\\n\\n")
        f.write("| **#** | **Page Name** | **Count** | **Status** |\n| --- | --- | --- | --- |\n")
        for i, (n, c, l) in enumerate(orphan_rows, 1):
            f.write(f"| {i} | {n} | {c} | {l} |\n")
        f.write("\n\n")

        f.write("## Excluded / Site Map Page Links\n")
        f.write("| **#** | **Target Page** | **Section** |\n| --- | --- | --- |\n")
        for i, (t, c, l) in enumerate(sm_rows, 1):
            try:
                sections_only = l.split('(')[1][:-1]
            except:
                sections_only = l
            f.write(f"| {i} | {t} | {sections_only} |\n")

    print(f"Generated Markdown: {args.output_md}")

    # --- WRITE CSV ---
    csv_rows = []
    for n, c, l in visible_rows:
        csv_rows.append({"Category": "Content Flow", "Name": n, "Count": c, "Details": l})
    for n, c, l in global_rows:
        csv_rows.append({"Category": "Global Navigation", "Name": n, "Count": c, "Details": l})
    for n, c, l in orphan_rows:
        csv_rows.append({"Category": "Orphaned", "Name": n, "Count": c, "Details": l})
    for t, c, l in sm_rows:
        csv_rows.append({"Category": "Site Map Link", "Name": t, "Count": c, "Details": l})

    with open(args.output_csv, "w", newline='') as csvfile:
        fieldnames = ["Category", "Name", "Count", "Details"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(f"Generated CSV: {args.output_csv}")

    # --- WRITE MERMAID ---
    with open(args.output_mmd, "w") as f:
        f.write("graph LR\n")
        # Nodes (Only Visible Content + Orphans usually, typically graphs show valid flow)
        # We will show the Valid Flow graph.
        
        # Define Nodes
        # Use page_map.values() but filtering out things we don't want?
        # Let's include everything in the map for completeness, or just involved nodes.
        nodes = set()
        for s, t in graph_edges:
            nodes.add(s)
            nodes.add(t)
            
        for n in sorted(list(nodes)):
            f.write(f"    {sanitize_id(n)}[{n}]\n")
            
        # Edges
        for s, t in sorted(list(graph_edges)):
            f.write(f"    {sanitize_id(s)} --> {sanitize_id(t)}\n")
            
    print(f"Generated Mermaid: {args.output_mmd}")

    # --- WRITE DOT ---
    with open(args.output_dot, "w") as f:
        f.write("digraph SiteMap {\n")
        f.write("    rankdir=LR;\n")
        f.write("    node [shape=box, style=filled, fillcolor=white];\n")
        
        for n in sorted(list(nodes)):
            f.write(f'    "{n}" [label="{n}"];\n')
            
        for s, t in sorted(list(graph_edges)):
            f.write(f'    "{s}" -> "{t}";\n')
            
        f.write("}\n")
        
    print(f"Generated DOT: {args.output_dot}")

if __name__ == "__main__":
    main()