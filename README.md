# Sitemap Crawler

sitemapcrawler is a simple, blocking Python Crawler that is the backbone of a few other projects.

You're welcome to use it, but it's only as modular as we've needed it to be, which is to say, probably not fit for projects that aren't built with this in mind.

It works pretty simply.

## Installation

```
pip install sitemapcrawler
```

## Usage

```
from sitemapcrawler.crawler import Crawler
crawler = Crawler(domain="https://yourdomain.com", sitemap="https://yourdomain.com/sitemap.xml", fetch=True)
crawler.run()
```

If you just want to fetch a given page, create an instance of the crawler and call it like this:

```
crawler.fetch_page(url="https://yourdomain.com/blog/title")
```

The `init` will create a nanoid `crawl_id` so that when results are persisted, they'll be associated to a given crawl, to make it easy for reports to be built against crawls and such.

## Building / Distributing

```
python3 -m build
python3 -m twine upload dist/* --skip-existing
