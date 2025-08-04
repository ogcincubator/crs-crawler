import argparse
import sys
import xml.etree.ElementTree as ET
import asyncio
import aiohttp


async def fetch_and_parse_xml(semaphore, session, url, pending_urls, crs_list, seen, do_not_drill_down):
    async with semaphore:
        parent_url = url['parent']
        url = url['url']
        if parent_url is not None and parent_url in do_not_drill_down:
            print(f"Not crawling {url} because {parent_url} children are CRSs", file=sys.stderr)
            crs_list.append(url)
            return
        print(f"Fetching {url}", file=sys.stderr)
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch {url} (status: {resp.status})", file=sys.stderr)
                    return
                content = await resp.read()
                root = ET.fromstring(content)
        except Exception as e:
            print(f"Error fetching/parsing {url}: {e}", file=sys.stderr)
            return

        root_tag = get_local_name(root.tag)
        if root_tag == 'identifiers':
            for child in root:
                if get_local_name(child.tag) == 'identifier' and child.text:
                    next_url = child.text.strip()
                    if next_url not in seen:
                        seen.add(next_url)
                        pending_urls.put_nowait({'url': next_url, 'parent': url})
        else:
            crs_list.append(url)
            if parent_url is not None:
                do_not_drill_down.add(parent_url)



def get_local_name(tag):
    return tag.split('}')[-1] if '}' in tag else tag


async def crawl_urls(start_url, request_queue_size):
    pending_urls: asyncio.Queue[dict] = asyncio.Queue()
    pending_urls.put_nowait({'url': start_url, 'parent': None})
    seen = {start_url}
    crs_list = []
    do_not_drill_down = set()
    semaphore = asyncio.Semaphore(request_queue_size)

    async with aiohttp.ClientSession() as session:
        async def worker():
            while True:
                try:
                    url = await asyncio.wait_for(pending_urls.get(), timeout=3)
                except asyncio.TimeoutError:
                    break
                await fetch_and_parse_xml(semaphore, session, url, pending_urls, crs_list, seen, do_not_drill_down)
                pending_urls.task_done()

        # Start workers
        workers = [asyncio.create_task(worker()) for _ in range(request_queue_size)]
        await asyncio.gather(*workers)

    return crs_list


def main():
    parser = argparse.ArgumentParser(description="Crawl CRS URLs from a starting XML document.")
    parser.add_argument('-p', '--parallel', type=int,
                        help='Number of parallel requests (default 8)', default=8)
    parser.add_argument("start_url", help="The starting URL pointing to an XML document",
                        nargs='?',
                        default='https://www.opengis.net/def/crs/')

    args = parser.parse_args()
    crs_urls = asyncio.run(crawl_urls(args.start_url, request_queue_size=args.parallel))

    print("## Final CRS URLs:")
    for url in crs_urls:
        print(url)


if __name__ == "__main__":
    main()
