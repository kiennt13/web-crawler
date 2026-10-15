import sys
import requests
from crawl import *


def main():
    arg_check()
    pages_data = crawl_page(sys.argv[1])
    print(f"Number of pages found: {len(pages_data)} pages.")
    for page_data in pages_data.values():
        print(page_data["heading"])


if __name__ == "__main__":
    main()