import os
import re
import json

def extract_links_from_markdown(content, file_dir):
    """Extract markdown links from content and convert to absolute docs paths."""
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    absolute_links = []

    for link_text, link_url in links:
        # Skip external links and anchors
        if link_url.startswith('http') or link_url.startswith('#') or link_url.startswith('mailto:'):
            continue

        # Convert relative paths to absolute paths within docs/
        if link_url.startswith('../'):
            # Go up one directory from file_dir
            parent_dir = os.path.dirname(file_dir)
            abs_path = os.path.join(parent_dir, link_url[3:])  # Remove ../
        elif link_url.startswith('./'):
            # Same directory
            abs_path = os.path.join(file_dir, link_url[2:])  # Remove ./
        elif not link_url.startswith('/'):
            # Relative path in same directory
            abs_path = os.path.join(file_dir, link_url)
        else:
            abs_path = link_url

        # Normalize path and ensure it starts with docs/
        abs_path = os.path.normpath(abs_path).replace('\\', '/')
        if abs_path.startswith('docs/'):
            absolute_links.append(abs_path)

    return absolute_links

def build_graph():
    """Build graph data from docs directory."""
    nodes = []
    links = []
    node_map = {}

    # Add phase nodes
    phases = ['00-onboarding', '01-discovery', '02-requirements', '03-design', '04-development', '05-testing', '06-deployment', '07-operations', '08-governance', 'team', 'playbooks']
    for phase in phases:
        node_id = f"docs/{phase}/"
        nodes.append({
            'id': node_id,
            'label': phase.replace('0', '').replace('-', ' ').title(),
            'group': 'phase',
            'size': 10
        })
        node_map[node_id] = len(nodes) - 1

    # Add file nodes and links
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, '.').replace('\\', '/')  # Normalize to forward slashes

                # Add node
                nodes.append({
                    'id': rel_path,
                    'label': file.replace('.md', ''),
                    'group': 'file',
                    'size': 5
                })
                node_idx = len(nodes) - 1
                node_map[rel_path] = node_idx

                # Link to phase
                phase_dir = os.path.dirname(rel_path)
                phase_node_id = f"{phase_dir}/"
                if phase_node_id in node_map:
                    links.append({
                        'source': node_map[phase_node_id],
                        'target': node_idx
                    })

                # Extract and add links
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_links = extract_links_from_markdown(content, os.path.dirname(rel_path))
                for link in file_links:
                    if link in node_map:
                        links.append({
                            'source': node_idx,
                            'target': node_map[link]
                        })

    return {'nodes': nodes, 'links': links}

def main():
    graph_data = build_graph()
    with open('docs/graph.json', 'w') as f:
        json.dump(graph_data, f, indent=2)

if __name__ == "__main__":
    main()