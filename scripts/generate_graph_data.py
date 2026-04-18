import os
import re
import json

def extract_links_from_markdown(content):
    """Extract markdown links from content."""
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    return [link[1] for link in links if link[1].startswith('docs/')]

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
                rel_path = os.path.relpath(filepath, '.')

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
                if phase_dir in node_map:
                    links.append({
                        'source': node_map[phase_dir],
                        'target': node_idx
                    })

                # Extract and add links
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_links = extract_links_from_markdown(content)
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