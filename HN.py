from summa.summarizer import summarize
from urllib.parse import urlparse
from termcolor import colored
from newspaper import Article
from bs4 import BeautifulSoup
from threading import Thread
from keybert import KeyBERT
from itertools import chain
import progressbar
import keyboard
import requests
import os


# Initialize
news_content = ['Hi, welcom to HN']
kw = KeyBERT() # keywords


def extract_news_url_from_a_page(content):
    """Extraction of all news URLs on a page"""

    # URLs that are repeated on all pages and are not news
    deleted_urls = ['https://news.ycombinator.com', 'https://github.com/HackerNews/API', 'https://www.ycombinator.com/legal/', 'https://www.ycombinator.com/apply/']

    def validator(x):
        """Validate the URL"""
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    # Extract URLs
    soup = BeautifulSoup(content, 'html.parser')
    urls = list([url['href'] for url in soup.find_all('a', href=True) if validator(url['href'])])

    # Remove deleted urls
    for d_url in deleted_urls:
        urls.remove(d_url)
    
    return urls

def extract_all_urls():
    """Performing the URL extraction process from all pages"""

    print('Start extract URLs ...')

    links = []
    number = 1

    # Progressbar
    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    while True:

        content = requests.get(f"https://news.ycombinator.com/?p={number}")
        urls = extract_news_url_from_a_page(content.text)

        bar.update(number - 1)

        if len(urls) == 0:
            break

        links.append(urls)
        number += 1


    links = list(chain.from_iterable(links))

    return links

def fetch_news_content_from_a_url(url):
    """Extracting textual content from news URLs"""

    try :
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except :
        return ''
    
def text_summary(content , ratio=0.4):
    """Summarize news text
    default: 0.4 -> The condensed text contains 40% of the original text"""
    summary = summarize(content , ratio=ratio, split=True)
    return ' '.join(summary)

def show(data, num_news=0):
    """Displaying the extracted news along with switching between the news with the up and down keys on the keyboard"""

    lenght = len(data) - 1

    while True:

        os.system('cls')
        print(data[num_news])

        try:
            press = keyboard.read_hotkey(suppress=False)

        except KeyboardInterrupt:
            print('Good Luck')
            return
               
        if press == 'up':
            num_news += 1

        if press == 'down':
            num_news -= 1
            
        if num_news > lenght:
            num_news = 0
            
        if num_news < 0:
            num_news = lenght

        if press == 'q':
            print('Good Luck')
            return

def NewsHN(summarize=False):
    """Implementing the process of extracting and displaying news from Hacker News"""

    os.system("")

    news_urls = extract_all_urls()
    

    def news():
        global news_content

        number_news = 1

        for url in news_urls:

            if 'youtube' not in url:

                if summarize:
                    content = text_summary(fetch_news_content_from_a_url(url))
                else:
                    content = fetch_news_content_from_a_url(url)

                if content:
                    
                    keyword = kw.extract_keywords(content)

                    for kwrd in keyword:
                        content = content.replace(kwrd[0], colored(kwrd[0], 'yellow'))

                    news_content.append(f"News {number_news}: URL -> {url}\n{content}")
                    number_news += 1
    
    extract = Thread(target=news)
    shows = Thread(target=show, args=(news_content, len(news_content)))

    extract.start()
    shows.start()


# Main
if __name__ == '__main__':

    try:
        NewsHN()
    except:
        print('A problem has occurred')
        if len(news_content) > 1:
            show(news_content)