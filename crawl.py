from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import sys


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    url_splits = urlsplit(url)
    normalized_url = url_splits.netloc + url_splits.path
    normalized_url = normalized_url.rstrip("/")
    return normalized_url.lower()


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


def extract_page_data(html: str, page_url: str) -> TypedDict:
    soup = BeautifulSoup(html, "html.parser")
    page_data = {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
    return page_data
