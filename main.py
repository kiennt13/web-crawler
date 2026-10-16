import sys
import asyncio
from crawl import *


async def main():
    arg_check()
    pages_data = await crawl_site_async(sys.argv[1], 10)
    print(f"Number of pages found: {len(pages_data)} pages.")
    for page_data in pages_data.values():
        print(page_data["heading"])


if __name__ == "__main__":
    asyncio.run(main())