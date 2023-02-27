import logging
from urllib.parse import urljoin
import requests
from lxml import etree
import urllib.robotparser
from time import time
from nanoid import generate
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, domain=None, sitemap=None, fetch=False):
        self.rp = urllib.robotparser.RobotFileParser()
        self.visited_urls = []
        self.urls_to_visit = []
        self.results = []
        self.domain = domain
        self.sitemap = sitemap
        self.crawl_delay = 0
        self.crawl_id = generate(size=10)
        self.fetch = fetch

    def guess_robots_url(self, url):
        logging.info("Guessing robots.txt url")
        return urljoin(url, "/robots.txt")

    def guess_sitemap_url(self, url):
        logging.info("Guessing sitemap url")
        return urljoin(url, "/sitemap.xml")

    def evaluate_robots(self, url):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(url, "/robots.txt"))
        rp.read()
        return rp.can_fetch("*", url)

    def fetch_page(self, url):
        logging.info(f"Fetching {url}")
        html = requests.get(url).text
        result = {
            "crawl_id": self.crawl_id,
            "domain": self.domain,
            "url": url,
            "html": html,
        }
        self.results.append(result)
        return result

    def fetch_initial_sitemap(self):
        logging.info(f"Crawling initial domain at {self.domain}")

        if not self.sitemap:
            url = self.guess_sitemap_url(self.domain)
        else:
            url = self.sitemap

        r = requests.get(url)
        root = etree.fromstring(r.content)

        for url in root.xpath("//*[local-name()='loc']/text()"):
            self.add_url_to_visit(url)

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        self.visited_urls.append(url)
        if self.rp.can_fetch("*", url) is False:
            logging.info(f"Skipping {url} due to robots.txt")
            return

        if url.endswith(".xml"):
            logging.info(f"Crawling {url}")
            self.crawl_sitemap(url)
            return
        else:
            logging.info(f"Crawling {url}")
            self.add_url_to_visit(url)
            if self.fetch:
                self.fetch_page(url)
            else:
                self.results.append(url)

    def crawl_sitemap(self, url):
        logging.info(f"Crawling child sitemap at {url}")
        if self.rp.can_fetch("*", url) is False:
            logging.info(f"Skipping {url} due to robots.txt")
            return

        r = requests.get(url)
        root = etree.fromstring(r.content)
        for url in root.xpath("//*[local-name()='loc']/text()"):
            logging.info(f"Adding: {url}")
            self.add_url_to_visit(url)

    def run(self):
        robots_url = self.guess_robots_url(self.domain)
        self.rp.set_url(robots_url)
        self.rp.read()

        rrate = self.rp.request_rate("*")
        if rrate:
            if rrate.seconds:
                self.crawl_delay = rrate.seconds

        if self.domain is not None:
            print("Fetching domain")
            self.fetch_initial_sitemap()

        while self.urls_to_visit:
            url = self.urls_to_visit.pop()
            self.crawl(url)
            if self.crawl_delay:
                time.sleep(self.crawl_delay)

        return self.results

