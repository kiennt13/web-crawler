import sys
import asyncio
from crawl import *
from json_report import write_json_report

async def main():
    max_concurrency, max_pages = arg_check()
    if len(sys.argv) == 2:
        page_data = await crawl_site_async(sys.argv[1])
    elif len(sys.argv) == 3:
        page_data = await crawl_site_async(sys.argv[1], max_concurrency)
    else:
        page_data = await crawl_site_async(sys.argv[1], max_concurrency, max_pages)
    print(f"Number of pages found: {len(page_data)} pages.")
    write_json_report(page_data)


if __name__ == "__main__":
    asyncio.run(main())