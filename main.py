import json
import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs


def getNewsURL(session, url: str = "https://www.taipeitimes.com/", headers=None,
               num: int = 10000) -> list:
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
    category = ["taiwan", "biz", "editorials", "sport", "world", "feat", "lang"]
    url_list = []
    cum_num = 0
    page = 1

    # Taiwan news
    for i in category:
        while cum_num < num:
            concatenate_url = f"{url}ajax_json/{page}/list/{i}"
            print(f"Parsing {concatenate_url}")
            json_content = session.get(concatenate_url, headers=headers)
            if len(json_content.content) == 0:
                break
            parsed_json = json.loads(json_content.text)
            for j in parsed_json:
                url_list.append(f"{url}{j['ar_url']}")
            cum_num += len(parsed_json)
            page += 1
        page = 1

    url_list.sort(reverse=True)
    print(f"We have {len(url_list)} news.\n")
    return url_list


def main():
    session = requests.session()
    session_id = ""
    saved_news_url_path = "news_url.txt"
    news_path = "news.md"
    rebuild = False

    # Get news' URL
    if os.path.isfile(saved_news_url_path):
        yn = input(f"Warning, the file {saved_news_url_path} exists, do you want to remove it? [y/N] ")
        if yn == 'Y' or yn == 'y':
            os.remove(saved_news_url_path)
            rebuild = True
        else:
            print(f"Reading the URLs in {saved_news_url_path}")
            with open(saved_news_url_path, "r+") as f:
                news = f.read()
            news = news.split('\n')
            if news[-1] == "":
                news = news[:-1]
            news = list(news)
    else:
        rebuild = True

    if rebuild:
        print("Getting news URL.")
        news = getNewsURL(session)
        with open(saved_news_url_path, "w+") as f:
            for i in news:
                f.write(i + "\n")

    print(f"Writing news into {news_path}")
    with open(news_path, "w+") as f:
        for url in tqdm(news):
            # Get news' information
            content = session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
            })
            parsed_content = BeautifulSoup(content.text, "html.parser")
            archive_content = parsed_content.find("div", {"class", "archives"})
            title = archive_content.find("h1").text
            author = archive_content.find("div", {"class", "name"}).text
            author = author.replace("\r\n", " ")
            article = archive_content.find_all("p")
            article = [x.getText() for x in article]
            article = [x.replace("\r", "") for x in article]

            # Write in MarkDown format.
            f.write(f"# {title}\n\n\n")
            f.write(f"*{author}*\n\n\n")
            for i in article:
                f.write(i)
                f.write("\n\n\n")
            f.flush()


if __name__ == "__main__":
    main()
