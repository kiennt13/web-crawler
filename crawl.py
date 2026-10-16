from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import sys
import requests
import asyncio
import aiohttp


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


class AsyncCrawler():
    def __init__(
        self,
        base_url: str,
        max_concurrency: int = 3,
        max_pages: int = 10
    ) -> None:
        self.base_url = base_url
        self.base_domain: str = urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        self.max_pages: int = max_pages
        self.should_stop: bool = False
        self.all_tasks: set = set()


    async def __aenter__(self) -> object:
        self.session = aiohttp.ClientSession()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> object:
        await self.session.close()


    async def add_page_visit(self, normalized_url: str):
        async with self.lock:
            if normalized_url in self.visited:
                return False
            if self.should_stop is True:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl")
                return False
            self.visited.add(normalized_url)
            return True


    async def get_html(self, url: str) -> str:
        try:
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as r:
                if r.status > 399:
                    raise Exception(f"Error responses: {r.status}")
                if "text/html" not in r.headers.get("content-type"):
                    raise Exception(f"{r.headers.get('content-type')} not supported")
                return await r.text()
        except Exception as e:
            raise Exception(f"Error: {e}")


    async def safe_get_html(self, url: str) -> str | None:
        try:
            return await self.get_html(url)
        except Exception as e:
            print(f"Error: {e}")
            return None


    async def crawl_page(self, current_url: str | None = None) -> None:
        if self.should_stop is True:
            return
        
        normalized_current_url = normalize_url(current_url)
        if urlsplit(current_url).netloc != self.base_domain:
            return
        
        check_vist = await self.add_page_visit(normalized_current_url)
        if not check_vist:
            return

        async with self.semaphore:
            html = await self.safe_get_html(current_url)
        if html is None:
            return
        print(f"Crawling from {current_url}")
        extract_result = extract_page_data(html, current_url)
                
        async with self.lock:
            self.page_data[normalized_current_url] = extract_result

        if self.should_stop is True:
            return
        
        tasks = []
        for url in self.page_data[normalized_current_url]["outgoing_links"]: 
            task = asyncio.create_task(self.crawl_page(url))
            tasks.append(task)
            self.all_tasks.add(task)
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)
        return


    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(url: str, max_concurrency: int = 3, max_pages: int = 10) -> dict[str, PageData]:
    async with AsyncCrawler(url, max_concurrency, max_pages) as crawler:
        await crawler.crawl()
        return crawler.page_data


def arg_check() -> None:
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    else:
        try:
            max_concurrency = int(sys.argv[2])
            max_pages = int(sys.argv[3])
        except ValueError:
            print("invalid max concurrency or max pages value")
            sys.exit(1)
        print(f"starting crawl of: {sys.argv}")
        return max_concurrency, max_pages


def normalize_url(url: str) -> str:
    url_splits = urlsplit(url)
    normalized_url = url_splits.netloc + url_splits.path
    normalized_url = normalized_url.rstrip("/")
    return normalized_url.lower()


def check_domain(base_url: str, current_url: str) -> bool:
    base_url_splits = urlsplit(base_url)
    current_url_splits = urlsplit(current_url)
    if base_url_splits.hostname == current_url_splits.hostname:
        return True
    return False


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find(["h1", "h2"])
    if isinstance(h_tag, Tag):
        return h_tag.get_text(strip=True)
    return ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    target_p = None
    main = soup.find("main")
    if isinstance(main, Tag):
        target_p = main.find("p")
    else:
        target_p = soup.find("p")
    if isinstance(target_p, Tag):
        return target_p.get_text(strip=True)
    return ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links_tag = soup.find_all("a")
    links = []
    for link_tag in links_tag:
        if not isinstance(link_tag, Tag):
            continue
        href = link_tag.get("href")
        if isinstance(href, str) and href:
            try:
                links.append(urljoin(base_url, href))
            except Exception as e:
                print(f"{str(e)}: {href}")
    return links


def get_images_from_html(html: str, base_url: str) -> list[str]:
    image_urls = []
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")

    for img in images:
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if isinstance(src, str) and src:
            try:
                absolute_url = urljoin(base_url, src)
                image_urls.append(absolute_url)
            except Exception as e:
                print(f"{str(e)}: {src}")

    return image_urls


def extract_page_data(html: str, page_url: str) -> PageData:
    soup = BeautifulSoup(html, "html.parser")
    page_data = {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
    return page_data