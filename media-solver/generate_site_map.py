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

    with open(args.output, "w") as f:
        f.write("## Page Tree (Content Links)\n")
        f.write("| **Page Name** | **Accessible From (Content)** | **Hidden** |\n| --- | --- | --- |\n")
        for rel, name in sorted(page_map.items(), key=lambda x: x[1]):
            accs = body_access[rel]
            if not accs:
                f.write(f"| {name} | None | (false) |\n")
                continue
            grouped = {}
            for e in accs:
                if e['src'] not in grouped: grouped[e['src']] = []
                if (e['sec'], e['hid']) not in grouped[e['src']]: grouped[e['src']].append((e['sec'], e['hid']))
            c2, c3 = [], []
            for s in sorted(grouped.keys()):
                c2.append(f"{s} ({', '.join([x[0] for x in grouped[s]]}})")
                c3.append("(" + ", ".join(["true" if x[1] else "false" for x in grouped[s]]) + ")")
            f.write(f"| {name} | {', '.join(c2)} | {','.join(c3)} |\n")

        f.write("\n## Global Navigation (NavBar & Footer)\n")
        f.write("| **Container** | **Links To** | **Hidden** |\n| --- | --- | --- |\n")
        nav_data = {"NavBar": set(), "Footer": set()}
        for c, t, s, h in global_links: nav_data[c].add((t, s, h))
        for c in ["NavBar", "Footer"]:
            items = sorted(list(nav_data[c]))
            if not items: continue
            groups = {}
            for t, s, h in items:
                if t not in groups: groups[t] = []
                groups[t].append((s, h))
            c2, c3 = [], []
            for t in sorted(groups.keys()):
                c2.append(f"{t} ({', '.join([x[0] for x in groups[t]]}})")
                c3.append("(" + ", ".join(["true" if x[1] else "false" for x in groups[t]]) + ")")
            f.write(f"| {c} | {', '.join(c2)} | {','.join(c3)} |\n")

    print(f"Generated {args.output}")

if __name__ == "__main__":
    main()
