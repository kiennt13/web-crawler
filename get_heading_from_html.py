from bs4 import BeautifulSoup, Tag


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
