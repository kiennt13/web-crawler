import json


def write_json_report(page_data, filename="report.json"):
    list_page_data = sorted(page_data.values(), key=lambda p: p["url"])
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(list_page_data, f, indent=2)
    print("Crreated json file")