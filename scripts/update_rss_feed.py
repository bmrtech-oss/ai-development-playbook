import json
import xml.etree.ElementTree as ET
from datetime import datetime

def update_rss_feed():
    """Update podcast.xml with the latest episode."""
    try:
        with open('latest_episode.json', 'r') as f:
            episode = json.load(f)
    except FileNotFoundError:
        print("No new episode to add.")
        return

    # Parse existing RSS
    tree = ET.parse('podcast.xml')
    root = tree.getroot()
    channel = root.find('channel')

    # Create new item
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = episode['title']
    ET.SubElement(item, 'description').text = episode['description']

    enclosure = ET.SubElement(item, 'enclosure')
    enclosure.set('url', episode['url'])
    enclosure.set('length', '12345678')  # Placeholder
    enclosure.set('type', 'audio/mpeg')

    ET.SubElement(item, 'guid').text = episode['url']
    ET.SubElement(item, 'pubDate').text = episode['date']
    ET.SubElement(item, 'itunes:duration').text = '00:15:30'  # Placeholder

    # Write back
    tree.write('podcast.xml', encoding='utf-8', xml_declaration=True)

    # Clean up
    os.remove('latest_episode.json')

if __name__ == "__main__":
    update_rss_feed()