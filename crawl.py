import argparse
import requests
import xml.etree.ElementTree as ET
from collections import deque

def fetch_and_parse_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except Exception as e:
        print(f"Failed to fetch/parse {url}: {e}")
        return None

def get_local_name(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def crawl_urls(start_url):
    pending_urls = deque([start_url])
    crs_list = []

    while pending_urls:
        current_url = pending_urls.popleft()
        root = fetch_and_parse_xml(current_url)

        if root is None:
            continue

        root_tag = get_local_name(root.tag)

        if root_tag == 'identifiers':
            for child in root:
                if get_local_name(child.tag) == 'identifier' and child.text:
                    pending_urls.append(child.text.strip())
        else:
            crs_list.append(current_url)

    return crs_list

def main():
    parser = argparse.ArgumentParser(description="Crawl CRS URLs from a starting XML document.")
    parser.add_argument("start_url", help="The starting URL pointing to an XML document")

    args = parser.parse_args()
    crs_urls = crawl_urls(args.start_url)

    print("Final CRS URLs:")
    for url in crs_urls:
        print(url)

if __name__ == "__main__":
    main()
