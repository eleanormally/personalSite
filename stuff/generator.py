# If you found this on my website, hi! This is how I generate the RSS feed from my file system.
# Please feel free to use this if you want, I won't bother with a real license but you may consider it MIT licensed code.

from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
import os
import re

class Parser(HTMLParser):
    tag = None
    title = ""
    description = ""
    category = ""
    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            if attrs[0][0] != "name":
                return
            self.tag = attrs[0][1]
            self.handle_data(attrs[1][1])
        self.tag = tag
    def handle_endtag(self, tag):
        self.tag = None

    def handle_data(self, data):
        if self.tag == "title":
            self.title = data
        elif self.tag == "description":
            self.description = data
        elif self.tag == "keywords":
            self.category = data

def rss_categories(category_string):
    return "\n    ".join([f'<category>{f}</category>' for f in category_string.split(", ")])

def rss_processed_page_contents(page_string):
    main_contents = next(re.finditer('<main>\n([\s\S]*)</main>', page_string)).group(1)
    return main_contents

def rss_contents(file):
    with open(file, "r") as file_contents:
        contents = file_contents.read()
        parser = Parser()
        parser.feed(contents)
        utc_dt = datetime.utcfromtimestamp(os.stat(file).st_birthtime).replace(tzinfo=timezone.utc)
        published_date = format_datetime(utc_dt, usegmt=True)
        return f"""  <item>
    <title>{parser.title}</title>
    <description><![CDATA[{rss_processed_page_contents(contents)}]]></description>
    {rss_categories(parser.category)}
    <link>https://eleanorkolson.com/stuff/{file}</link>
    <guid>https://eleanorkolson.com/stuff/{file}</guid>
    <pubDate>{published_date}</pubDate>
  </item>
"""

def html_contents(file):
    with open(file, "r") as file_contents:
        parser = Parser()
        parser.feed(file_contents.read())
        utc_dt = datetime.utcfromtimestamp(os.stat(file).st_birthtime)
        published_date = utc_dt.strftime("%Y-%m-%d")
        return f"""    <li>
      <a href="{file}">{parser.title}</a>: {parser.description} ({parser.category}) ({published_date})
    </li>"""

def should_include(file):
    excludedFiles = [
        "index.html",
        "generator.py",
        "feed.xml",
        "feed",
    ]
    return file not in excludedFiles and "_draft" not in file

def generate_rss_items():
    files = os.listdir(os.getcwd())
    files.sort(key=lambda x: -1 * os.stat(x).st_birthtime)
    files = [rss_contents(f) for f in files if should_include(f)]
    return "".join(files)

def generate_html_items():
    files = os.listdir(os.getcwd())
    files.sort(key=lambda x: -1 * os.stat(x).st_birthtime)
    files = [html_contents(f) for f in files if should_include(f)]
    return "".join(files)


def generate_rss_feed():
    published_date = format_datetime(datetime.now(timezone.utc), usegmt=True)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
  <atom:link href="http://eleanorkolson.com/feed" rel="self" type="application/rss+xml" />
  <title>Eleanor Olson</title>
  <link>https://eleanorkolson.com</link>
  <image>
    <url>https://eleanorkolson.com/public/icon.png</url>
    <title>Eleanor Olson</title>
    <link>https://eleanorkolson.com</link>
  </image>
  <pubDate>{published_date}</pubDate>
  <language>en-us</language>
  <copyright>© {datetime.now().year} Eleanor Olson</copyright>
  <description>
    Eleanor's personal blog about various things. Probably mostly transit.
  </description>
{generate_rss_items()}  </channel>
</rss>"""

def generate_html_blog():
    return f"""<!DOCTYPE html>
<head>
  <title>Eleanor Olson's Stuff!</title>
  <meta name="color-scheme" content="light dark">
  <link rel="icon" href="/public/favicon.ico">
  <style>
  body {{
    margin: auto;
    max-width:800px;
  }}

  html {{
    padding: 1rem;
  }}
  </style>
</head>
<body>
  <h1>My Stuff! (and my Thoughts)</h1>
  <p>I like working on Stuff and writing about my Thoughts. Here's some Stuff I've worked on and some Thoughts that I've had.<br>
  If you'd like to follow my Thoughts and/or my Stuff, you may do so through the wonders of <a href="/feed">RSS</a>. This page contains the contents of that feed in a more browser-friendly form.</p>
  <ul>
{generate_html_items()}
  </ul>
</body>
<footer>
  <a href="/">Back home!</a>
</footer>
</html>"""

if __name__ == "__main__":
    feed = generate_rss_feed()
    with open("../feed", "w") as file:
        file.write(feed)

    blog = generate_html_blog()
    with open("index.html", "w") as file:
        file.write(blog)
    
