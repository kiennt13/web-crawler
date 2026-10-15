from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import sys
import requests


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def arg_check() -> None:
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv}")


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


def crawl_page(base_url: str, current_url: str | None = None, page_data: dict[str, PageData] = None) -> dict[str: PageData]:
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}
    
    if not check_domain(base_url, current_url):
        return page_data
    
    normalized_current_url = normalize_url(current_url)
    if normalized_current_url in page_data:
        return page_data

    print(f"Crawling from {current_url}")
    html = safe_get_html(current_url)
    if html is None:
        return page_data
    
    page_data[normalized_current_url] = extract_page_data(html, current_url)
    
    for url in page_data[normalized_current_url]["outgoing_links"]:
        page_data = crawl_page(base_url, current_url=url, page_data=page_data)
    
    return page_data


def get_html(url) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
        if r.status_code == "4__":
            raise Exception("Error responses: {r.status_code}")
        if "text/html" not in r.headers.get("content-type"):
            raise Exception(f"{r.headers.get('content-type')} not supported")
    except Exception as e:
        raise f"Error: {e}"
    return r.text


def safe_get_html(url: str) -> str | None:
    try:
        return get_html(url)
    except Exception as e:
        print(f"Error: {e}")
        return None