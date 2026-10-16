import sys
import asyncio
from crawl import *


async def main():
    max_concurrency, max_pages = arg_check()
    if len(sys.argv) == 2:
        pages_data = await crawl_site_async(sys.argv[1])
    elif len(sys.argv) == 3:
        pages_data = await crawl_site_async(sys.argv[1], max_concurrency)
    else:
        pages_data = await crawl_site_async(sys.argv[1], max_concurrency, max_pages)
    print(f"Number of pages found: {len(pages_data)} pages.")
    for page_data in pages_data.values():
        print(page_data["heading"])


if __name__ == "__main__":
    asyncio.run(main())