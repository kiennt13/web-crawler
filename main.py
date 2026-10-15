import sys
import requests


def main():
    arg_check()
    print(get_html(sys.argv[1]))


def arg_check() -> None:
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv}")


def get_html(url) -> None:
    try:
        r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
        if r.status_code == "4__":
            raise Exception("Error responses: {r.status_code}")
        if r.headers.get("content-type") != "text/html":
            raise Exception(f"{r.headers.get('content-type')} not supported")
    except Exception as e:
        raise f"Error: {e}"
    return r.text


if __name__ == "__main__":
    main()